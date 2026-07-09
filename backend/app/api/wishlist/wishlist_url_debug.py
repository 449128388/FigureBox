"""
wishlist_url_debug.py - raw_html 调试 API

提供查看缓存中原始 HTML 的调试能力。
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
import gzip

from app.api.users import get_current_user
from app.models.user import User
from app.models.database import get_db
from app.models.hpoi_cache import HpoiScrapeCache
from app.services.wishlist_service.hpoi_scraper.cache_manager import CacheManager

router = APIRouter()


class RawHtmlResponse:
    url_hash: str
    source_url: str
    raw_html_size: int
    raw_html: str
    parsed_data: dict


@router.get("/debug/raw-html")
def debug_raw_html(
    url: str = Query(..., description="原始抓取 URL"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    查看缓存中的原始 HTML（调试用）

    - 从 hpoi_scrape_cache 中按 URL 查找
    - 返回自动解压后的完整 HTML 和解析数据
    """
    if not url or not url.startswith("http"):
        raise HTTPException(status_code=400, detail="无效 URL，请输入完整的 https:// 链接")

    url_hash = CacheManager.url_to_hash(url)
    record = db.query(HpoiScrapeCache).filter(
        and_(
            HpoiScrapeCache.url_hash == url_hash,
        )
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail=f"未找到 URL 的缓存数据\n请先在愿望清单中使用「URL 智能抓取」")

    # 解压 raw_html
    try:
        raw_html_str = gzip.decompress(record.raw_html).decode("utf-8")
    except Exception:
        raw_html_str = str(record.raw_html)

    try:
        import json
        parsed = json.loads(record.parsed_data) if record.parsed_data else {}
    except Exception:
        parsed = {}

    return {
        "url_hash": record.url_hash,
        "source_url": record.source_url,
        "raw_html_size": len(raw_html_str),
        "raw_html": raw_html_str,
        "parsed_data": parsed,
        "created_at": str(record.created_at) if record.created_at else None,
        "expires_at": str(record.expires_at) if record.expires_at else None,
    }
