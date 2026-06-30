"""
创建 HPI 新设计所需的数据表：hpi_daily 和 hpi_components
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL


def upgrade():
    """创建 hpi_daily 和 hpi_components 表"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        # 创建 hpi_daily 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hpi_daily (
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
                record_date     DATE NOT NULL,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_user_date (user_id, record_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='HPI每日快照表'
        """))
        print("✅ hpi_daily 表创建成功")

        # 创建 hpi_components 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hpi_components (
                id              INT PRIMARY KEY AUTO_INCREMENT,
                user_id         INT NOT NULL,
                figure_id       INT NOT NULL,
                record_date     DATE NOT NULL,
                first_buy_price FLOAT NOT NULL COMMENT '首次买入价',
                first_buy_date  DATE NOT NULL COMMENT '首次买入日期',
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
        print("✅ hpi_components 表创建成功")

    print("🎉 HPI 表迁移完成")


if __name__ == "__main__":
    upgrade()
