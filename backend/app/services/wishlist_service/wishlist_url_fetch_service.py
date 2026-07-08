"""
wishlist_url_fetch_service - URL 智能抓取服务

支持 HPOI 站点的六层防护抓取引擎，以及 Amiami/MFC 的模板模拟。
HPOI 使用 Playwright + Chromium 真实浏览器抓取，其他站点暂用模拟数据。
"""
import re
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from sqlalchemy.orm import Session

from .hpoi_scraper import HpoiScraperService

logger = logging.getLogger(__name__)

# Amiami / MFC 模拟数据模板
MOCK_TEMPLATES = {
    "amiami.com": {
        "name": "蜜姬 标准版",
        "japanese_name": "ミツキ 標準版",
        "manufacturer": "Alter",
        "scale": "1/7",
        "price": 16500,
        "currency": "JPY",
        "market_price": 0,
        "market_currency": "CNY",
        "release_date": "2026-08-20",
        "work": "原创",
        "material": "PVC",
        "image": "https://img.amiami.com/images/model/p/figure/116383.jpg",
    },
    "myfigurecollection.net": {
        "name": "测试数据1号",
        "japanese_name": "テストデータ1号",
        "manufacturer": "GSC",
        "scale": "1/8",
        "price": 12000,
        "currency": "JPY",
        "market_price": 0,
        "market_currency": "CNY",
        "release_date": "2026-12-01",
        "work": "原创",
        "material": "PVC",
        "image": "https://static.myfigurecollection.net/upload/figures/116383.jpg",
    },
}

DEFAULT_TEMPLATE = {
    "name": "未知手办",
    "japanese_name": None,
    "manufacturer": "Unknown",
    "scale": "1/7",
    "price": 1000,
    "currency": "CNY",
    "market_price": 0,
    "market_currency": "CNY",
    "release_date": "2026-09-01",
    "work": None,
    "material": "PVC",
    "image": "https://placehold.co/300x300?text=Wishlist",
}


class WishlistUrlFetchService:
    """URL 智能抓取服务"""

    @staticmethod
    def parse_url(url: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        解析 URL，返回结构化手办数据

        HPOI 链接：通过 Playwright 浏览器引擎真实抓取（六层防护）
        其他站点：使用模拟数据

        Args:
            url: 商品详情页 URL
            db: 数据库会话（用于 HPOI 缓存）

        Returns:
            {
                "source_url": 原URL,
                "source_domain": 域名,
                "name": 手办名称,
                "japanese_name": 日文名,
                ...
            }
        """
        if not url or not url.strip():
            raise ValueError("URL 不能为空")

        if not re.match(r'^https?://', url):
            raise ValueError("URL 格式错误，需以 http:// 或 https:// 开头")

        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower()
        except Exception:
            raise ValueError("URL 解析失败")

        # === HPOI：使用六层防护引擎 ===
        if HpoiScraperService.is_supported(url):
            try:
                if db is not None:
                    data = HpoiScraperService.scrape(url, db)
                    data["source_domain"] = host
                    return data
                else:
                    logger.warning("[URL Fetch] HPOI 需要数据库会话，降级为模拟数据")
            except Exception as e:
                logger.error(f"[URL Fetch] HPOI 抓取失败: {e}")
                # 降级到模拟数据
                pass

        # === 其他站点：模板模拟 ===
        template = DEFAULT_TEMPLATE.copy()
        for domain, tpl in MOCK_TEMPLATES.items():
            if domain in host:
                template = tpl.copy()
                break

        return {
            "source_url": url,
            "source_domain": host,
            **template,
        }
