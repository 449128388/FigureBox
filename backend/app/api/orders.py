from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate, OrderListItem, OrderListResponse
from app.api.users import get_current_user
from app.models.user import User
from app.services.order_service import OrderService

router = APIRouter()


class BatchDeleteRequest(BaseModel):
    """批量删除请求模型"""
    order_ids: list[int]


@router.get("/unpaid-balance/")
def get_unpaid_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取未支付状态的尾款总额
    
    只统计未软删除的订单（is_active=1）
    """
    return OrderService.get_unpaid_balance(db, current_user)


@router.get("/", response_model=OrderListResponse)
def get_orders(
    figure_name: str = None,
    due_date_start: str = None,
    due_date_end: str = None,
    figure_id: int = None,
    status: str = Query(None, description="订单状态过滤：未支付/已支付/已取消/已完成；不传则返回全部状态"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页条数（1-100）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取订单分页列表（2026-08-06 重构：尾款管理翻页走服务端）

    只返回未软删除的订单（is_active=1）

    查询参数：
    - figure_name: 手办名称模糊搜索
    - due_date_start: 出荷日期开始（格式：YYYY-MM-DD）
    - due_date_end: 出荷日期结束（格式：YYYY-MM-DD）
    - figure_id: 手办ID精确过滤（手办详情页专用，只取关联订单）
    - status: 订单状态过滤（未支付/已支付/已取消/已完成）
    - skip: 分页起始位置
    - limit: 每页条数

    返回：
    - items: 当前页订单列表
    - total: 符合当前过滤条件的总数（用于前端分页器）
    - status_counts: 各状态订单计数（用于状态 Tab 展示）
    """
    from datetime import datetime

    # 解析日期参数
    start_date = None
    end_date = None
    if due_date_start:
        try:
            start_date = datetime.strptime(due_date_start, "%Y-%m-%d").date()
        except ValueError:
            pass
    if due_date_end:
        try:
            end_date = datetime.strptime(due_date_end, "%Y-%m-%d").date()
        except ValueError:
            pass

    return OrderService.get_orders_page(
        db=db,
        current_user=current_user,
        figure_name=figure_name,
        due_date_start=start_date,
        due_date_end=end_date,
        figure_id=figure_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.get("/{order_id}/", response_model=OrderSchema)
def get_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取单个订单详情
    
    只返回未软删除的订单（is_active=1）
    """
    return OrderService.get_order_by_id(db, order_id, current_user)


@router.post("/", response_model=OrderSchema)
def create_order(order: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    创建订单
    
    创建订单时会自动关联或创建对应的资产交易记录
    """
    return OrderService.create_order(db, order, current_user)


@router.put("/{order_id}/", response_model=OrderSchema)
def update_order(order_id: int, order: OrderUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    更新订单
    
    只能更新未软删除的订单（is_active=1）
    """
    return OrderService.update_order(db, order_id, order, current_user)


@router.delete("/{order_id}/")
def delete_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    软删除订单
    
    不物理删除订单记录，仅标记 is_active=False 和 deleted_at
    同时软删除关联的资产交易记录和资金流水记录
    """
    return OrderService.delete_order(db, order_id, current_user)


@router.post("/batch-delete/")
def batch_delete_orders(request: BatchDeleteRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    批量软删除订单
    
    不物理删除订单记录，仅标记 is_active=False 和 deleted_at
    同时软删除关联的资产交易记录和资金流水记录
    
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
    
    return OrderService.batch_delete_orders(db, request.order_ids, current_user)
