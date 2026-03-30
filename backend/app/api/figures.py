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

# 入手形式映射表：英文大写 -> 中文
PURCHASE_TYPE_MAP = {
    "OTHER": "其他",
    "PREORDER": "预定",
    "INSTOCK": "现货",
    "SECONDHAND": "二手",
    "LOOSE": "散货",
    "DOMESTIC": "国产"
}

# 反向映射表：中文 -> 英文大写
PURCHASE_TYPE_REVERSE_MAP = {v: k for k, v in PURCHASE_TYPE_MAP.items()}

@router.get("/", response_model=list[FigureSchema])
def get_figures(
    skip: int = 0,
    limit: int = 100,
    name: str = None,
    purchase_type: str = None,
    purchase_date_start: str = None,
    purchase_date_end: str = None,
    db: Session = Depends(get_db)
):
    """
    获取手办列表，支持搜索过滤
    """
    query = db.query(Figure)
    
    # 按名称搜索（模糊匹配）
    if name:
        query = query.filter(Figure.name.ilike(f"%{name}%"))
    
    # 按入手形式过滤
    if purchase_type:
        # 将英文大写参数转换为中文进行查询
        chinese_purchase_type = PURCHASE_TYPE_MAP.get(purchase_type.upper(), purchase_type)
        query = query.filter(Figure.purchase_type == chinese_purchase_type)
    
    # 按入手日期范围过滤
    if purchase_date_start:
        try:
            start_date = datetime.strptime(purchase_date_start, "%Y-%m-%d").date()
            query = query.filter(Figure.purchase_date >= start_date)
        except ValueError:
            pass
    
    if purchase_date_end:
        try:
            end_date = datetime.strptime(purchase_date_end, "%Y-%m-%d").date()
            query = query.filter(Figure.purchase_date <= end_date)
        except ValueError:
            pass
    
    # 按 id 降序排序（最新的在前面）
    query = query.order_by(Figure.id.desc())
    
    figures = query.offset(skip).limit(limit).all()
    return figures

def json_serial(obj):
    """JSON 序列化辅助函数，处理日期类型"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

@router.get("/download")
def download_figures(db: Session = Depends(get_db)):
    """
    下载所有手办数据及关联的尾款数据为 JSON 格式
    """
    try:
        # 导入 Order 模型
        from app.models.order import Order
        
        # 获取所有手办数据
        figures = db.query(Figure).all()
        
        # 转换为字典列表
        figures_data = []
        for figure in figures:
            # 获取该手办关联的尾款订单
            orders = db.query(Order).filter(Order.figure_id == figure.id).all()
            orders_data = []
            for order in orders:
                order_dict = {
                    "id": order.id,
                    "figure_id": order.figure_id,
                    "deposit": order.deposit,
                    "balance": order.balance,
                    "due_date": order.due_date.isoformat() if order.due_date else None,
                    "status": order.status,
                    "shop_name": order.shop_name,
                    "shop_contact": order.shop_contact,
                    "tracking_number": order.tracking_number
                }
                orders_data.append(order_dict)
            
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
                "images": figure.images,
                "orders": orders_data  # 添加关联的尾款数据
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
    figure_data = figure.model_dump()
    
    # 将入手形式的英文转换为中文
    if figure_data.get('purchase_type'):
        figure_data['purchase_type'] = PURCHASE_TYPE_MAP.get(
            figure_data['purchase_type'].upper(), 
            figure_data['purchase_type']
        )
    
    db_figure = Figure(**figure_data)
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
    
    figure_data = figure.model_dump(exclude_unset=True)
    
    # 将入手形式的英文转换为中文
    if 'purchase_type' in figure_data and figure_data['purchase_type']:
        figure_data['purchase_type'] = PURCHASE_TYPE_MAP.get(
            figure_data['purchase_type'].upper(), 
            figure_data['purchase_type']
        )
    
    for key, value in figure_data.items():
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
