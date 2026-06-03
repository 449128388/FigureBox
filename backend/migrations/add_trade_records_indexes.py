"""
交易流水查询索引优化迁移脚本

功能说明：
- 为交易流水查询涉及的时间字段建立索引
- 优化按时间倒序查询的性能
- 支持用户ID+时间的复合查询

创建时间: 2026-06-02
"""

from sqlalchemy import create_engine, text
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def upgrade():
    """
    添加索引优化交易流水查询性能
    """
    # 从环境变量获取数据库连接
    from dotenv import load_dotenv
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://admin:password@localhost:3306/figurebox")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. 为 sold_orders 表的 created_at 字段添加索引
        # 用于卖出交易流水按时间倒序查询
        try:
            conn.execute(text("""
                CREATE INDEX idx_sold_orders_user_created_at 
                ON sold_orders(user_id, created_at DESC)
            """))
            print("✅ 创建索引: idx_sold_orders_user_created_at")
        except Exception as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("⚠️ 索引已存在: idx_sold_orders_user_created_at")
            else:
                print(f"❌ 创建索引失败: {e}")
        
        # 2. 为 orders 表的 created_at 字段添加索引
        # 用于买入交易流水按时间倒序查询
        try:
            conn.execute(text("""
                CREATE INDEX idx_orders_user_created_at 
                ON orders(user_id, created_at DESC)
            """))
            print("✅ 创建索引: idx_orders_user_created_at")
        except Exception as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("⚠️ 索引已存在: idx_orders_user_created_at")
            else:
                print(f"❌ 创建索引失败: {e}")
        
        # 3. 为 asset_transactions 表的 transaction_date 字段添加索引
        # 用于资产交易记录按时间倒序查询
        try:
            conn.execute(text("""
                CREATE INDEX idx_asset_transactions_user_date 
                ON asset_transactions(user_id, transaction_date DESC)
            """))
            print("✅ 创建索引: idx_asset_transactions_user_date")
        except Exception as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("⚠️ 索引已存在: idx_asset_transactions_user_date")
            else:
                print(f"❌ 创建索引失败: {e}")
        
        # 4. 为 order_transactions 表的 transaction_date 字段添加索引
        # 用于订单交易流水按时间倒序查询
        try:
            conn.execute(text("""
                CREATE INDEX idx_order_transactions_user_date 
                ON order_transactions(user_id, transaction_date DESC)
            """))
            print("✅ 创建索引: idx_order_transactions_user_date")
        except Exception as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("⚠️ 索引已存在: idx_order_transactions_user_date")
            else:
                print(f"❌ 创建索引失败: {e}")
        
        # 5. 为 sold_orders 表的 status 和 is_active 字段添加复合索引
        # 用于筛选已完成且未删除的卖出订单
        try:
            conn.execute(text("""
                CREATE INDEX idx_sold_orders_user_status_active 
                ON sold_orders(user_id, status, is_active)
            """))
            print("✅ 创建索引: idx_sold_orders_user_status_active")
        except Exception as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("⚠️ 索引已存在: idx_sold_orders_user_status_active")
            else:
                print(f"❌ 创建索引失败: {e}")
        
        # 6. 为 orders 表的 status 和 is_active 字段添加复合索引
        # 用于筛选未删除的买入订单
        try:
            conn.execute(text("""
                CREATE INDEX idx_orders_user_status_active 
                ON orders(user_id, status, is_active)
            """))
            print("✅ 创建索引: idx_orders_user_status_active")
        except Exception as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("⚠️ 索引已存在: idx_orders_user_status_active")
            else:
                print(f"❌ 创建索引失败: {e}")
        
        conn.commit()
        print("\n🎉 索引优化完成！")

def downgrade():
    """
    回滚：删除添加的索引
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://admin:password@localhost:3306/figurebox")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        indexes = [
            "idx_sold_orders_user_created_at",
            "idx_orders_user_created_at",
            "idx_asset_transactions_user_date",
            "idx_order_transactions_user_date",
            "idx_sold_orders_user_status_active",
            "idx_orders_user_status_active"
        ]
        
        for index_name in indexes:
            try:
                conn.execute(text(f"DROP INDEX {index_name} ON sold_orders"))
                print(f"✅ 删除索引: {index_name}")
            except:
                try:
                    conn.execute(text(f"DROP INDEX {index_name} ON orders"))
                    print(f"✅ 删除索引: {index_name}")
                except:
                    try:
                        conn.execute(text(f"DROP INDEX {index_name} ON asset_transactions"))
                        print(f"✅ 删除索引: {index_name}")
                    except:
                        try:
                            conn.execute(text(f"DROP INDEX {index_name} ON order_transactions"))
                            print(f"✅ 删除索引: {index_name}")
                        except Exception as e:
                            print(f"⚠️ 删除索引失败或索引不存在: {index_name}")
        
        conn.commit()
        print("\n🎉 索引回滚完成！")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
