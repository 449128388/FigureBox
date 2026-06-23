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

echo "✅ 数据库迁移完成"

# 启动 uvicorn
echo "🚀 启动应用服务器..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
