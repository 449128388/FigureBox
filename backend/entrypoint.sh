#!/bin/sh
# 启动入口 - 在启动 uvicorn 前执行数据库迁移

set -e

echo "🚀 执行数据库迁移..."

# 执行所有表注释补充
echo "→ 检查所有表注释..."
python migrations/add_all_table_comments.py

# 清理废弃表（asset_alerts 已无代码使用）
echo "→ 清理废弃表..."
python -c "
from app.models.database import engine
from sqlalchemy import inspect, text
inspector = inspect(engine)
if inspector.has_table('asset_alerts'):
    with engine.connect() as conn:
        conn.execute(text('DROP TABLE IF EXISTS asset_alerts'))
        conn.commit()
        print('  ✅ asset_alerts 表已删除')
else:
    print('  · asset_alerts 表不存在，跳过')
"

echo "✅ 数据库迁移完成"

# 启动 uvicorn
echo "🚀 启动应用服务器..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
