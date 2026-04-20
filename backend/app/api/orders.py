from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate, OrderListItem
from app.api.users import get_current_user
from app.models.user import User
from app.services.asset_transaction_service import AssetTransactionService
from sqlalchemy import func

router = APIRouter()


@router.get("/unpaid-balance/")
def get_unpaid_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取未支付状态的尾款总额
    
    只统计未软删除的订单（is_active=1）
    """
    if current_user.is_admin:
        # 管理员查看所有未支付订单的尾款总额
        total_balance = db.query(func.sum(Order.balance)).filter(
            Order.status == "未支付",
            Order.is_active == 1
        ).scalar()
    else:
        # 普通用户只查看自己的未支付订单的尾款总额
        total_balance = db.query(func.sum(Order.balance)).filter(
            Order.status == "未支付",
            Order.user_id == current_user.id,
            Order.is_active == 1
        ).scalar()
    
    # 如果没有未支付订单，返回0
    return {"total_unpaid_balance": float(total_balance) if total_balance else 0.0}


@router.get("/", response_model=list[OrderListItem])
def get_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取订单列表
    
    只返回未软删除的订单（is_active=1）
    """
    if current_user.is_admin:
        orders = db.query(Order).join(Figure).filter(Order.is_active == 1).all()
    else:
        orders = db.query(Order).join(Figure).filter(
            Order.user_id == current_user.id,
            Order.is_active == 1
        ).all()
        
    return [OrderListItem(
        id=order.id,
        user_id=order.user_id,
        figure_id=order.figure_id,
        figure_name=order.figure.name,
        figure_image=order.figure.images[0] if order.figure.images else None,
        deposit=order.deposit,
        deposit_currency=order.deposit_currency,
        balance=order.balance,
        balance_currency=order.balance_currency,
        due_date=order.due_date,
        status=order.status,
        shop_name=order.shop_name,
        shop_contact=order.shop_contact,
        tracking_number=order.tracking_number
    ) for order in orders]


@router.get("/{order_id}/", response_model=OrderSchema)
def get_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取单个订单详情
    
    只返回未软删除的订单（is_active=1）
    """
    order = db.query(Order).filter(Order.id == order_id, Order.is_active == 1).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return order


@router.post("/", response_model=OrderSchema)
def create_order(order: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    创建订单
    
    创建订单时会自动关联或创建对应的资产交易记录
    """
    # 检查手办是否存在
    db_figure = db.query(Figure).filter(Figure.id == order.figure_id).first()
    if not db_figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="手办不存在"
        )
    
    # 检查手办的订单数量是否超过手办的数量字段值（只计算未软删除的订单）
    order_count = db.query(func.count(Order.id)).filter(
        Order.figure_id == order.figure_id,
        Order.is_active == 1
    ).scalar()
    figure_quantity = db_figure.quantity or 1
    
    if order_count >= figure_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该手办已达到最大订单数量限制（{figure_quantity}个）"
        )
    
    db_order = Order(
        user_id=current_user.id,
        **order.dict()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # 【修复】创建资产交易记录（补录凭证模式）和资金流水记录
    try:
        # 1. 将订单关联到现有的库存记录（不新增记录）
        AssetTransactionService.link_order_to_existing_transaction(
            db=db,
            user_id=current_user.id,
            figure_id=order.figure_id,
            order=db_order
        )

        # 2. 创建资金流水记录（资金账）
        from app.services.order_transaction_service import OrderTransactionService

        # 计算订单总价（定金 + 尾款）
        total_price = db_order.deposit + db_order.balance

        OrderTransactionService.create_buy_transaction(
            db=db,
            user_id=current_user.id,
            figure_id=order.figure_id,
            order_id=db_order.id,
            quantity=1,
            unit_price=total_price,
            total_amount=total_price,
            payment_method=None,  # 可在订单中扩展此字段
            platform=None,  # 可在订单中扩展此字段
            notes=f"订单 #{db_order.id} 资金流水"
        )

        db.commit()
    except Exception as e:
        # 如果创建交易记录失败，不影响订单创建
        db.rollback()
        print(f"创建交易记录失败: {e}")

    return db_order


@router.put("/{order_id}/", response_model=OrderSchema)
def update_order(order_id: int, order: OrderUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    更新订单
    
    只能更新未软删除的订单（is_active=1）
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.is_active == 1).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    if not current_user.is_admin and db_order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{order_id}/")
def delete_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    软删除订单
    
    不物理删除订单记录，仅标记 is_active=False 和 deleted_at
    同时软删除关联的资产交易记录和资金流水记录
    """
    from app.models.asset import AssetTransaction, OrderTransaction
    from datetime import datetime

    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    if not current_user.is_admin and db_order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # 软删除关联的资产交易记录（库存账）
    db.query(AssetTransaction).filter(
        AssetTransaction.order_id == order_id
    ).update({
        'is_active': False,
        'deleted_at': datetime.now(),
        'order_id': None  # 解除外键关联，避免外键约束错误
    }, synchronize_session=False)

    # 软删除关联的资金流水记录（资金账）
    db.query(OrderTransaction).filter(
        OrderTransaction.order_id == order_id
    ).update({
        'is_active': False,
        'deleted_at': datetime.now(),
        'order_id': None  # 解除外键关联，避免外键约束错误
    }, synchronize_session=False)

    # 软删除订单本身
    db_order.is_active = 0
    db_order.deleted_at = datetime.now()
    
    db.commit()
    return {"message": "Order deleted successfully"}
