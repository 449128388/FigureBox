"""
scraper_service.py - HPOI 抓取编排层（第六层防护：异常处理与降级）

整合所有 6 层防护，对外提供统一的抓取接口：
1. 浏览器引擎 -> 2. 代理池 -> 3. 限流器 -> 4. 缓存 -> 5. 解析器 -> 6. 异常降级
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from .rate_limiter import hpoi_limiter
from .proxy_pool import proxy_pool
from .browser_engine import BrowserEngine
from .cache_manager import CacheManager
from .html_parser import HpoiParser

logger = logging.getLogger(__name__)


class HpoiScraperService:
    """HPOI 抓取服务（整合六层防护）"""

    # 支持的域名
    SUPPORTED_DOMAINS = [
        "hpoi.net",
        "www.hpoi.net",
    ]

    @classmethod
    def is_supported(cls, url: str) -> bool:
        """判断 URL 是否支持"""
        from urllib.parse import urlparse
        try:
            host = urlparse(url).netloc.lower()
            return any(d in host for d in cls.SUPPORTED_DOMAINS)
        except Exception:
            return False

    @classmethod
    def scrape(cls, url: str, db: Session) -> Dict[str, Any]:
        """
        六层防护抓取入口

        Args:
            url: HPOI 商品详情页 URL
            db: 数据库会话（用于缓存）

        Returns:
            结构化手办数据

        Raises:
            ValueError: 参数错误
            RuntimeError: 抓取失败（所有降级措施均已尝试）
        """
        # === 第 0 步：URL 校验 ===
        if not url or not url.strip():
            raise ValueError("URL 不能为空")
        if not url.startswith("http"):
            raise ValueError("URL 格式错误，需以 http:// 或 https:// 开头")

        # === 第 4 步（优先检查）：缓存命中 ===
        cached = CacheManager.get(db, url)
        if cached and cached.get("parsed_data"):
            logger.info(f"[HPOI Scraper] 缓存命中: {url}")
            data = cached["parsed_data"]
            data["source_url"] = url
            data["_cache_hit"] = True
            return data

        # === 第 3 步：请求频率控制 ===
        if not hpoi_limiter.acquire(blocking=True, timeout=120):
            raise RuntimeError("请求过于频繁，请稍后再试")

        # === 第 2 步：选择代理 ===
        proxy = proxy_pool.get_random()
        if proxy:
            logger.info(f"[HPOI Scraper] 使用代理: {proxy.split('@')[0] if '@' in proxy else proxy[:20]}...")
        else:
            logger.info("[HPOI Scraper] 无可用代理，直连模式")

        # === 第 1 步 + 第 5 步 + 第 6 步：浏览器抓取 + 解析 + 异常处理 ===
        html = None
        parse_error = None

        # 尝试 1：有代理
        if proxy:
            try:
                html = cls._fetch_with_browser(url, proxy)
            except Exception as e:
                logger.warning(f"[HPOI Scraper] 代理抓取失败: {e}")
                html = None

        # 尝试 2：无代理（降级）
        if html is None:
            try:
                html = cls._fetch_with_browser(url)
            except Exception as e:
                logger.error(f"[HPOI Scraper] 直连抓取失败: {e}")
                raise RuntimeError(f"抓取失败: {e}")

        # === 第 5 步：解析 HTML ===
        try:
            parsed = HpoiParser.parse(html)
        except Exception as e:
            parse_error = str(e)
            logger.error(f"[HPOI Scraper] HTML 解析失败: {e}")
            # 降级：返回基础数据
            parsed = cls._fallback_parse(url)

        # === 写入缓存 ===
        try:
            CacheManager.set(db, url, html, parsed)
        except Exception as e:
            logger.warning(f"[HPOI Scraper] 缓存写入失败: {e}")

        parsed["source_url"] = url
        parsed["_cache_hit"] = False
        if parse_error:
            parsed["_parse_warning"] = parse_error

        return parsed

    @classmethod
    def _fetch_with_browser(cls, url: str, proxy: str = None) -> str:
        """使用 Playwright 浏览器引擎抓取页面"""
        engine = BrowserEngine.get_instance()
        return engine.fetch_page(url, proxy=proxy, timeout=30000)

    @classmethod
    def _fallback_parse(cls, url: str) -> Dict[str, Any]:
        """降级解析：提取 URL 中的 ID 和域名作为基本信息"""
        import re
        match = re.search(r"/hobby/(\d+)", url)
        item_id = match.group(1) if match else "unknown"
        return {
            "name": f"HPOI 手办 #{item_id}",
            "japanese_name": None,
            "manufacturer": None,
            "scale": None,
            "price": 0,
            "currency": "CNY",
            "release_date": None,
            "work": None,
            "material": None,
            "image": None,
            "_fallback": True,
        }
