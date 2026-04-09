"""
标签服务
提供标签相关的业务逻辑，包括增删改查等
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.models.tag import Tag
from app.schemas.figure import TagCreate


class TagService:
    """标签服务类"""
    
    @staticmethod
    def get_all_tags(db: Session) -> List[Tag]:
        """
        获取所有标签（按名称升序排序）
        
        Args:
            db: 数据库会话
            
        Returns:
            List[Tag]: 标签列表
        """
        return db.query(Tag).order_by(asc(Tag.name)).all()
    
    @staticmethod
    def get_tag_by_id(db: Session, tag_id: int) -> Optional[Tag]:
        """
        根据ID获取标签
        
        Args:
            db: 数据库会话
            tag_id: 标签ID
            
        Returns:
            Tag对象或None
        """
        return db.query(Tag).filter(Tag.id == tag_id).first()
    
    @staticmethod
    def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
        """
        根据名称获取标签
        
        Args:
            db: 数据库会话
            name: 标签名称
            
        Returns:
            Tag对象或None
        """
        return db.query(Tag).filter(Tag.name == name).first()
    
    @staticmethod
    def create_tag(db: Session, tag_name: str) -> Tag:
        """
        创建新标签
        
        Args:
            db: 数据库会话
            tag_name: 标签名称
            
        Returns:
            创建的Tag对象
            
        Raises:
            ValueError: 标签已存在时抛出
        """
        # 检查标签是否已存在
        existing_tag = TagService.get_tag_by_name(db, tag_name)
        if existing_tag:
            raise ValueError("标签已存在")
        
        db_tag = Tag(name=tag_name)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag
    
    @staticmethod
    def update_tag(db: Session, tag_id: int, new_name: str) -> Optional[Tag]:
        """
        更新标签
        
        Args:
            db: 数据库会话
            tag_id: 标签ID
            new_name: 新标签名称
            
        Returns:
            更新后的Tag对象或None（不存在时）
            
        Raises:
            ValueError: 新名称已被其他标签使用时抛出
        """
        db_tag = TagService.get_tag_by_id(db, tag_id)
        if not db_tag:
            return None
        
        # 检查新名称是否已被其他标签使用
        existing_tag = db.query(Tag).filter(
            Tag.name == new_name,
            Tag.id != tag_id
        ).first()
        
        if existing_tag:
            raise ValueError("标签名称已存在")
        
        db_tag.name = new_name
        db.commit()
        db.refresh(db_tag)
        return db_tag
    
    @staticmethod
    def delete_tag(db: Session, tag_id: int) -> bool:
        """
        删除标签
        
        Args:
            db: 数据库会话
            tag_id: 标签ID
            
        Returns:
            bool: 是否删除成功
        """
        db_tag = TagService.get_tag_by_id(db, tag_id)
        if not db_tag:
            return False
        
        db.delete(db_tag)
        db.commit()
        return True
