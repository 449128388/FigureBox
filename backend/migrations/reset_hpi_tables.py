"""
重置 HPI 表结构并重新跑批

1. DROP 重建 hpi_daily 和 hpi_components 表（使其与模型定义完全一致）
2. 执行全量 HPI 跑批
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.models.database import engine, SessionLocal
from app.models.hpi import HPIDaily, HPIComponent
from app.models.user import User
from app.services.dashboard_service.market_service.hpi_service import HPIService
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def reset_tables():
    """DROP 并重建 hpi_daily 和 hpi_components 表"""
    logger.info("=" * 50)
    logger.info("开始重置 HPI 表结构...")
    logger.info("=" * 50)

    with engine.connect() as conn:
        # 禁用外键检查（如果有外键依赖）
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        # DROP 表（先删从表，再删主表）
        logger.info("→ 删除 hpi_components 表...")
        conn.execute(text("DROP TABLE IF EXISTS hpi_components"))
        logger.info("→ 删除 hpi_daily 表...")
        conn.execute(text("DROP TABLE IF EXISTS hpi_daily"))

        # 重建 hpi_daily 表（包含所有字段，与 HPIComponent 模型一致）
        logger.info("→ 创建 hpi_daily 表...")
        conn.execute(text("""
            CREATE TABLE hpi_daily (
                id              INT PRIMARY KEY AUTO_INCREMENT,
                user_id         INT NOT NULL,
                index_value     FLOAT NOT NULL COMMENT 'HPI指数值',
                avg_return      FLOAT NOT NULL COMMENT '平均超额收益率%',
                total_figures   INT NOT NULL COMMENT '生涯累计交易手办数',
                holding_figures INT NOT NULL COMMENT '当前在柜数',
                sold_figures    INT NOT NULL COMMENT '已出但跟踪数',
                up_count        INT DEFAULT 0 COMMENT '买入后上涨的手办数',
                flat_count      INT DEFAULT 0 COMMENT '持平',
                down_count      INT DEFAULT 0 COMMENT '买入后下跌的手办数',
                sold_up_count   INT DEFAULT 0 COMMENT '卖出后上涨（卖飞）',
                sold_down_count INT DEFAULT 0 COMMENT '卖出后下跌（卖对）',
                in_cabinet_value FLOAT DEFAULT 0 COMMENT '在柜手办加权市值贡献(走势图绿色实线)',
                sold_value      FLOAT DEFAULT 0 COMMENT '已出手办加权市值贡献(走势图灰色虚线)',
                record_date     DATE NOT NULL,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                UNIQUE KEY uk_user_date (user_id, record_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='HPI每日快照表'
        """))

        # 重建 hpi_components 表（与模型一致）
        logger.info("→ 创建 hpi_components 表...")
        conn.execute(text("""
            CREATE TABLE hpi_components (
                id              INT PRIMARY KEY AUTO_INCREMENT,
                user_id         INT NOT NULL,
                figure_id       INT NOT NULL,
                record_date     DATE NOT NULL,
                first_buy_price FLOAT NOT NULL COMMENT '首次买入价',
                first_buy_date  DATE NOT NULL COMMENT '首次买入日期',
                quantity        INT DEFAULT 1 COMMENT '累计买入数量（订单笔数）',
                total_buy_amount FLOAT NOT NULL COMMENT '累计买入金额',
                current_price   FLOAT NOT NULL COMMENT '当日市场价',
                is_sold         TINYINT DEFAULT 0 COMMENT '是否已出',
                sell_price      FLOAT NULL COMMENT '卖出价（已出时）',
                return_pct      FLOAT NOT NULL COMMENT '相对首次买入的收益率%',
                weight          FLOAT NOT NULL COMMENT '权重',
                contribution    FLOAT NOT NULL COMMENT '对HPI的贡献度',
                sell_fly        TINYINT DEFAULT 0 COMMENT '1=卖出后上涨(卖飞)',
                sell_right      TINYINT DEFAULT 0 COMMENT '1=卖出后下跌(卖对)',
                KEY idx_user_figure_date (user_id, figure_id, record_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='HPI成分明细表'
        """))

        # 恢复外键检查
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()

    logger.info("✅ HPI 表结构重置完成！")


def run_batch():
    """执行全量 HPI 跑批"""
    logger.info("=" * 50)
    logger.info("开始全量 HPI 跑批...")
    logger.info("=" * 50)

    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        success_count = 0
        for user in users:
            try:
                if HPIService.run_daily_batch(db, user.id):
                    success_count += 1
                    logger.info(f"  ✅ user_id={user.id} 跑批成功")
                else:
                    logger.warning(f"  ⚠️ user_id={user.id} 无数据可计算（无交易记录）")
            except Exception as e:
                logger.error(f"  ❌ user_id={user.id} 跑批失败: {e}")

        logger.info(f"🏁 全量跑批完成：共 {len(users)} 人，成功 {success_count} 人")
    except Exception as e:
        logger.error(f"跑批任务异常: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    reset_tables()
    run_batch()
