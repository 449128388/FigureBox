"""
operation_position.py - 补仓操作层

功能说明：
- 提供补仓操作相关API端点
- 执行补仓流程：创建订单、记录交易、更新库存等

API端点：
- POST /figures/{figure_id}/add-position: 执行补仓操作

依赖：
- fastapi.APIRouter, HTTPException
- sqlalchemy.orm.Session
- app.services.dashboard_service.assets_service.AddPositionService
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
from app.services.dashboard_service.assets_service import AddPositionService

router = APIRouter()


class AddPositionRequest(BaseModel):
    """补仓请求模型"""
    quantity: int  # 补仓数量
    price: float   # 补仓单价


@router.post("/figures/{figure_id}/add-position")
def add_position(
    figure_id: int,
    request: AddPositionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    执行补仓操作

    补仓流程:
    1. 创建已完成状态的订单（补仓视同已完成购买）
    2. 创建asset_transactions记录（买入）
    3. 创建order_transactions记录（资金流出）
    4. 更新手办数量和平均入手价格（加权平均）
    5. 更新日涨跌缓存（新买入部分按买入价=市值处理，贡献0%波动）

    参数:
        figure_id: 手办ID
        quantity: 补仓数量
        price: 补仓单价

    返回:
        补仓操作结果
    """
    try:
        result = AddPositionService.add_position(
            db=db,
            user_id=current_user.id,
            figure_id=figure_id,
            quantity=request.quantity,
            price=request.price
        )

        return {
            "message": "补仓成功",
            "figure_id": result["figure_id"],
            "figure_name": result["figure_name"],
            "order_ids": result["order_ids"],
            "added_quantity": result["added_quantity"],
            "add_price": result["add_price"],
            "previous_quantity": result["previous_quantity"],
            "new_quantity": result["new_quantity"],
            "previous_cost_price": result["previous_cost_price"],
            "new_cost_price": result["new_cost_price"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"补仓失败: {str(e)}")
