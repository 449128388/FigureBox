"""
hpoi_scraper - HPOI 多层防护抓取引擎

六层防护：
1. 浏览器级模拟（Playwright + Chromium）
2. 智能代理池（IP 轮换）
3. 请求频率控制（令牌桶）
4. 多级缓存（MySQL + 30 天有效期）
5. 数据解析（HPOI 页面结构）
6. 异常处理与降级
"""

from .scraper_service import HpoiScraperService
from .browser_engine import BrowserEngine
from .proxy_pool import ProxyPool
from .rate_limiter import RateLimiter
from .cache_manager import CacheManager
from .html_parser import HpoiParser

__all__ = [
    "HpoiScraperService",
    "BrowserEngine",
    "ProxyPool",
    "RateLimiter",
    "CacheManager",
    "HpoiParser",
]
