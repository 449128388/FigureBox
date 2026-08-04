#!/bin/sh
# 启动入口 - 在启动 uvicorn 前执行数据库迁移

set -e

echo "🚀 执行数据库迁移..."

# 执行所有表注释补充（含 Base.metadata.create_all() 自动建表 + 表/列注释同步）
echo "→ 检查所有表注释..."
python migrations/add_all_table_comments.py

echo "✅ 数据库迁移完成"

# 启动 uvicorn
echo "🚀 启动应用服务器..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
