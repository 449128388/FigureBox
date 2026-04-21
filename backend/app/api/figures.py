from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from fastapi.responses import Response
from datetime import datetime
from typing import List, Dict, Any

from app.models.database import get_db
from app.models.figure import Figure
from app.schemas.figure import (
    Figure as FigureSchema, FigureCreate, FigureUpdate, 
    Tag as TagSchema, TagCreate, FigureListItem
)
from app.api.users import get_current_user
from app.models.user import User

# 引入服务层
from app.services import FigureService, TagService, FigureExportService, FigureImportService
from app.services.asset_transaction_service import AssetTransactionService
from app.services.order_transaction_service import OrderTransactionService

router = APIRouter()


@router.get("/", response_model=list[FigureListItem])
def get_figures(
    skip: int = 0,
    limit: int = 100,
    name: str = None,
    purchase_type: str = None,
    purchase_date_start: str = None,
    purchase_date_end: str = None,
    tag_id: int = None,
    tag_ids: list[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取手办列表，支持搜索过滤（使用精简响应模型减少数据传输）
    """
    return FigureService.get_figures_list(
        db=db,
        skip=skip,
        limit=limit,
        name=name,
        purchase_type=purchase_type,
        purchase_date_start=purchase_date_start,
        purchase_date_end=purchase_date_end,
        tag_id=tag_id,
        tag_ids=tag_ids
    )


@router.get("/download")
def download_figures(db: Session = Depends(get_db)):
    """
    下载所有手办数据及关联的尾款数据为 JSON 格式
    """
    try:
        # 使用服务层导出数据
        json_data = FigureExportService.export_all_figures(db)
        filename = FigureExportService.get_export_filename()
        
        # 返回 JSON 响应
        return Response(
            content=json_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载数据失败: {str(e)}"
        )


# ========== 标签管理接口（必须放在 /{figure_id} 路由之前）==========

@router.get("/tags", response_model=list[TagSchema])
def get_tags(db: Session = Depends(get_db)):
    """
    获取所有标签
    """
    return TagService.get_all_tags(db)


@router.post("/tags", response_model=TagSchema)
def create_tag(
    tag: TagCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    创建新标签
    """
    try:
        return TagService.create_tag(db, tag.name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/tags/{tag_id}", response_model=TagSchema)
def update_tag(
    tag_id: int, 
    tag: TagCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    更新标签
    """
    try:
        db_tag = TagService.update_tag(db, tag_id, tag.name)
        if not db_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="标签不存在"
            )
        return db_tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    删除标签
    """
    success = TagService.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    return {"message": "标签删除成功"}


# ========== 手办CRUD接口 ==========

@router.get("/{figure_id}", response_model=FigureSchema)
@router.get("/{figure_id}/", response_model=FigureSchema)
def get_figure(figure_id: int, db: Session = Depends(get_db)):
    """
    获取手办详情

    返回的手办数据包含：
    - 基础信息（名称、定价等）
    - 平均入手价格（根据关联订单自动计算）
    """
    figure = FigureService.get_figure_by_id(db, figure_id)
    if not figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )

    # 【优化】加载关联的订单并计算平均入手价格
    from sqlalchemy.orm import joinedload
    figure_with_orders = db.query(Figure).options(
        joinedload(Figure.orders)
    ).filter(Figure.id == figure_id).first()

    if figure_with_orders:
        # 【重构】使用服务层方法计算平均入手价格
        avg_price = FigureService.calculate_figure_average_purchase_price(figure_with_orders)
        # 将计算结果添加到返回数据中
        figure.average_purchase_price = avg_price

    return figure


@router.post("/", response_model=FigureSchema)
def create_figure(
    figure: FigureCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    创建手办
    
    创建手办时会自动创建对应的资产交易记录（买入类型）
    """
    figure_data = figure.model_dump()
    return FigureService.create_figure(db, figure_data, user_id=current_user.id)


@router.put("/{figure_id}", response_model=FigureSchema)
def update_figure(
    figure_id: int,
    figure: FigureUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新手办

    支持冲正交易：
    - 修改数量（增加）：创建补录买入交易
    - 修改数量（减少）：创建冲正交易
    - 修改入手价格：创建价格调整记录
    """
    figure_data = figure.model_dump(exclude_unset=True)

    # 获取原始手办数据（用于冲正计算）
    original_figure = FigureService.get_figure_by_id(db, figure_id)
    if not original_figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )

    original_quantity = original_figure.quantity or 1
    original_price = original_figure.average_purchase_price or 0

    # 更新手办
    db_figure = FigureService.update_figure(db, figure_id, figure_data)

    if not db_figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )

    # 处理冲正交易
    try:
        # 检查数量变化
        new_quantity = db_figure.quantity or 1
        if 'quantity' in figure_data and new_quantity != original_quantity:
            quantity_change = new_quantity - original_quantity
            # 使用当前入手价格作为冲正价格
            adjustment_price = db_figure.average_purchase_price or original_price or 0

            # 【修复】无论价格是否为0，都创建资产交易记录（库存账）
            # 数量调整属于库存变动，必须记录以保证库存数据完整性
            AssetTransactionService.create_quantity_adjustment_transaction(
                db=db,
                user_id=current_user.id,
                figure_id=figure_id,
                quantity_change=quantity_change,
                price=adjustment_price,
                original_quantity=original_quantity,
                new_quantity=new_quantity
            )
            db.commit()

        # 检查价格变化（数量未变化时）

    except Exception as e:
        # 冲正交易失败不影响手办更新
        db.rollback()
        print(f"创建冲正交易记录失败: {e}")

    return db_figure


@router.get("/{figure_id}/orders/count")
def get_figure_orders_count(
    figure_id: int,
    db: Session = Depends(get_db)
):
    """
    获取手办关联的未软删除订单数量

    用于删除确认对话框显示关联订单信息
    只统计 is_active=1 的订单（未软删除）
    """
    from app.models.order import Order

    # 查询该手办的未软删除订单数量
    order_count = db.query(Order).filter(
        Order.figure_id == figure_id,
        Order.is_active == 1
    ).count()

    return {
        "figure_id": figure_id,
        "count": order_count
    }


@router.delete("/{figure_id}")
def delete_figure(
    figure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除手办
    """
    try:
        success = FigureService.delete_figure(db, figure_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Figure not found"
            )
        return {"message": "Figure deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/import")
def import_figures(
    data: Dict[str, List[Dict[str, Any]]],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从JSON数据导入手办和订单
    """
    try:
        figures_data = data.get('figures', [])
        if not figures_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供要导入的数据"
            )
        
        result = FigureImportService.import_figures_from_json(
            db=db,
            json_data=figures_data,
            user_id=current_user.id
        )
        
        return {
            "success": result['success'],
            "imported_count": result['imported_figures'],
            "updated_count": result['updated_figures'],
            "orders_count": result['imported_orders'],
            "message": f"成功导入 {result['imported_figures']} 个新手办，更新 {result['updated_figures']} 个手办，导入 {result['imported_orders']} 个订单",
            "errors": result['errors']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入失败: {str(e)}"
        )
