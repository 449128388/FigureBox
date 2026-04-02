from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from app.models.database import get_db
from app.models.figure import Figure
from app.models.tag import Tag, figure_tag
from app.schemas.figure import Figure as FigureSchema, FigureCreate, FigureUpdate, Tag as TagSchema, TagCreate, FigureListItem
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

    # 按标签ID筛选（单个标签）
    if tag_id:
        # 先执行子查询获取包含指定标签的手办ID列表
        # 避免在主查询中使用子查询导致的排序内存问题
        figure_ids = db.query(figure_tag.c.figure_id).filter(figure_tag.c.tag_id == tag_id).all()
        # 提取ID值
        figure_id_list = [id_tuple[0] for id_tuple in figure_ids]
        # 如果没有符合条件的手办，直接返回空列表
        if not figure_id_list:
            return []
        # 然后根据ID列表筛选
        query = query.filter(Figure.id.in_(figure_id_list))
    
    # 按标签ID列表筛选（多标签联合筛选）
    if tag_ids and len(tag_ids) > 0:
        # 对每个标签ID进行筛选
        for tag_id in tag_ids:
            # 先执行子查询获取包含当前标签的手办ID列表
            figure_ids = db.query(figure_tag.c.figure_id).filter(figure_tag.c.tag_id == tag_id).all()
            # 提取ID值
            figure_id_list = [id_tuple[0] for id_tuple in figure_ids]
            # 如果没有符合条件的手办，直接返回空列表
            if not figure_id_list:
                return []
            # 然后根据ID列表筛选
            query = query.filter(Figure.id.in_(figure_id_list))

    # 按 id 降序排序（最新的在前面）
    query = query.order_by(Figure.id.desc())

    # 使用 selectinload 预加载标签数据，避免 N+1 查询问题和排序内存问题
    query = query.options(selectinload(Figure.tags))

    figures = query.offset(skip).limit(limit).all()
    
    # 转换为精简响应模型，只返回第一张图片
    result = []
    for figure in figures:
        item = FigureListItem(
            id=figure.id,
            name=figure.name,
            japanese_name=figure.japanese_name,
            price=figure.price,
            currency=figure.currency,
            manufacturer=figure.manufacturer,
            release_date=figure.release_date,
            purchase_price=figure.purchase_price,
            purchase_currency=figure.purchase_currency,
            purchase_date=figure.purchase_date,
            purchase_method=figure.purchase_method,
            purchase_type=figure.purchase_type,
            quantity=figure.quantity,
            scale=figure.scale,
            painting=figure.painting,
            original_art=figure.original_art,
            work=figure.work,
            material=figure.material,
            size=figure.size,
            description=figure.description,
            # 只返回第一张图片，减少数据量
            image=figure.images[0] if figure.images and len(figure.images) > 0 else None,
            tags=figure.tags
        )
        result.append(item)
    
    return result

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
            
            # 转换标签对象为可序列化的字典列表
            tags_data = []
            for tag in figure.tags:
                tag_dict = {
                    "id": tag.id,
                    "name": tag.name
                }
                tags_data.append(tag_dict)
            
            figure_dict = {
                "id": figure.id,
                "name": figure.name,
                "japanese_name": figure.japanese_name,
                "manufacturer": figure.manufacturer,
                "price": figure.price,
                "currency": figure.currency,
                "tags": tags_data,
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

# ========== 标签管理接口（必须放在 /{figure_id} 路由之前）==========

@router.get("/tags", response_model=list[TagSchema])
def get_tags(db: Session = Depends(get_db)):
    """
    获取所有标签
    """
    tags = db.query(Tag).order_by(Tag.name).all()
    return tags


@router.post("/tags", response_model=TagSchema)
def create_tag(tag: TagCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    创建新标签
    """
    # 检查标签是否已存在
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签已存在"
        )

    db_tag = Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.put("/tags/{tag_id}", response_model=TagSchema)
def update_tag(tag_id: int, tag: TagCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    更新标签
    """
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    # 检查新名称是否已被其他标签使用
    existing_tag = db.query(Tag).filter(Tag.name == tag.name, Tag.id != tag_id).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签名称已存在"
        )

    db_tag.name = tag.name
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    删除标签
    """
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    db.delete(db_tag)
    db.commit()
    return {"message": "标签删除成功"}


@router.get("/{figure_id}", response_model=FigureSchema)
@router.get("/{figure_id}/", response_model=FigureSchema)
def get_figure(figure_id: int, db: Session = Depends(get_db)):
    figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )
    return figure

@router.post("/", response_model=FigureSchema)
def create_figure(figure: FigureCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    figure_data = figure.model_dump()

    # 提取标签ID列表
    tag_ids = figure_data.pop('tag_ids', [])

    # 将入手形式的英文转换为中文
    if figure_data.get('purchase_type'):
        figure_data['purchase_type'] = PURCHASE_TYPE_MAP.get(
            figure_data['purchase_type'].upper(),
            figure_data['purchase_type']
        )

    # 创建手办对象
    db_figure = Figure(**figure_data)
    db.add(db_figure)
    db.commit()
    db.refresh(db_figure)

    # 关联标签
    if tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        db_figure.tags = tags
        db.commit()
        db.refresh(db_figure)

    return db_figure

@router.put("/{figure_id}", response_model=FigureSchema)
def update_figure(figure_id: int, figure: FigureUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not db_figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )

    figure_data = figure.model_dump(exclude_unset=True)

    # 提取标签ID列表
    tag_ids = figure_data.pop('tag_ids', None)

    # 将入手形式的英文转换为中文
    if 'purchase_type' in figure_data and figure_data['purchase_type']:
        figure_data['purchase_type'] = PURCHASE_TYPE_MAP.get(
            figure_data['purchase_type'].upper(),
            figure_data['purchase_type']
        )

    # 更新其他字段
    for key, value in figure_data.items():
        setattr(db_figure, key, value)

    # 更新标签关联
    if tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        db_figure.tags = tags

    db.commit()
    db.refresh(db_figure)
    return db_figure

@router.delete("/{figure_id}")
def delete_figure(figure_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
