"""
exchange_rates_api.py - 汇率查询 API

提供前端获取实时汇率数据的接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict

from app.models.database import get_db
from app.services.exchange_rate_service import ExchangeRateService

router = APIRouter()


@router.get("/exchange-rates")
async def get_exchange_rates(
    db: Session = Depends(get_db)
) -> Dict[str, float]:
    """
    获取当前汇率映射表

    返回格式：
    {
        "CNY": 1.0,
        "USD": 7.0,
        "JPY": 0.0435,
        "EUR": 8.0,
        "HKD": 0.9,
        "GBP": 9.0
    }
    """
    return ExchangeRateService.get_exchange_rates(db)
