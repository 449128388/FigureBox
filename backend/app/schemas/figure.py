from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class FigureBase(BaseModel):
    name: str
    price: float
    currency: str = "CNY"
    manufacturer: str | None = None
    attribute: str | None = None
    release_date: date | None = None
    scale: str | None = None
    prototype: str | None = None
    painting: str | None = None
    original_art: str | None = None
    work: str | None = None
    material: str | None = None
    size: str | None = None
    description: str | None = None
    image_url: str | None = None
    images: List[str] | None = []

class FigureCreate(FigureBase):
    pass

class FigureUpdate(BaseModel):
    name: str | None = None
    manufacturer: str | None = None
    price: float | None = None
    currency: str | None = None
    attribute: str | None = None
    release_date: date | None = None
    scale: str | None = None
    prototype: str | None = None
    painting: str | None = None
    original_art: str | None = None
    work: str | None = None
    material: str | None = None
    size: str | None = None
    description: str | None = None
    image_url: str | None = None
    images: List[str] | None = None

class Figure(FigureBase):
    id: int

    class Config:
        from_attributes = True