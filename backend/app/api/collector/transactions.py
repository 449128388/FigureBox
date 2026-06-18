"""
transactions.py - 收藏家模式收藏历程接口

API端点：
- GET /collector/figures/{figure_id}/transactions: 获取手办全生命周期资产变动流水

职责：
- 返回某个手办下所有入库/出库记录的完整流水
- 按时间倒序排列，包含交易类型、数量、单价、库存结余
"""

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.models.figure import Figure
from app.api.users import get_current_user
from app.services.collector_service.collector_transaction_service import CollectorTransactionService

router = APIRouter()


@router.get("/figures/{figure_id}/transactions")
async def get_figure_transactions(
    request: Request,
    response: Response,
    figure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取手办收藏历程（全生命周期资产变动流水）

    参数：
    - figure_id: 手办ID

    返回：
    - transactions: 交易流水列表（按日期倒序）
    """
    # 验证手办存在
    figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not figure:
        raise HTTPException(status_code=404, detail="手办不存在")

    transactions = CollectorTransactionService.get_figure_transactions(
        db, current_user.id, figure_id
    )

    return {
        "transactions": transactions
    }
