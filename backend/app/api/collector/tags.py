"""
tags.py - 收藏家看板标签云接口

API端点：
- GET /collector/tags: 获取标签云数据（系统标签+用户标签）
- GET /collector/tags/figures?tag_name=xxx: 按标签筛选手办

职责：
- 展示分类标签（海景房、破发区、待补款、已出坑）
- 展示用户自定义标签
- 支持按标签筛选藏品
"""

from fastapi import APIRouter, Depends, Request, Response, Query, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.api.collector.dashboard import check_token_refresh
from app.services.dashboard_service.collector_service.collector_tag_service import CollectorTagService

router = APIRouter()


@router.get("/tags")
async def get_collector_tags(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收藏家看板标签云数据

    返回系统标签（自动计算）和用户标签（手动添加）：
    - system_tags: 海景房、破发区、待补款、已出坑
    - user_tags: 用户自定义标签（来自 figure_tag 中间表）
    """
    # 获取系统标签（自动计算）
    system_tags = CollectorTagService.get_system_tags(db, current_user.id)

    # 获取用户标签（手动添加）
    user_tags = CollectorTagService.get_user_tags(db, current_user.id)

    # 合并标签（前端区分展示）
    all_tags = system_tags + user_tags

    # 检查token续期
    check_token_refresh(request, response)

    return {
        "tags": all_tags,
        "system_tags": system_tags,
        "user_tags": user_tags
    }


@router.get("/tags/figures")
async def get_tag_filtered_figures(
    tag_name: str = Query(..., description="标签名称"),
    request: Request = None,
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    按标签筛选手办列表

    支持系统标签和用户标签：
    - 系统标签: 海景房、破发区、待补款、已出坑
    - 用户标签: figure_tag 中间表中用户手动添加的任意标签

    Args:
        tag_name: 标签名称

    Returns:
        { figures: list, tag_name: str, total: int }
    """
    figures = CollectorTagService.get_figures_by_tag(db, current_user.id, tag_name)

    if response:
        check_token_refresh(request, response)

    return {
        "figures": figures,
        "tag_name": tag_name,
        "total": len(figures)
    }

