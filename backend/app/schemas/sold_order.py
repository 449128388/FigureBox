import re
from pydantic import BaseModel, field_validator
from datetime import date, datetime
from app.schemas.figure import Figure

class SoldOrderBase(BaseModel):
    figure_id: int | str
    quantity: int = 1  # 卖出数量，默认为1
    sell_price: float
    cost_price: float
    shipping_fee: float = 0.0
    platform_fee: float = 0.0
    sell_price_currency: str = "CNY"
    cost_price_currency: str = "CNY"
    shipping_fee_currency: str = "CNY"
    platform_fee_currency: str = "CNY"
    sell_platform: str
    order_number: str | None = None
    buyer_phone: str
    buyer_address: str | None = None
    tracking_number: str | None = None
    shipping_date: datetime | None = None
    status: str
    remark: str | None = None
    
    @field_validator('sell_price_currency', 'cost_price_currency', 'shipping_fee_currency', 'platform_fee_currency')
    @classmethod
    def validate_currency(cls, v):
        allowed_currencies = ['CNY', 'USD', 'JPY', 'EUR']
        if v and v not in allowed_currencies:
            raise ValueError(f'币种必须是以下之一: {", ".join(allowed_currencies)}')
        return v or 'CNY'

    @field_validator('figure_id', mode='before')
    @classmethod
    def validate_figure_id(cls, v):
        # 处理空字符串或None的情况
        if v == '' or v is None:
            raise ValueError('请选择手办')
        # 尝试转换为整数
        try:
            return int(v)
        except ValueError:
            raise ValueError('手办ID格式不正确')

    @field_validator('sell_platform')
    @classmethod
    def validate_sell_platform(cls, v):
        if v == '' or v is None:
            raise ValueError('请选择卖出平台')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v == '' or v is None:
            raise ValueError('请选择卖出状态')
        allowed_statuses = ['待发货', '已发货', '已完成', '退款/纠纷']
        if v not in allowed_statuses:
            raise ValueError(f'卖出状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @field_validator('buyer_phone')
    @classmethod
    def validate_buyer_phone(cls, v):
        if v == '' or v is None:
            raise ValueError('请输入买家手机号')
        # 手机号格式校验：支持大陆手机号
        pattern = r'^(1[3-9]\d{9})$'
        if not re.match(pattern, v):
            raise ValueError('手机号格式不正确，请输入11位有效手机号')
        return v

    @field_validator('buyer_address')
    @classmethod
    def validate_buyer_address(cls, v):
        # 买家地址为非必填项，空字符串转为None
        if v == '':
            return None
        return v

    @field_validator('sell_price', mode='before')
    @classmethod
    def validate_sell_price(cls, v):
        # 卖出价格为必填项
        if v is None or v == '':
            raise ValueError('请输入卖出价格')
        try:
            price = float(v)
            if price <= 0:
                raise ValueError('卖出价格必须大于0')
            return price
        except (ValueError, TypeError):
            raise ValueError('卖出价格格式不正确')

class SoldOrderCreate(SoldOrderBase):
    pass

class SoldOrderUpdate(BaseModel):
    figure_id: int | None = None
    sell_price: float | None = None
    cost_price: float | None = None
    shipping_fee: float | None = None
    platform_fee: float | None = None
    sell_price_currency: str | None = None
    cost_price_currency: str | None = None
    shipping_fee_currency: str | None = None
    platform_fee_currency: str | None = None
    sell_platform: str | None = None
    order_number: str | None = None
    buyer_phone: str | None = None
    buyer_address: str | None = None
    tracking_number: str | None = None
    shipping_date: datetime | None = None
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