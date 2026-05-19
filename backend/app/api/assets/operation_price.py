"""
operation_price.py - 价格更新操作层

功能说明：
- 提供手办价格更新相关API端点
- 包括获取手办价格信息、更新手办现价等

API端点：
- GET /figures/{figure_id}/price-info: 获取手办价格信息
- POST /figures/{figure_id}/update-price: 更新手办现价

依赖：
- fastapi.APIRouter, HTTPException
- sqlalchemy.orm.Session
- app.services.AssetCalculationService
- pydantic.BaseModel

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services import AssetCalculationService

router = APIRouter()


class PriceUpdateRequest(BaseModel):
    """价格更新请求模型"""
    new_price: float
    currency: str = "CNY"  # 默认人民币，可选：CNY, JPY, USD, EUR


@router.get("/figures/{figure_id}/price-info")
def get_figure_price_info(
    figure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取手办价格信息（用于修改现价弹窗）
    
    返回手办的当前价格、成本价、盈亏比例等信息
    """
    figure = AssetCalculationService.get_figure_current_price(db, figure_id)
    if not figure:
        raise HTTPException(status_code=404, detail="手办不存在")

    # 获取最新价格历史
    latest_history = AssetCalculationService.get_price_history(db, figure_id)

    # 计算影响
    current_price = figure.market_price or figure.price or 0
    impact = AssetCalculationService.calculate_price_update_impact(
        db, current_user.id, figure, current_price
    )
    
    # 计算单个手办的盈亏比例
    cost_price = figure.average_purchase_price or 0
    quantity = figure.quantity or 1
    if cost_price > 0:
        current_profit = current_price - cost_price
        current_profit_percentage = (current_profit / cost_price) * 100
    else:
        current_profit_percentage = 0
    
    return {
        "figure_id": figure.id,
        "figure_name": figure.name,
        "current_price": current_price,
        "cost_price": cost_price,
        "last_updated": latest_history.date if latest_history else figure.purchase_date,
        "quantity": quantity,
        "total_assets": impact["old_total_assets"],
        "profit_percentage": current_profit_percentage,
        "total_profit_percentage": impact["old_profit_percentage"]
    }


@router.post("/figures/{figure_id}/update-price")
def update_figure_price(
    figure_id: int,
    request: PriceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新手办现价
    
    更新手办的市场价格，并返回更新后的影响数据
    """
    try:
        result = AssetCalculationService.update_figure_price(
            db, figure_id, request.new_price, current_user.id
        )

        # 确定新状态
        new_status = AssetCalculationService.determine_status(
            result["impact"]["new_profit_percentage"]
        )
        
        return {
            "message": "价格更新成功",
            "figure_id": figure_id,
            "figure_name": result["figure"].name,
            "old_price": result["old_price"],
            "new_price": result["new_price"],
            "new_status": new_status,
            "impact": {
                "old_total_assets": result["impact"]["old_total_assets"],
                "new_total_assets": result["impact"]["new_total_assets"],
                "old_profit_percentage": result["impact"]["old_profit_percentage"],
                "new_profit_percentage": result["impact"]["new_profit_percentage"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"价格更新失败: {str(e)}")
