from pydantic import BaseModel
from datetime import date
from app.schemas.figure import Figure

class OrderBase(BaseModel):
    figure_id: int
    deposit: float
    deposit_currency: str = "CNY"
    balance: float
    balance_currency: str = "CNY"
    due_date: date
    shop_name: str | None = None
    shop_contact: str | None = None

class OrderCreate(OrderBase):
    status: str
    # 【修复】已取消状态的订单不需要出荷日期，设置为可选
    due_date: date | None = None
    tracking_number: str | None = None
    order_number: str | None = None

class OrderUpdate(BaseModel):
    deposit: float | None = None
    deposit_currency: str | None = None
    balance: float | None = None
    balance_currency: str | None = None
    due_date: date | None = None
    status: str | None = None
    shop_name: str | None = None
    shop_contact: str | None = None
    tracking_number: str | None = None
    order_number: str | None = None

class Order(OrderBase):
    id: int
    user_id: int
    status: str
    tracking_number: str | None = None
    order_number: str | None = None
    figure: Figure
    due_date: date | None = None  # 允许为空

    class Config:
        from_attributes = True

class OrderListItem(OrderBase):
    id: int
    user_id: int
    status: str
    tracking_number: str | None = None
    order_number: str | None = None
    figure_name: str
    figure_image: str | None = None
    due_date: date | None = None

    class Config:
        from_attributes = True