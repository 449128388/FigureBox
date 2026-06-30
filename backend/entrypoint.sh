#!/bin/sh
# 启动入口 - 在启动 uvicorn 前执行数据库迁移

set -e

echo "🚀 执行数据库迁移..."

# 执行收藏柜喜爱度评分表迁移
echo "→ 检查 cabinet_ratings 表..."
python migrations/add_cabinet_rating_table.py

# 执行展示分类排除表迁移
echo "→ 检查 cabinet_figure_exclusions 表..."
python migrations/add_cabinet_exclusion_table.py

# 执行汇率缓存和历史表迁移
echo "→ 检查 exchange_rate 表..."
python migrations/add_exchange_rate_tables.py

# 执行汇率表备注迁移
echo "→ 检查 exchange_rate 表备注..."
python migrations/add_exchange_rate_comments.py

# 执行所有表注释补充
echo "→ 检查所有表注释..."
python migrations/add_all_table_comments.py

# 执行 user_settings → users_info 合并迁移
echo "→ 合并 user_settings 到 users_info 表..."
python migrations/merge_user_settings_into_users.py

# 执行 HPI 表创建
echo "→ 检查 HPI 表..."
python migrations/add_hpi_tables.py

echo "✅ 数据库迁移完成"

# 启动 uvicorn
echo "🚀 启动应用服务器..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
