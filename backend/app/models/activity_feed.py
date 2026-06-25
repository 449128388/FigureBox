"""
activity_feed.py - 用户动态流模型

功能说明：
- 记录用户与藏品/订单的所有交互事件
- 支持多态关联（order/tag 等）
- 按时间倒序排列，用于动态流展示

事件类型：
- BUY: 入手（创建订单）
- FULL_PAY: 尾款已付清
- IN_STOCK: 手办到库
- SELL: 已售出
- OUT: 移出收藏柜
- TAG_ADD: 添加标签
- FIX: 待修复标记
- ORDER_CREATE: 创建订单
- ORDER_CANCEL: 取消订单
- PRICE_UPDATE: 价格更新
"""

from sqlalchemy import Column, BigInteger, Integer, String, DateTime, TIMESTAMP, Date, JSON, text, func
from app.models.database import Base


class ActivityFeed(Base):
    """用户动态流表"""
    __tablename__ = "activity_feed"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "comment": "用户动态流"
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    figure_id = Column(Integer, nullable=False, comment="手办ID")

    event_type = Column(String(32), nullable=False, comment="事件类型：BUY: 入手（创建订单）/FULL_PAY: 尾款已付清/IN_STOCK: 手办到库/SELL: 已售出/OUT: 移出收藏柜/TAG_ADD: 添加标签/FIX: 待修复标记/ORDER_CREATE: 创建订单/ORDER_CANCEL: 取消订单/PRICE_UPDATE: 价格更新")
    event_title = Column(String(255), nullable=False, comment="展示标题，如：入手「蜜姬」，等待补款")

    # 关联对象（多态关联）
    target_type = Column(String(32), default=None, comment="关联对象类型：order/tag")
    target_id = Column(Integer, default=None, comment="关联对象ID")

    # 详情数据（JSON，用于详情弹窗展示）
    detail_data = Column(JSON, default=None, comment="详情数据：{figure_name, order_no, amount, status, before, after...}")

    # 时间轴分组
    event_date = Column(Date, nullable=False, comment="事件日期（用于按天分栏）")
    is_cancelled = Column(Integer, default=0, comment="是否已取消/回滚：0=正常，1=已取消")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), onupdate=func.now(), comment="更新时间")
