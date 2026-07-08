"""
browser_engine.py - 浏览器级模拟引擎（第一层防护）

使用 Playwright + Chromium 以真实浏览器行为访问 HPOI：
- 完整 JavaScript 渲染（HPOI 是 Vue SPA）
- 5-10 个 User-Agent 池随机切换
- 视口随机化（1366×768 ~ 2560×1440）
- 持久化 browser 实例复用（避免每次新建浏览器的指纹特征）
- Cookie/localStorage 持久化（模拟历史会话）
- 反自动化检测 + Canvas/WebGL/AudioContext 指纹随机化
- 模拟人类操作（滚动、随机延迟）
"""
import random
import hashlib
from playwright.sync_api import sync_playwright, Browser, BrowserContext


# ========== User-Agent 池（10 个，Chrome 120~130，Win/Mac 混用） ==========
USER_AGENT_POOL = [
    # Chrome 130 (Win11)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    # Chrome 129 (Win11)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    # Chrome 128 (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    # Chrome 127 (Win10)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    # Chrome 126 (Win11)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    # Chrome 125 (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    # Chrome 124 (Win11)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Chrome 123 (Win10)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Chrome 122 (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    # Chrome 121 (Win11)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]


# ========== 反检测 + 指纹随机化脚本 ==========
FINGERPRINT_SCRIPT = """
// === 反自动化检测 ===
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});
Object.defineProperty(navigator, 'languages', {
    get: () => ['zh-CN', 'zh', 'en']
});
window.chrome = { runtime: {} };

// 覆盖 permissions API
const _origQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        _origQuery(parameters)
);

// === Canvas 指纹随机化（轻微扰动） ===
(function() {
    const _origGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(...args) {
        const ctx = _origGetContext.apply(this, args);
        if (ctx && args[0] === '2d') {
            const _origFillText = ctx.fillText.bind(ctx);
            ctx.fillText = function(text, x, y, maxWidth) {
                const noise = (Math.random() - 0.5) * 0.02;
                return _origFillText(text, x + noise, y + noise, maxWidth);
            };
            const _origGetImageData = ctx.getImageData.bind(ctx);
            ctx.getImageData = function(...args) {
                const data = _origGetImageData(...args);
                for (let i = 0; i < data.data.length; i += 4) {
                    data.data[i] += (Math.random() - 0.5) * 2;
                    data.data[i + 1] += (Math.random() - 0.5) * 2;
                    data.data[i + 2] += (Math.random() - 0.5) * 2;
                }
                return data;
            };
        }
        return ctx;
    };
})();

// === WebGL 指纹随机化 ===
(function() {
    const _origGetParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(param) {
        if (param === 37445) return 'Intel Inc.';
        if (param === 37446) return 'Intel Iris OpenGL Engine';
        return _origGetParameter.apply(this, arguments);
    };
})();

// === AudioContext 指纹随机化 ===
(function() {
    const _origCreateOscillator = (window.AudioContext || window.webkitAudioContext).prototype.createOscillator;
    (window.AudioContext || window.webkitAudioContext).prototype.createOscillator = function() {
        const osc = _origCreateOscillator.apply(this, arguments);
        const _origGetFrequencyData = osc.getFrequencyData;
        if (_origGetFrequencyData) {
            osc.getFrequencyData = function(array) {
                _origGetFrequencyData.apply(this, arguments);
                for (let i = 0; i < array.length; i++) {
                    array[i] += (Math.random() - 0.5) * 2;
                }
            };
        }
        return osc;
    };
})();
"""


# ========== 视口池 ==========
VIEWPORT_POOL = [
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1600, "height": 900},
    {"width": 1680, "height": 1050},
    {"width": 1920, "height": 1080},
    {"width": 1920, "height": 1200},
    {"width": 2048, "height": 1152},
    {"width": 2560, "height": 1440},
]

# ========== 公共请求头（平台/版本无关部分） ==========
BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.hpoi.net/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


class BrowserEngine:
    """浏览器引擎（持久化实例 + 指纹随机化）"""

    _instance = None
    _playwright = None
    _browser: Browser = None
    _context: BrowserContext = None
    _current_proxy: str = None

    @classmethod
    def get_instance(cls) -> "BrowserEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_browser(self, proxy: str = None, force_new: bool = False):
        """
        确保持久化 browser 实例存在。
        代理变更时自动重建实例。
        """
        if proxy != self._current_proxy:
            force_new = True

        if self._browser is not None and not force_new:
            return

        self._current_proxy = proxy

        # 关闭旧实例
        self._close()

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ]
        proxy_config = {"server": proxy} if proxy else None

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=True,
            proxy=proxy_config,
            args=launch_args,
        )

        # 创建持久化 context（Cookie/localStorage 在此 context 中保持）
        ua = random.choice(USER_AGENT_POOL)
        viewport = random.choice(VIEWPORT_POOL)
        self._context = self._browser.new_context(
            viewport=viewport,
            user_agent=ua,
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            extra_http_headers=BASE_HEADERS,
        )
        self._context.add_init_script(FINGERPRINT_SCRIPT)

    def _close(self):
        """安全关闭所有资源"""
        try:
            if self._context:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._context = None
        self._browser = None
        self._playwright = None

    def fetch_page(self, url: str, proxy: str = None, timeout: int = 30000) -> str:
        """
        使用 Playwright 获取页面完整 HTML（持久化 browser 实例）

        Args:
            url: 目标 URL
            proxy: 代理地址
            timeout: 超时毫秒

        Returns:
            渲染后的页面 HTML 字符串
        """
        try:
            self._ensure_browser(proxy=proxy)
            page = self._context.new_page()

            page.goto(url, wait_until="networkidle", timeout=timeout)

            # 随机停留 2-5 秒，模拟人类阅读
            page.wait_for_timeout(random.randint(2000, 5000))

            # 模拟滚动（HPOI 有懒加载图片）
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            page.wait_for_timeout(random.randint(800, 1500))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(random.randint(500, 1000))

            html = page.content()
            page.close()
            return html
        except Exception as e:
            # 发生异常时关闭并重置（下次请求重建）
            self._close()
            raise RuntimeError(f"浏览器抓取失败: {e}")

    @staticmethod
    def url_to_hash(url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()
