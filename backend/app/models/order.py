from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

class Order(Base):
    """
    订单模型 - 存储手办购买订单的详细信息
    
    功能说明：
    - 记录每个手办的购买订单详情
    - 支持分期付款（定金+尾款）模式
    - 跟踪订单状态和物流信息
    - 关联用户和手办
    
    订单状态说明：
    - 未支付：订单已创建，尚未支付定金
    - 已支付：已支付定金，等待支付尾款
    - 已完成：已支付全部款项，订单完成
    - 已取消：订单已取消
    
    关联关系：
    - user: 多对一关联 User 表（订单所属用户）
    - figure: 多对一关联 Figure 表（订单对应的手办）
    """
    __tablename__ = "orders"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 订单唯一标识ID
    
    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联用户ID（订单所属用户）
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False)  # 关联手办ID（订单对应的手办）
    
    # 付款信息（支持定金+尾款模式）
    deposit = Column(Float, nullable=False)  # 定金金额（预付款）
    balance = Column(Float, nullable=False)  # 尾款金额（剩余款项）
    due_date = Column(Date, nullable=True)  # 尾款截止日期/预计出货日期
    
    # 订单状态
    status = Column(String(20), default="未支付")  # 订单状态：未支付、已支付、已取消、已完成
    
    # 店铺信息
    shop_name = Column(String(100))  # 购买店铺名称（如：淘宝店铺、会员购等）
    shop_contact = Column(String(200))  # 店铺联系方式（客服、QQ群等）
    tracking_number = Column(String(100))  # 物流订单号/快递单号

    # 关系
    user = relationship("User")  # 关联用户对象
    figure = relationship("Figure")  # 关联手办对象
