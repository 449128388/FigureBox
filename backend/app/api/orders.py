from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate, OrderListItem
from app.api.users import get_current_user
from app.models.user import User
from app.services.order_service import OrderService

router = APIRouter()


@router.get("/unpaid-balance/")
def get_unpaid_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取未支付状态的尾款总额
    
    只统计未软删除的订单（is_active=1）
    """
    return OrderService.get_unpaid_balance(db, current_user)


@router.get("/", response_model=list[OrderListItem])
def get_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取订单列表
    
    只返回未软删除的订单（is_active=1）
    """
    return OrderService.get_orders(db, current_user)


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
