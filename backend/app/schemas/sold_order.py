from pydantic import BaseModel
from datetime import date, datetime
from app.schemas.figure import Figure

class SoldOrderBase(BaseModel):
    figure_id: int
    sell_price: float
    cost_price: float
    shipping_fee: float = 0.0
    platform_fee: float = 0.0
    sell_platform: str | None = None
    order_number: str | None = None
    buyer_phone: str | None = None
    buyer_address: str | None = None
    tracking_number: str | None = None
    shipping_date: date | None = None
    status: str = "待发货"
    remark: str | None = None

class SoldOrderCreate(SoldOrderBase):
    pass

class SoldOrderUpdate(BaseModel):
    figure_id: int | None = None
    sell_price: float | None = None
    cost_price: float | None = None
    shipping_fee: float | None = None
    platform_fee: float | None = None
    sell_platform: str | None = None
    order_number: str | None = None
    buyer_phone: str | None = None
    buyer_address: str | None = None
    tracking_number: str | None = None
    shipping_date: date | None = None
    status: str | None = None
    remark: str | None = None

class SoldOrder(SoldOrderBase):
    id: int
    user_id: int
    net_profit: float | None = None
    profit_rate: float | None = None
    figure: Figure

    class Config:
        from_attributes = True

class SoldOrderListItem(SoldOrderBase):
    id: int
    user_id: int
    net_profit: float | None = None
    profit_rate: float | None = None
    figure_name: str
    figure_image: str | None = None

    class Config:
        from_attributes = True

class SoldOrderStatistics(BaseModel):
    total_count: int
    pending_count: int
    shipped_count: int
    completed_count: int
    dispute_count: int
    total_net_profit: float