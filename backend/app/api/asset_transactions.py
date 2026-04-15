"""
资产交易 API 路由
提供资产交易记录的增删改查接口
支持股票式补仓功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.models.database import get_db
from app.models.user import User
from app.services.asset_transaction_service import AssetTransactionService
from app.api.users import get_current_user

router = APIRouter(prefix="/asset-transactions", tags=["资产交易"])


# ============== 请求/响应模型 ==============

class TransactionCreateRequest(BaseModel):
    """创建交易记录请求"""
    figure_id: int = Field(..., description="手办ID")
    transaction_type: str = Field(..., description="交易类型: buy/sell")
    price: float = Field(..., gt=0, description="单价")
    quantity: int = Field(default=1, gt=0, description="数量")
    notes: Optional[str] = Field(None, description="备注")


class SellTransactionRequest(BaseModel):
    """卖出交易请求"""
    figure_id: int = Field(..., description="手办ID")
    price: float = Field(..., gt=0, description="卖出单价")
    quantity: int = Field(..., gt=0, description="卖出数量")
    notes: Optional[str] = Field(None, description="备注")


class TransactionResponse(BaseModel):
    """交易记录响应"""
    id: int
    figure_id: int
    order_id: Optional[int]
    transaction_type: str
    price: float
    quantity: int
    total_amount: float
    remaining_quantity: Optional[int]
    transaction_date: str
    notes: Optional[str]

    class Config:
        from_attributes = True


class AverageCostResponse(BaseModel):
    """平均成本响应"""
    figure_id: int
    average_cost: float
    total_quantity: int
    total_remaining: int
    total_cost: float


class ProfitResponse(BaseModel):
    """盈亏分析响应"""
    figure_id: int
    average_cost: float
    total_cost: float
    total_remaining: int
    total_sell_revenue: float
    total_sell_quantity: int
    realized_profit: float
    current_market_price: Optional[float] = None
    unrealized_profit: Optional[float] = None
    total_profit: Optional[float] = None


# ============== API 路由 ==============

@router.get("/figure/{figure_id}", response_model=List[TransactionResponse])
def get_figure_transactions(
    figure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定手办的所有交易记录
    """
    transactions = AssetTransactionService.get_transactions_by_figure(
        db, current_user.id, figure_id
    )
    return transactions


@router.get("/my", response_model=List[TransactionResponse])
def get_my_transactions(
    transaction_type: Optional[str] = Query(None, description="交易类型过滤: buy/sell"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有交易记录
    """
    transactions = AssetTransactionService.get_all_transactions(
        db, current_user.id, transaction_type, skip, limit
    )
    return transactions


@router.post("/buy", response_model=TransactionResponse)
def create_buy_transaction(
    request: TransactionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建买入交易记录（补仓）
    """
    if request.transaction_type != "buy":
        raise HTTPException(status_code=400, detail="交易类型必须是 buy")

    try:
        transaction = AssetTransactionService.create_transaction_from_figure(
            db=db,
            user_id=current_user.id,
            figure_id=request.figure_id,
            price=request.price,
            quantity=request.quantity
        )
        db.commit()
        return transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sell", response_model=TransactionResponse)
def create_sell_transaction(
    request: SellTransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建卖出交易记录
    """
    try:
        transaction = AssetTransactionService.create_sell_transaction(
            db=db,
            user_id=current_user.id,
            figure_id=request.figure_id,
            price=request.price,
            quantity=request.quantity,
            notes=request.notes
        )
        db.commit()
        return transaction
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/figure/{figure_id}/average-cost", response_model=AverageCostResponse)
def get_average_cost(
    figure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取手办的平均成本（补仓核心数据）
    """
    cost_info = AssetTransactionService.calculate_average_cost(
        db, current_user.id, figure_id
    )
    return {
        "figure_id": figure_id,
        **cost_info
    }


@router.get("/figure/{figure_id}/profit", response_model=ProfitResponse)
def get_profit_analysis(
    figure_id: int,
    current_market_price: Optional[float] = Query(None, description="当前市场价格"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取手办的盈亏分析
    """
    profit_info = AssetTransactionService.calculate_profit(
        db, current_user.id, figure_id, current_market_price
    )
    return {
        "figure_id": figure_id,
        **profit_info
    }


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除交易记录
    """
    success = AssetTransactionService.delete_transaction(
        db, transaction_id, current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="交易记录不存在")

    db.commit()
    return {"message": "删除成功"}
