from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.figure import Figure
from app.schemas.figure import Figure as FigureSchema, FigureCreate, FigureUpdate
from app.api.users import get_current_user
from app.models.user import User
from fastapi.responses import Response
import json
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[FigureSchema])
def get_figures(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    figures = db.query(Figure).offset(skip).limit(limit).all()
    return figures

def json_serial(obj):
    """JSON 序列化辅助函数，处理日期类型"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

@router.get("/download")
def download_figures(db: Session = Depends(get_db)):
    """
    下载所有手办数据为 JSON 格式
    """
    try:
        # 获取所有手办数据
        figures = db.query(Figure).all()
        
        # 转换为字典列表
        figures_data = []
        for figure in figures:
            figure_dict = {
                "id": figure.id,
                "name": figure.name,
                "japanese_name": figure.japanese_name,
                "manufacturer": figure.manufacturer,
                "price": figure.price,
                "currency": figure.currency,
                "tags": figure.tags,
                "release_date": figure.release_date.isoformat() if figure.release_date else None,
                "purchase_price": figure.purchase_price,
                "purchase_currency": figure.purchase_currency,
                "purchase_date": figure.purchase_date.isoformat() if figure.purchase_date else None,
                "purchase_method": figure.purchase_method,
                "purchase_type": figure.purchase_type,
                "scale": figure.scale,
                "painting": figure.painting,
                "original_art": figure.original_art,
                "work": figure.work,
                "material": figure.material,
                "size": figure.size,
                "images": figure.images
            }
            figures_data.append(figure_dict)
        
        # 转换为 JSON 字符串
        json_data = json.dumps(figures_data, ensure_ascii=False, indent=2, default=json_serial)
        
        # 返回 JSON 响应
        return Response(
            content=json_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=figures_{datetime.utcnow().strftime('%Y-%m-%d')}.json"
            }
        )
    except Exception as e:
        import traceback
        print(f"下载数据时发生错误: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载数据失败: {str(e)}"
        )

@router.get("/{figure_id}", response_model=FigureSchema)
def get_figure(figure_id: int, db: Session = Depends(get_db)):
    figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )
    return figure

@router.post("/", response_model=FigureSchema)
def create_figure(figure: FigureCreate, db: Session = Depends(get_db)):
    db_figure = Figure(**figure.model_dump())
    db.add(db_figure)
    db.commit()
    db.refresh(db_figure)
    return db_figure

@router.put("/{figure_id}", response_model=FigureSchema)
def update_figure(figure_id: int, figure: FigureUpdate, db: Session = Depends(get_db)):
    db_figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not db_figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )
    for key, value in figure.model_dump(exclude_unset=True).items():
        setattr(db_figure, key, value)
    db.commit()
    db.refresh(db_figure)
    return db_figure

@router.delete("/{figure_id}")
def delete_figure(figure_id: int, db: Session = Depends(get_db)):
    db_figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not db_figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )
    
    # 检查是否有关联的订单
    from app.models.order import Order
    associated_orders = db.query(Order).filter(Order.figure_id == figure_id).first()
    if associated_orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法删除有关联尾款的手办"
        )
    
    db.delete(db_figure)
    db.commit()
    return {"message": "Figure deleted successfully"}
