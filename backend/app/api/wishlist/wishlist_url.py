"""
wishlist_url.py - URL 智能抓取 API

HPOI 链接使用六层防护引擎（Playwright 浏览器模拟 + 代理池 + 限流 + 缓存 + 解析 + 降级）
其他站点使用模板模拟数据。
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.users import get_current_user
from app.models.user import User
from app.models.database import get_db
from app.services import WishlistUrlFetchService

router = APIRouter()


class UrlFetchRequest(BaseModel):
    url: str


@router.post("/url-fetch")
def url_fetch(
    payload: UrlFetchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    URL 智能抓取

    HPOI 链接：通过 Playwright 浏览器引擎真实抓取（六层防护）
    其他站点：使用模板模拟
    """
    try:
        return WishlistUrlFetchService.parse_url(payload.url, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
