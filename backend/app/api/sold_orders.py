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
from app.services.sold_order_service.quick_sell_service import QuickSellService
from app.services.dashboard_service.assets_service.holding_position_service import HoldingPositionService
from pydantic import BaseModel, field_validator

router = APIRouter()


class BatchDeleteRequest(BaseModel):
    """批量删除请求模型"""
    order_ids: list[int]


class QuickSellRequest(BaseModel):
    """快速卖出请求模型"""
    figure_id: int
    figure_name: str
    quantity: int
    sell_price: float
    cost_price: float

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('卖出数量必须大于0')
        return v

    @field_validator('sell_price')
    @classmethod
    def validate_sell_price(cls, v):
        if v <= 0:
            raise ValueError('卖出价格必须大于0')
        return v


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
def get_sold_orders(
    figure_name: str = None,
    order_number: str = None,
    sell_platform: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取已出售订单列表

    只返回未软删除的订单（is_active=1）

    查询参数：
    - figure_name: 手办名称模糊搜索
    - order_number: 订单编号模糊搜索
    - sell_platform: 卖出平台筛选
    """
    return SoldOrderService.get_sold_orders(db, current_user, figure_name, order_number, sell_platform)


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


@router.post("/quick-sell", response_model=SoldOrderSchema)
def quick_sell(request: QuickSellRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    快速卖出接口
    
    从持仓列表快速创建卖出订单，简化订单创建流程：
    1. 自动生成订单编号（QS + 时间戳）
    2. 默认使用"快速卖出"作为卖出平台
    3. 默认状态为"已完成"
    4. 自动联动更新：库存账、资金账、资产看板、手办状态
    
    Args:
        figure_id: 手办ID
        figure_name: 手办名称
        quantity: 卖出数量
        sell_price: 卖出单价
        cost_price: 成本单价
        
    Returns:
        创建的已出售订单对象
        
    Raises:
        HTTPException: 参数校验失败或创建失败
    """
    try:
        return QuickSellService.create_quick_sell_order(
            db=db,
            figure_id=request.figure_id,
            figure_name=request.figure_name,
            quantity=request.quantity,
            sell_price=request.sell_price,
            cost_price=request.cost_price,
            current_user=current_user
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"快速卖出失败: {str(e)}"
        )


@router.get("/figure-cost-price/{figure_id}/")
def get_figure_cost_price(
    figure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取手办的实际成本价

    基于库存账计算当前剩余持仓的实际平均成本，与持仓列表保持一致。
    用于添加已出售订单时自动填充成本价。

    计算逻辑：
    - 查询该手办所有买入记录（transaction_type='buy'）
    - 基于 remaining_quantity 和 price 计算加权平均成本
    - 平均成本 = 剩余总成本 / 剩余总数量

    Args:
        figure_id: 手办ID

    Returns:
        Dict: 包含成本价和库存数量
        - cost_price: 实际平均成本价（人民币）
        - stock: 当前库存数量
    """
    try:
        cost_price = HoldingPositionService.calculate_remaining_cost_price(
            db, figure_id, current_user.id
        )
        stock = HoldingPositionService.get_figure_inventory(
            db, figure_id, current_user.id
        )
        return {
            "cost_price": cost_price,
            "stock": stock
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取成本价失败: {str(e)}"
        )