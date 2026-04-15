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
    """
    figure = FigureService.get_figure_by_id(db, figure_id)
    if not figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )
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
    """
    figure_data = figure.model_dump(exclude_unset=True)
    db_figure = FigureService.update_figure(db, figure_id, figure_data)
    
    if not db_figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )
    
    return db_figure


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
