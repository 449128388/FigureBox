FROM python:3.11-slim-bookworm

WORKDIR /app

# 安装 Playwright 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    --fix-missing \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 安装 Playwright + Chromium
RUN pip install --no-cache-dir playwright && \
    python -m playwright install chromium

# 安装 Playwright 系统依赖
RUN python -m playwright install-deps chromium || true

COPY . .

RUN chmod +x entrypoint.sh

CMD ["sh", "entrypoint.sh"]
