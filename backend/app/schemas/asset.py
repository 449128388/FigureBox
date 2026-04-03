from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional

class AssetPriceHistoryBase(BaseModel):
    figure_id: int
    current_price: float

class AssetPriceHistoryCreate(AssetPriceHistoryBase):
    pass

class AssetPriceHistory(AssetPriceHistoryBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True

class AssetAlertBase(BaseModel):
    figure_id: int
    alert_type: str
    threshold: float

class AssetAlertCreate(AssetAlertBase):
    pass

class AssetAlert(AssetAlertBase):
    id: int
    user_id: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True

class AssetTransactionBase(BaseModel):
    figure_id: int
    transaction_type: str
    price: float
    notes: Optional[str] = None

class AssetTransactionCreate(AssetTransactionBase):
    pass

class AssetTransaction(AssetTransactionBase):
    id: int
    user_id: int
    transaction_date: datetime

    class Config:
        from_attributes = True

class AssetSummary(BaseModel):
    total_assets: float
    daily_change: float
    daily_change_percentage: float
    plastic_index: float
    sh_index: float
    outperform_percentage: float
    position: str
    monthly_purchases: int

class AssetDetail(BaseModel):
    figure_id: int
    figure_name: str
    cost_price: float
    current_price: float
    profit: float
    profit_percentage: float
    status: str

class AssetKlineData(BaseModel):
    date: datetime
    value: float

class AssetRanking(BaseModel):
    figure_id: int
    figure_name: str
    change_percentage: float
    trend: str  # up, down, stable

class AssetAdvice(BaseModel):
    figure_name: str
    advice: str

class AssetDashboard(BaseModel):
    summary: AssetSummary
    kline_data: List[AssetKlineData]
    rankings: List[AssetRanking]
    advice: List[AssetAdvice]
    holdings: List[AssetDetail]
