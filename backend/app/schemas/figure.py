from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import List, Optional

class FigureBase(BaseModel):
    name: str
    price: float | None = None
    currency: str = "CNY"
    manufacturer: str | None = None
    tags: str | None = None
    release_date: date | None = None
    purchase_price: float | None = None
    purchase_date: date | None = None

    @field_validator('release_date', 'purchase_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            # 处理 ISO 格式日期时间字符串 (如: 2026-03-06T16:00:00.000Z)
            if 'T' in v:
                # 提取日期部分
                v = v.split('T')[0]
            # 解析日期字符串
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v
    purchase_method: str | None = None
    purchase_type: str | None = None
    scale: str | None = None
    prototype: str | None = None
    painting: str | None = None
    original_art: str | None = None
    work: str | None = None
    material: str | None = None
    size: str | None = None
    description: str | None = None
    images: List[str] | None = []

class FigureCreate(FigureBase):
    pass

class FigureUpdate(BaseModel):
    name: str | None = None
    manufacturer: str | None = None
    price: float | None = None
    currency: str | None = None
    tags: str | None = None
    release_date: date | None = None
    purchase_price: float | None = None
    purchase_date: date | None = None
    purchase_method: str | None = None
    purchase_type: str | None = None
    scale: str | None = None
    prototype: str | None = None
    painting: str | None = None
    original_art: str | None = None
    work: str | None = None
    material: str | None = None
    size: str | None = None
    description: str | None = None
    images: List[str] | None = None

class Figure(FigureBase):
    id: int

    class Config:
        from_attributes = True