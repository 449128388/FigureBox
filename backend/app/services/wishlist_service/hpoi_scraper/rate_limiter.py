"""
rate_limiter.py - 令牌桶限流器（第三层防护）

全局限制对 HPOI 的请求速率，避免触发 WAF。
默认：每 20 秒 1 个请求，最多突发 2 个。
"""
import time
import threading


class RateLimiter:
    """令牌桶限流器"""

    def __init__(self, rate: float = 1 / 20, capacity: int = 2):
        """
        Args:
            rate: 每秒产生令牌数（默认 1/20 = 每20秒1个请求）
            capacity: 桶容量（突发请求上限）
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()

    def acquire(self, blocking: bool = True, timeout: float = None) -> bool:
        """获取令牌"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True

            if not blocking:
                return False

            wait_time = (1 - self.tokens) / self.rate
            if timeout is not None and wait_time > timeout:
                return False

        time.sleep(wait_time)
        return self.acquire(blocking=False)


# 全局单例：所有 HPOI 请求共用同一个限流器
hpoi_limiter = RateLimiter(rate=1 / 20, capacity=2)
