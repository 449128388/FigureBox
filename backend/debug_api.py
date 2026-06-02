"""
调试收益曲线API返回数据
"""
import sys
sys.path.insert(0, '/app')

from app.models.database import SessionLocal
from app.services.dashboard_service.assets_service.profit_curve_service import ProfitCurveService

db = SessionLocal()
user_id = 1

print("=" * 60)
print("调试收益曲线数据")
print("=" * 60)

# 获取收益曲线数据
result = ProfitCurveService.get_profit_curve_data(db, user_id, days=30)

print(f"\n返回数据条数: {len(result)}")
if len(result) > 0:
    print(f"\n数据样例:")
    print(f"  第一条: {result[0]}")
    print(f"  最后一条: {result[-1]}")
    print(f"\n所有数据:")
    for item in result:
        print(f"  {item['date']}: ¥{item['profit']}")
else:
    print("\n警告: 返回数据为空!")

print("\n" + "=" * 60)
db.close()
