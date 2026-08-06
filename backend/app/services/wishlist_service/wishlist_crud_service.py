"""
wishlist_crud_service - 愿望清单 CRUD 服务

提供创建/更新/删除/状态流转/转入手办库能力：
- create_wishlist：创建愿望
- update_wishlist：更新愿望
- delete_wishlist：软删除
- change_status：状态流转
- move_to_library：转入手办库（修改 purchase_type）
"""
from typing import Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.figure import Figure
from .wishlist_query_service import STATUS_MAP, PURCHASE_TYPE


class WishlistCrudService:
    """愿望清单 CRUD 服务"""

    @staticmethod
    def create_wishlist(
        db: Session,
        user_id: int,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        创建愿望清单项

        Args:
            data: 包含 name/japanese_name/price/currency/manufacturer/scale/...
                  release_date/source_url/note/tags/images/wishlist_status
        """
        # 2026-08-05 修复：强制 user_id 非 NULL 校验，防止任何调用路径漏传导致无主数据
        if user_id is None:
            raise HTTPException(status_code=401, detail="缺少用户上下文")

        # 必填校验
        if not data.get("name"):
            raise HTTPException(status_code=400, detail="手办名称不能为空")

        # 状态校验
        status = data.get("wishlist_status", "wish")
        if status not in STATUS_MAP:
            status = "wish"

        # 解析日期
        release_date = data.get("release_date")
        if isinstance(release_date, str):
            try:
                release_date = date.fromisoformat(release_date)
            except ValueError:
                release_date = None

        # 解析 images
        images = data.get("images") or []
        if isinstance(images, str):
            images = [img.strip() for img in images.split(",") if img.strip()]

        figure = Figure(
            name=data["name"],
            japanese_name=data.get("japanese_name"),
            manufacturer=data.get("manufacturer"),
            scale=data.get("scale"),
            painting=data.get("painting"),
            original_art=data.get("original_art"),
            work=data.get("work"),
            material=data.get("material"),
            size=data.get("size"),
            price=data.get("price", 0) or 0,
            currency=data.get("currency", "CNY") or "CNY",
            market_price=data.get("market_price", 0) or 0,
            market_currency=data.get("market_currency", "CNY") or "CNY",
            release_date=release_date,
            purchase_type=PURCHASE_TYPE,
            wishlist_status=status,
            source_url=data.get("source_url"),
            note=data.get("note"),
            images=images,
            quantity=1,
            is_active=1,
            user_id=user_id,  # 2026-08-05 修复：写入所有者，否则愿望清单项为 NULL 无主数据
        )

        db.add(figure)
        db.flush()

        # 2026-07-29 重构：标签直接使用 figure.tags JSON 字段
        tag_names = data.get("tag_names") or data.get("tags") or []
        if isinstance(tag_names, str):
            tag_names = [t.strip() for t in tag_names.split() if t.strip()]
        # 去重
        tag_names = list(dict.fromkeys([t for t in tag_names if t]))
        figure.tags = tag_names

        db.commit()
        db.refresh(figure)
        return figure

    @staticmethod
    def update_wishlist(
        db: Session,
        user_id: int,
        figure_id: int,
        data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        更新愿望清单项
        """
        figure = db.query(Figure).filter(
            Figure.id == figure_id,
            Figure.purchase_type == PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,  # 2026-08-05 修复：所有权校验，防止越权更新他人愿望
        ).first()
        if not figure:
            return None

        # 字段更新（白名单）
        field_map = {
            "name": "name",
            "japanese_name": "japanese_name",
            "manufacturer": "manufacturer",
            "scale": "scale",
            "painting": "painting",
            "original_art": "original_art",
            "work": "work",
            "material": "material",
            "size": "size",
            "price": "price",
            "currency": "currency",
            "market_price": "market_price",
            "market_currency": "market_currency",
            "source_url": "source_url",
            "note": "note",
        }
        for k, attr in field_map.items():
            if k in data and data[k] is not None:
                setattr(figure, attr, data[k])

        # 状态更新
        if "wishlist_status" in data:
            status = data["wishlist_status"]
            if status in STATUS_MAP:
                figure.wishlist_status = status

        # 发行日期
        if "release_date" in data:
            rd = data["release_date"]
            if isinstance(rd, str):
                try:
                    rd = date.fromisoformat(rd)
                except ValueError:
                    rd = None
            figure.release_date = rd

        # 图片
        if "images" in data:
            imgs = data["images"]
            if isinstance(imgs, str):
                imgs = [i.strip() for i in imgs.split(",") if i.strip()]
            figure.images = imgs

        # 标签
        if "tag_names" in data or "tags" in data:
            tag_names = data.get("tag_names") or data.get("tags") or []
            if isinstance(tag_names, str):
                tag_names = [t.strip() for t in tag_names.split() if t.strip()]
            # 2026-07-29 重构：直接覆盖 figure.tags JSON 字段
            figure.tags = list(dict.fromkeys([t for t in tag_names if t]))

        db.commit()
        db.refresh(figure)
        return figure

    @staticmethod
    def delete_wishlist(
        db: Session,
        user_id: int,
        figure_id: int,
    ) -> bool:
        """软删除愿望清单项"""
        figure = db.query(Figure).filter(
            Figure.id == figure_id,
            Figure.purchase_type == PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,  # 2026-08-05 修复：所有权校验，防止越权删除他人愿望
        ).first()
        if not figure:
            return False
        figure.is_active = 0
        db.commit()
        return True

    @staticmethod
    def change_status(
        db: Session,
        user_id: int,
        figure_id: int,
        new_status: str,
    ) -> Optional[Dict[str, Any]]:
        """状态流转"""
        if new_status not in STATUS_MAP:
            raise HTTPException(status_code=400, detail=f"无效状态: {new_status}")
        return WishlistCrudService.update_wishlist(
            db, user_id, figure_id, {"wishlist_status": new_status}
        )

    @staticmethod
    def move_to_library(
        db: Session,
        user_id: int,
        figure_id: int,
        purchase_type: str = "preorder",
    ) -> Optional[Dict[str, Any]]:
        """
        转入手办库
        修改 purchase_type 字段，清空 wishlist_status（标记为非愿望清单）
        """
        if purchase_type not in ("preorder", "spot", "secondhand"):
            raise HTTPException(status_code=400, detail="无效的转库类型")
        figure = db.query(Figure).filter(
            Figure.id == figure_id,
            Figure.purchase_type == PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,  # 2026-08-05 修复：所有权校验，防止越权转库他人愿望
        ).first()
        if not figure:
            return None
        # 映射为数据库标准大写值（与 PURCHASE_TYPE_MAP 一致）
        type_mapping = {
            "preorder": "PREORDER",
            "spot": "INSTOCK",
            "secondhand": "SECONDHAND",
        }
        figure.purchase_type = type_mapping.get(purchase_type, purchase_type.upper())
        figure.wishlist_status = None
        db.commit()
        db.refresh(figure)
        return figure
