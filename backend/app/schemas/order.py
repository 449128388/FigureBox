from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from app.schemas.figure import Figure

class OrderBase(BaseModel):
    figure_id: int
    order_type: str = "定金预定"  # 订单类型：定金预定、全款预定、现货、补仓
    deposit: float
    deposit_currency: str = "CNY"
    balance: float
    balance_currency: str = "CNY"
    due_date: date
    shop_name: str | None = None
    shop_contact: str | None = None
    logistics_company: str | None = None  # 物流公司：顺丰、圆通、中通、申通、韵达、EMS、其他
    payment_method: str | None = None  # 定金支付方式：支付宝、微信、银行卡转账、现金
    payment_time: datetime | None = None  # 定金支付时间
    balance_payment_method: str | None = None  # 尾款支付方式：支付宝、微信、银行卡转账、现金
    balance_payment_time: datetime | None = None  # 尾款支付时间
    remarks: str | None = None

class OrderCreate(OrderBase):
    order_type: str = "定金预定"  # 订单类型：定金预定、全款预定、现货、补仓
    status: str
    # 【修复】已取消状态的订单不需要出荷日期，设置为可选
    due_date: date | None = None
    tracking_number: str | None = None
    logistics_company: str | None = None  # 物流公司：顺丰、圆通、中通、申通、韵达、EMS、其他
    order_number: str | None = None
    payment_method: str | None = None  # 定金支付方式：支付宝、微信、银行卡转账、现金
    payment_time: datetime | None = None  # 定金支付时间
    balance_payment_method: str | None = None  # 尾款支付方式：支付宝、微信、银行卡转账、现金
    balance_payment_time: datetime | None = None  # 尾款支付时间
    remarks: str | None = None

class OrderUpdate(BaseModel):
    order_type: str | None = None  # 订单类型：定金预定、全款预定、现货、补仓
    deposit: float | None = None
    deposit_currency: str | None = None
    balance: float | None = None
    balance_currency: str | None = None
    due_date: date | None = None
    status: str | None = None
    shop_name: str | None = None
    shop_contact: str | None = None
    tracking_number: str | None = None
    logistics_company: str | None = None  # 物流公司：顺丰、圆通、中通、申通、韵达、EMS、其他
    order_number: str | None = None
    payment_method: str | None = None  # 定金支付方式：支付宝、微信、银行卡转账、现金
    payment_time: datetime | None = None  # 定金支付时间
    balance_payment_method: str | None = None  # 尾款支付方式：支付宝、微信、银行卡转账、现金
    balance_payment_time: datetime | None = None  # 尾款支付时间
    remarks: str | None = None

class Order(OrderBase):
    id: int
    user_id: int
    order_type: str = "定金预定"  # 订单类型：定金预定、全款预定、现货、补仓
    status: str
    tracking_number: str | None = None
    logistics_company: str | None = None  # 物流公司：顺丰、圆通、中通、申通、韵达、EMS、其他
    order_number: str | None = None
    payment_method: str | None = None  # 定金支付方式：支付宝、微信、银行卡转账、现金
    payment_time: datetime | None = None  # 定金支付时间
    balance_payment_method: str | None = None  # 尾款支付方式：支付宝、微信、银行卡转账、现金
    balance_payment_time: datetime | None = None  # 尾款支付时间
    remarks: str | None = None
    figure: Figure
    due_date: date | None = None  # 允许为空
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间

    class Config:
        from_attributes = True

class OrderListItem(OrderBase):
    id: int
    user_id: int
    order_type: str = "定金预定"  # 订单类型：定金预定、全款预定、现货、补仓
    status: str
    tracking_number: str | None = None
    logistics_company: str | None = None  # 物流公司：顺丰、圆通、中通、申通、韵达、EMS、其他
    order_number: str | None = None
    payment_method: str | None = None  # 定金支付方式：支付宝、微信、银行卡转账、现金
    payment_time: datetime | None = None  # 定金支付时间
    balance_payment_method: str | None = None  # 尾款支付方式：支付宝、微信、银行卡转账、现金
    balance_payment_time: datetime | None = None  # 尾款支付时间
    remarks: str | None = None
    figure_name: str
    figure_image: str | None = None
    due_date: date | None = None
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单分页列表响应（2026-08-06 新增：尾款管理翻页走服务端，与手办库分页响应结构一致）

    - items: 当前页订单列表（OrderListItem 精简字段）
    - total: 符合当前过滤条件的订单总数（用于前端分页器 total）
    - status_counts: 各状态订单计数（应用 figure_name / due_date_range 过滤，但不应用 status 过滤），
      用于前端状态 Tab 上的"未支付 (12)"等计数展示
    """
    items: list[OrderListItem]
    total: int
    status_counts: dict[str, int] = {}

    class Config:
        from_attributes = True
