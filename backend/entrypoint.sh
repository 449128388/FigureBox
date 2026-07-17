#!/bin/sh
# 启动入口 - 在启动 uvicorn 前执行数据库迁移

set -e

echo "🚀 执行数据库迁移..."

# 执行所有表注释补充
echo "→ 检查所有表注释..."
python migrations/add_all_table_comments.py

# 执行订单支付字段迁移
echo "→ 检查订单支付字段..."
python migrations/add_order_payment_fields.py

# 执行订单尾款支付字段迁移
echo "→ 检查订单尾款支付字段..."
python migrations/add_order_balance_payment_fields.py

# 执行 order_transactions 支付字段迁移
echo "→ 检查 order_transactions 支付字段..."
python migrations/add_order_transaction_payment_fields.py

echo "✅ 数据库迁移完成"

# 启动 uvicorn
echo "🚀 启动应用服务器..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
