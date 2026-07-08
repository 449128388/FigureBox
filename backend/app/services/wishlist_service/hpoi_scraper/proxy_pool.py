"""
proxy_pool.py - 智能代理池（第二层防护）

维护住宅代理列表，每次请求随机出口 IP。
当前为模板配置，实际使用需替换为真实代理。
支持多代理服务商：阿布云、快代理、站大爷、Bright Data 等。
"""
import random
import os
from typing import Optional


# 从环境变量读取代理列表，逗号分隔
# 格式: http://user:pass@host:port
_DEFAULT_PROXIES = os.getenv("HPOI_PROXY_LIST", "").split(",") if os.getenv("HPOI_PROXY_LIST") else []


class ProxyPool:
    """代理池"""

    def __init__(self, proxies: list = None):
        self.proxies = proxies or _DEFAULT_PROXIES

    def get_random(self) -> Optional[str]:
        """随机获取一个代理，无可用代理时返回 None（降级为直连）"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def is_empty(self) -> bool:
        return len(self.proxies) == 0


# 全局单例
proxy_pool = ProxyPool()
