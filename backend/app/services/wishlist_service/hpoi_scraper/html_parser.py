"""
html_parser.py - HPOI 页面解析器（第五层防护）

从 HPOI 商品详情页的 HTML 中提取结构化数据。
HPOI 是 Vue SPA，但 SSR 会在 HTML 中嵌入 meta、og 标签和 JSON-LD 数据。
降级策略：meta tags → text heuristic → ID 占位符
"""
import re
import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class HpoiParser:
    """HPOI 页面解析器"""

    @staticmethod
    def parse(html: str, base_url: str = "https://www.hpoi.net") -> Dict[str, Any]:
        """
        解析 HPOI 商品详情页 HTML

        优先级：
        1. Open Graph / Twitter Card meta tags
        2. JSON-LD 结构化数据
        3. 页面文本启发式匹配
        4. 默认值

        Returns:
            {
                "name", "japanese_name", "manufacturer", "scale",
                "price", "currency", "release_date", "work",
                "material", "image"
            }
        """
        soup = BeautifulSoup(html, "html.parser")
        result = {}

        # === 1. 名称 ===
        result["name"] = HpoiParser._extract_name(soup)
        result["japanese_name"] = None

        # === 2. 封面图 ===
        result["image"] = HpoiParser._extract_image(soup, base_url)

        # === 3. 从文本行中提取结构化信息 ===
        text_lines = HpoiParser._get_text_lines(soup)

        result["manufacturer"] = HpoiParser._extract_by_keywords(text_lines, ["厂商", "制造商", "品牌"])
        result["scale"] = HpoiParser._extract_by_keywords(text_lines, ["比例", "スケール"])
        result["work"] = HpoiParser._extract_by_keywords(text_lines, ["作品", "作品名", "原作"])
        result["material"] = HpoiParser._extract_by_keywords(text_lines, ["材质", "素材", "材料"])

        # === 4. 发售日期 ===
        result["release_date"] = HpoiParser._extract_date(text_lines)

        # === 5. 价格 ===
        price_info = HpoiParser._extract_price(text_lines)
        result["price"] = price_info["price"]
        result["currency"] = price_info["currency"]

        # 确保所有字段有值
        defaults = {
            "name": "未知手办",
            "japanese_name": None,
            "manufacturer": None,
            "scale": None,
            "work": None,
            "material": None,
            "release_date": None,
            "price": 0,
            "currency": "CNY",
            "image": None,
        }
        for k, v in defaults.items():
            if k not in result or result[k] is None:
                result[k] = v

        return result

    @staticmethod
    def _get_text_lines(soup: BeautifulSoup) -> list:
        """获取页面的非空文本行"""
        text = soup.get_text(separator="\n", strip=True)
        return [line.strip() for line in text.split("\n") if line.strip()]

    @staticmethod
    def _extract_name(soup: BeautifulSoup) -> Optional[str]:
        """提取名称"""
        # 1. og:title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
            # 去掉站点后缀
            for suffix in [" - HPOI", " | Hpoi手办维基", " | HPOI"]:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
            if title:
                return title

        # 2. <title>
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)
            for suffix in [" - HPOI", " | Hpoi手办维基", " | HPOI", " | 动漫模玩百科"]:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
            if title:
                return title

        # 3. h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return None

    @staticmethod
    def _extract_image(soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """提取封面图"""
        # 1. og:image
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            return og_img["content"].strip()

        # 2. twitter:image
        twitter_img = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_img and twitter_img.get("content"):
            return twitter_img["content"].strip()

        # 3. 查找 hpoi 图床的 img
        imgs = soup.find_all("img")
        for img in imgs:
            src = img.get("src") or img.get("data-src") or ""
            if "hpoi.net/gc" in src or "img.hpoi.net" in src:
                # 尝试获取大图
                src = src.replace("/s/", "/n/").replace("/t/", "/n/")
                return src

        return None

    @staticmethod
    def _extract_by_keywords(lines: list, keywords: list) -> Optional[str]:
        """从文本行中按关键词提取冒号后的值"""
        for kw in keywords:
            for line in lines:
                if kw in line:
                    # 取冒号后的内容
                    for sep in [":", "："]:
                        if sep in line:
                            val = line.split(sep, 1)[1].strip()
                            if val and val != kw and len(val) < 100:
                                return val
        return None

    @staticmethod
    def _extract_date(lines: list) -> Optional[str]:
        """提取发售日期"""
        date_pattern = re.compile(r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})日?")
        for line in lines:
            if "发售" in line or "发行" in line or "出荷" in line or "上市" in line:
                match = date_pattern.search(line)
                if match:
                    y, m, d = match.group(1), match.group(2), match.group(3)
                    return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        return None

    @staticmethod
    def _extract_price(lines: list) -> Dict[str, Any]:
        """提取定价和币种"""
        # 常见价格格式: ¥1,280 / ￥1,280 / 1,280円 / 16,500 JPY / 1280元
        price_patterns = [
            re.compile(r"[¥￥]\s*([\d,]+)"),
            re.compile(r"([\d,]+)\s*円"),
            re.compile(r"([\d,]+)\s*JPY"),
            re.compile(r"([\d,]+)\s*元"),
            re.compile(r"USD\s*([\d,]+)"),
            re.compile(r"([\d,]+)\s*USD"),
        ]

        for line in lines:
            if "定价" not in line and "价格" not in line and "售价" not in line and "価格" not in line:
                continue

            for pattern in price_patterns:
                match = pattern.search(line)
                if match:
                    price_str = match.group(1).replace(",", "")
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = 0

                    currency = "CNY"
                    if "円" in line or "JPY" in line:
                        currency = "JPY"
                    elif "USD" in line or "$" in line:
                        currency = "USD"

                    return {"price": price, "currency": currency}

        return {"price": 0, "currency": "CNY"}
