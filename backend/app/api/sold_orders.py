from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.models.sold_order import SoldOrder
from app.models.figure import Figure
from app.schemas.sold_order import SoldOrder as SoldOrderSchema, SoldOrderCreate, SoldOrderUpdate, SoldOrderListItem, SoldOrderStatistics
from app.api.users import get_current_user
from app.models.user import User
from app.services.sold_order_service import SoldOrderService

router = APIRouter()


class BatchDeleteRequest(BaseModel):
    """批量删除请求模型"""
    order_ids: list[int]


@router.get("/statistics/")
def get_sold_order_statistics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取已出售订单统计信息
    
    返回各状态订单数量和累计净利润
    """
    return SoldOrderService.get_sold_order_statistics(db, current_user)


@router.get("/xianyu-monthly-stats/")
def get_xianyu_monthly_statistics(
    exclude_order_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户当月闲鱼订单统计信息（用于计算平台手续费）
    
    统计当月（自然月）的闲鱼订单数量和成交额
    用于根据用户选择的平台类型自动套用对应费率
    
    Args:
        exclude_order_id: 需要排除的订单ID（编辑时使用）
    
    Returns:
        Dict: 包含订单数量和成交额的字典
        - order_count: 当月订单数量
        - total_amount: 当月成交总额
    """
    return SoldOrderService.get_xianyu_monthly_statistics(db, current_user, exclude_order_id)


@router.get("/", response_model=list[SoldOrderListItem])
def get_sold_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取已出售订单列表
    
    只返回未软删除的订单（is_active=1）
    """
    return SoldOrderService.get_sold_orders(db, current_user)


@router.get("/{order_id}/", response_model=SoldOrderSchema)
def get_sold_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取单个已出售订单详情
    
    只返回未软删除的订单（is_active=1）
    """
    order = SoldOrderService.get_sold_order_by_id(db, order_id, current_user)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在或已被删除"
        )
    return order


@router.post("/", response_model=SoldOrderSchema)
def create_sold_order(order: SoldOrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    创建已出售订单
    
    创建时自动计算净利润和利润率
    """
    return SoldOrderService.create_sold_order(db, order, current_user)


@router.put("/{order_id}/", response_model=SoldOrderSchema)
def update_sold_order(order_id: int, order: SoldOrderUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    更新已出售订单
    
    只能更新未软删除的订单（is_active=1）
    更新时自动重新计算净利润和利润率
    """
    try:
        return SoldOrderService.update_sold_order(db, order_id, order, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{order_id}/")
def delete_sold_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    软删除已出售订单
    
    不物理删除订单记录，仅标记 is_active=False 和 deleted_at
    """
    try:
        return SoldOrderService.delete_sold_order(db, order_id, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/batch-delete/")
def batch_delete_sold_orders(request: BatchDeleteRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    批量软删除已出售订单
    
    不物理删除订单记录，仅标记 is_active=False 和 deleted_at
    
    Args:
        order_ids: 要删除的订单ID列表
        
    Returns:
        删除结果统计
    """
    if not request.order_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单ID列表不能为空"
        )
    
    return SoldOrderService.batch_delete_sold_orders(db, request.order_ids, current_user)