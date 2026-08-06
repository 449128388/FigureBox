"""
为所有数据库表补充或修正中文注释

说明：
- 遍历所有已知表，使用 ALTER TABLE ... COMMENT 添加备注
- 跳过已存在备注的表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import Base, DATABASE_URL as SQLALCHEMY_DATABASE_URL

# 所有表的注释映射
TABLE_COMMENTS = {
    "users_info": "用户信息表 - 存储用户基本信息、认证信息及配置（含年度消费上限）",
    "users": "用户表 - 存储系统用户的基本信息和认证信息【已重命名为 users_info】",
    "figures": "手办表 - 存储手办的基本信息、市场价、成本价等核心数据",
    "orders": "订单表 - 存储手办预定/购买的订单信息（定金、尾款、状态等）",
    "sold_orders": "卖出订单表 - 存储手办卖出/转卖的记录",
    "asset_transactions": "资产交易记录表 - 记录手办的买卖交易（股票式补仓、买入卖出流水）",
    "asset_price_history": "资产价格历史表 - 记录手办价格变化历史，用于价格趋势图表",
    "asset_value_cache": "资产市值缓存表 - 缓存用户每日资产总市值，用于日涨跌计算",
    "stock_index_cache": "指数缓存表 - 缓存最新上证指数/沪深300指数数据",
    "stock_index_history": "指数历史记录表 - 保存每次请求的指数详细数据，用于趋势分析",
    "order_transactions": "订单交易流水表 - 记录订单的支付流水明细（定金、尾款、费用等）",
    "plastic_index_history": "塑料手办指数(HPI)历史表 - 记录每日 HPI 指数值",
    "holding_snapshots": "持仓快照表 - 每日收盘时各手办的持仓数据快照",
    "holding_snapshot_summaries": "持仓快照汇总表 - 每日收盘时用户持仓汇总数据",
    "user_asset_snapshots": "用户资产每日快照表 - 每日记录用户资产状况用于日涨跌对比",
    "tags": "标签表 - 手办标签字典（作品、角色、属性等分类），供前端标签下拉候选使用",
    "activity_feed": "动态流表 - 收藏家模式的动态事件记录（入手、到库、售出等）",
    "collector_privacy": "收藏家隐私设置表 - 收藏家模式下的个人主页可见性等隐私配置",
    "favorite_manufacturers": "本命厂商表 - 用户关注/收藏的手办厂商列表",
    "cabinet_ratings": "收藏柜喜爱度评分表 - 用户在收藏柜中对手办的 1-5 星评分",
    "cabinet_figure_exclusions": "展示分类手动排除表 - 用户从展示分类中手动移出的手办记录",
    "user_settings": "用户设置表 - 存储用户的个性化配置（年度消费上限等设置）【已废弃，合并到 users_info】",
    "exchange_rate_realtime": "最新汇率缓存表 - 缓存从中国外汇交易中心获取的当前最新汇率",
    "exchange_rate_history": "汇率历史记录表 - 记录每次从中国外汇交易中心获取的汇率快照",
    "hpi_daily": "HPI每日快照表 - 投资生涯全周期收益指数每日快照",
    "hpi_components": "HPI成分明细表 - 记录每手办对指数的贡献",
    "hpoi_scrape_cache": "HPOI 抓取缓存表 - 存储 HPOI 页面抓取结果与解析数据（30 天 TTL）",
    "backup_records": "备份历史记录表 - 记录每次备份的元数据指针",
}

# 需要补充列注释的表（id 主键列无注释）
COLUMN_COMMENTS = {
    "hpoi_scrape_cache": {
        "id": "缓存记录唯一标识ID",
    },
    # orders 表的支付方式/时间字段注释同步（原由 add_order_balance_payment_fields.py 承担 MODIFY COLUMN 增量更新，现归口到本脚本）
    "orders": {
        "payment_method": "定金支付方式：支付宝、微信、银行卡转账、现金",
        "payment_time": "定金支付时间",
    },
    # users_info 表自动备份配置 4 字段注释同步（原由 add_auto_backup_fields.py 承担，现归口到本脚本）
    "users_info": {
        "auto_backup_enabled": "是否开启自动备份",
        "auto_backup_frequency": "自动备份频率：daily / weekly / monthly",
        "auto_backup_retain": "保留份数：0=不限制，≥1 保留最近 N 份",
        "last_auto_backup_at": "上次自动备份成功时间（用于调度到期判断）",
        # 邮箱设置（SMTP 发件配置）8 字段（用于密码重置/尾款提醒/资产周报等系统通知）
        "smtp_host": "SMTP 服务器地址，如 smtp.163.com",
        "smtp_port": "SMTP 端口：SSL 通常 465，STARTTLS 通常 587，无加密 25",
        "smtp_from_email": "发件人邮箱地址（系统发件时显示的 From 地址）",
        "smtp_from_name": "发件人昵称（邮件中显示的发件人名称）",
        "smtp_password": "SMTP 授权码 / 密码（建议使用邮箱服务商提供的授权码）",
        "smtp_secure_mode": "安全连接：ssl / starttls / none",
        "smtp_last_test_at": "SMTP 连接测试成功时间",
        "smtp_last_test_status": "SMTP 连接测试状态：success / failed（便于面板展示连接状态）",
    },
    # 2026-08-05 新增：figures.user_id 字段（数据隔离）
    "figures": {
        "user_id": "所属用户ID（数据隔离用，NULL 表示全局共享/历史数据）",
    },
}

# 增量补列：Base.metadata.create_all() 只建新表，不会给已存在表加新列
# 字段定义与 [models/user.py] Column 完全一致；存在则跳过，缺失则 ADD COLUMN
COLUMN_DEFINITIONS = {
    "users_info": {
        "smtp_host": "VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'SMTP 服务器地址，如 smtp.163.com'",
        "smtp_port": "INT NOT NULL DEFAULT 465 COMMENT 'SMTP 端口：SSL 通常 465，STARTTLS 通常 587，无加密 25'",
        "smtp_from_email": "VARCHAR(255) NOT NULL DEFAULT '' COMMENT '发件人邮箱地址（系统发件时显示的 From 地址）'",
        "smtp_from_name": "VARCHAR(100) NOT NULL DEFAULT 'FigureBox 系统通知' COMMENT '发件人昵称（邮件中显示的发件人名称）'",
        "smtp_password": "VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'SMTP 授权码 / 密码（建议使用邮箱服务商提供的授权码）'",
        "smtp_secure_mode": "VARCHAR(16) NOT NULL DEFAULT 'ssl' COMMENT '安全连接：ssl / starttls / none'",
        "smtp_last_test_at": "DATETIME NULL COMMENT 'SMTP 连接测试成功时间'",
        "smtp_last_test_status": "VARCHAR(20) NOT NULL DEFAULT '' COMMENT 'SMTP 连接测试状态：success / failed（便于面板展示连接状态）'",
    },
    # 2026-08-05 新增：figures.user_id 字段（数据隔离：每条手办只属于创建它的用户）
    "figures": {
        "user_id": "INT NULL COMMENT '所属用户ID（数据隔离用，NULL 表示全局共享/历史数据）'",
    },
}

# 增量补索引：Base.metadata.create_all() 不会给已存在表加新索引，需主动 CREATE INDEX
# 索引名规则：ix_<表名>_<列名>
INDEX_DEFINITIONS = {
    # 2026-08-05 新增：figures.user_id 索引（数据隔离查询性能优化）
    "figures": {
        "ix_figures_user_id": ["user_id"],
    },
}


def upgrade():
    """为所有表添加注释 + 增量补列（Base.metadata.create_all 不会给已存在表加新列）"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # 先确保所有表已创建（ORM 模型自动建表）
    Base.metadata.create_all(bind=engine)
    print("✅ 所有 ORM 表已创建")

    with engine.connect() as conn:
        # 获取数据库中已有的所有表
        result = conn.execute(text(
            "SELECT table_name, table_comment FROM information_schema.tables "
            "WHERE table_schema = DATABASE()"
        ))
        existing_tables = {}
        for row in result:
            existing_tables[row[0]] = row[1] or ""

        # 增量补列：Base.metadata.create_all() 不会给已存在表加新列，需主动 ADD COLUMN
        # 存在性判断：information_schema.columns 查列名，缺失则 ADD
        add_col_count = 0
        for table_name, columns in COLUMN_DEFINITIONS.items():
            if table_name not in existing_tables:
                print(f"  ⚠️ {table_name}: 表不存在，跳过增量补列")
                continue
            for col_name, col_ddl in columns.items():
                exists = conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.columns "
                    "WHERE table_schema = DATABASE() AND table_name = :t AND column_name = :c"
                ), {"t": table_name, "c": col_name}).scalar()
                if exists:
                    print(f"  - {table_name}.{col_name}: 列已存在，跳过")
                    continue
                conn.execute(text(f"ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {col_ddl}"))
                conn.commit()
                print(f"  ✅ {table_name}.{col_name}: 新列已添加")
                add_col_count += 1

        # 增量补索引：Base.metadata.create_all() 不会给已存在表加新索引，需主动 CREATE INDEX
        # 存在性判断：information_schema.statistics 查索引名
        add_idx_count = 0
        for table_name, indexes in INDEX_DEFINITIONS.items():
            if table_name not in existing_tables:
                print(f"  ⚠️ {table_name}: 表不存在，跳过增量补索引")
                continue
            for idx_name, idx_cols in indexes.items():
                # 索引存在性：information_schema.statistics 查 index_name
                idx_exists = conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.statistics "
                    "WHERE table_schema = DATABASE() AND table_name = :t AND index_name = :i"
                ), {"t": table_name, "i": idx_name}).scalar()
                if idx_exists:
                    print(f"  - {table_name}.{idx_name}: 索引已存在，跳过")
                    continue
                cols_sql = ", ".join(f"`{c}`" for c in idx_cols)
                conn.execute(text(f"CREATE INDEX `{idx_name}` ON `{table_name}` ({cols_sql})"))
                conn.commit()
                print(f"  ✅ {table_name}.{idx_name}: 新索引已添加")
                add_idx_count += 1

        count = 0
        for table_name, comment in TABLE_COMMENTS.items():
            if table_name in existing_tables:
                current_comment = existing_tables[table_name]
                # 如果注释已经是期望的值则跳过
                if current_comment == comment:
                    print(f"  - {table_name}: 注释已存在，跳过")
                    continue
                # 更新注释
                conn.execute(text(
                    f"ALTER TABLE `{table_name}` COMMENT = '{comment}'"
                ))
                conn.commit()
                print(f"  ✅ {table_name}: 注释已更新")
                count += 1
            else:
                print(f"  ⚠️ {table_name}: 表不存在，跳过")

        # 更新列注释
        col_count = 0
        for table_name, columns in COLUMN_COMMENTS.items():
            if table_name not in existing_tables:
                print(f"  ⚠️ {table_name}: 表不存在，跳过列注释")
                continue
            for col_name, col_comment in columns.items():
                conn.execute(text(
                    f"ALTER TABLE `{table_name}` MODIFY `{col_name}` "
                    f"{get_column_type(conn, table_name, col_name)} "
                    f"COMMENT '{col_comment}'"
                ))
                conn.commit()
                print(f"  ✅ {table_name}.{col_name}: 列注释已更新")
                col_count += 1

    print(f"\n🎉 共更新 {count} 张表的注释，{col_count} 个列的注释，新增 {add_col_count} 个列，{add_idx_count} 个索引")


def get_column_type(conn, table_name: str, col_name: str) -> str:
    """查询列定义（保留原类型/默认值/非空等属性）"""
    result = conn.execute(text(
        "SELECT COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA "
        "FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = :t AND column_name = :c"
    ), {"t": table_name, "c": col_name}).first()
    if not result:
        return col_name
    col_type, is_nullable, col_default, extra = result
    parts = [col_type]
    if is_nullable == "NO":
        parts.append("NOT NULL")
    if col_default is not None:
        default_val = col_default if col_default != "CURRENT_TIMESTAMP" else "CURRENT_TIMESTAMP"
        # 字符串/时间字面量类型（VARCHAR/CHAR/ENUM/SET/TEXT/日期时间）的 DEFAULT 需要加单引号
        # information_schema 中 col_default 是裸字面量（如 weekly / 2024-01-01），
        # 拼回 MODIFY COLUMN 语句时若不加引号，MySQL 解析会报 1064
        if default_val != "CURRENT_TIMESTAMP" and col_type.lower().startswith(
            ("varchar", "char", "enum", "set", "text", "tinytext", "mediumtext", "longtext",
             "date", "datetime", "timestamp")
        ):
            default_val = f"'{default_val}'"
        parts.append(f"DEFAULT {default_val}")
    if extra:
        parts.append(extra)
    return " ".join(parts)


if __name__ == "__main__":
    upgrade()
