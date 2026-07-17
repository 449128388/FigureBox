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
