"""
html_parser.py - HPOI 页面解析器（第五层防护）

从 HPOI 商品详情页的 HTML 中提取结构化数据。
HPOI 是 Vue SPA，但 SSR 会在 HTML 中嵌入 JSON-LD (± schema.org Product)。
先尝试解析 JSON-LD（最准确），降级到 meta tags / 文本启发式匹配。

新版解析优先级：
1. <script type="application/ld+json"> 中的 mainEntity 字段
2. Open Graph meta tags
3. 页面文本启发式匹配
4. 默认值空占位
"""
import re
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class HpoiParser:
    """HPOI 页面解析器"""

    @staticmethod
    def parse(html: str, base_url: str = "https://www.hpoi.net") -> Dict[str, Any]:
        """
        解析 HPOI 商品详情页 HTML

        Returns:
            {
                "name", "japanese_name", "manufacturer",
                "price", "currency", "release_date", "work",
                "material", "scale", "image",
                "attributes", "production", "painter", "size"
            }
        """
        soup = BeautifulSoup(html, "html.parser")
        result = {}

        # === 1. JSON-LD 解析（优先级最高） ===
        ld = HpoiParser._parse_jsonld(html)
        if ld:
            result = HpoiParser._extract_from_ld(ld)
            # 返回前补充缺失字段
            return HpoiParser._fill_defaults(result, ld, soup, base_url)

        # === 2. 降级：meta tags / 文本启发式 ===
        result["name"] = HpoiParser._extract_name(soup)
        result["japanese_name"] = None
        result["image"] = HpoiParser._extract_image(soup, base_url)
        text_lines = HpoiParser._get_text_lines(soup)
        result["manufacturer"] = HpoiParser._extract_by_keywords(text_lines, ["发行", "厂商", "制造商"])
        result["scale"] = HpoiParser._extract_by_keywords(text_lines, ["比例"])
        result["original_art"] = HpoiParser._extract_by_keywords(text_lines, ["原画"])
        result["work"] = HpoiParser._extract_by_keywords(text_lines, ["作品", "原作"])
        result["material"] = HpoiParser._extract_by_keywords(text_lines, ["材质", "素材"])
        result["attributes"] = HpoiParser._extract_by_keywords(text_lines, ["属性"])
        if result["attributes"]:
            result["attributes"] = [a.strip() for a in result["attributes"].split() if a.strip()]
        else:
            result["attributes"] = []
        result["production"] = HpoiParser._extract_by_keywords(text_lines, ["制作"])
        result["painter"] = HpoiParser._extract_by_keywords(text_lines, ["涂装"])
        result["size"] = HpoiParser._extract_by_keywords(text_lines, ["尺寸", "高约"])
        result["release_date"] = HpoiParser._extract_date(text_lines)
        result["release_date_text"] = result["release_date"]
        price_info = HpoiParser._extract_price(text_lines)
        result["price"] = price_info["price"]
        result["currency"] = price_info["currency"]
        result["price_text"] = None

        return HpoiParser._fill_defaults(result)

    # ==================== JSON-LD 解析 ====================

    @staticmethod
    def _parse_jsonld(html: str) -> Optional[dict]:
        """提取页面中第一个 application/ld+json 数据"""
        pattern = r'<script type="application/ld\+json">(.*?)</script>'
        for m in re.findall(pattern, html, re.DOTALL):
            try:
                data = json.loads(m.strip())
                # 找到包含 mainEntity 的块
                if isinstance(data, dict):
                    if "mainEntity" in data:
                        return data
                    # 如果直接是 Product 类型
                    if data.get("@type") == "Product":
                        return {"mainEntity": data}
            except json.JSONDecodeError:
                continue
        return None

    @staticmethod
    def _extract_from_ld(ld: dict) -> dict:
        """从 JSON-LD mainEntity 提取各字段"""
        me = ld.get("mainEntity") or {}
        if not isinstance(me, dict):
            me = {}

        result = {}

        # 1. name → mainEntity.name
        result["name"] = me.get("name")

        # 2. japanese_name → mainEntity.alternateName
        alt = me.get("alternateName")
        if isinstance(alt, list) and alt:
            result["japanese_name"] = alt[0]
        elif isinstance(alt, str):
            result["japanese_name"] = alt
        else:
            result["japanese_name"] = None

        # 3. image → mainEntity.image
        result["image"] = me.get("image")

        # 4. 从 description 字段解析结构化信息
        desc = me.get("description") or ""
        desc_fields = HpoiParser._parse_description(desc)

        release_text = desc_fields.get("release_date", "")
        result["release_date"] = HpoiParser._normalize_date(release_text) if release_text else None
        # 保留原始出货日文本（如"2026年12月"），供前端展示
        result["release_date_text"] = release_text or None
        result["manufacturer"] = desc_fields.get("manufacturer")
        result["original_art"] = desc_fields.get("original_art")
        result["work"] = desc_fields.get("work")
        result["material"] = desc_fields.get("material")
        result["scale"] = desc_fields.get("scale")
        attrs_raw = desc_fields.get("attributes")
        if attrs_raw:
            result["attributes"] = [a.strip() for a in attrs_raw.split() if a.strip()]
        else:
            result["attributes"] = []
        result["production"] = desc_fields.get("production")
        result["painter"] = desc_fields.get("painter")
        result["size"] = desc_fields.get("size")

        # 5. price / currency：从 description 中的定价字段提取
        price_raw = desc_fields.get("price_raw", "")
        price_info = HpoiParser._parse_price_from_desc(price_raw)
        result["price"] = price_info["price"]
        result["currency"] = price_info["currency"]
        # 保留原始定价文本（含日元/含税/人民币等），供前端展示
        result["price_text"] = price_raw or None

        return result

    @staticmethod
    def _parse_description(desc: str) -> dict:
        """
        从 JSON-LD description 字段提取关键字段。

        使用正则匹配而非逗号分割，因为描述中的定价/尺寸等字段内部
        可能包含逗号（如 "33,000日元 （含税，1385元）"），逗号分割会断裂。
        定价字段使用独立的正则处理（含数字逗号）。
        """
        fields = {}

        # 所有非定价字段：匹配到下一个 ", \S+:" 模式或行尾
        # 注意：使用 .+? 而非 [^,]+?，因为字段值可能包含英文逗号（如 "材质: PVC, ABS"）
        simple_patterns = {
            "manufacturer": r"(?:^|,\s*)发行\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
            "work":         r"(?:^|,\s*)作品\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
            "original_art": r"(?:^|,\s*)原画\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
            "release_date": r"(?:^|,\s*)出货日\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
            "material":     r"(?:^|,\s*)材质\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
            "scale":        r"(?:^|,\s*)比例\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
            "production":   r"(?:^|,\s*)制作\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
            "painter":      r"(?:^|,\s*)涂装\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
            "size":         r"(?:^|,\s*)尺寸\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
            "attributes":   r"(?:^|,\s*)属性\s*[:：]\s*(.+?)(?=,\s*\S+?\s*[:：]|$)",
        }
        for key, pat in simple_patterns.items():
            m = re.search(pat, desc)
            if m:
                val = m.group(1).strip()
                if val:
                    fields[key] = val

        # 定价：专用模式，处理数字内的逗号（如 "33,000日元 （含税，1385元）"）
        price_pat = r"(?:^|,\s*)定价\s*[:：]\s*([\d,]+(?:日元|円)\s*(?:（[^）]*）)?)"
        m = re.search(price_pat, desc)
        if m:
            fields["price_raw"] = m.group(1).strip()

        return fields

    @staticmethod
    def _parse_price_from_desc(price_raw: str) -> Dict[str, Any]:
        """
        从定价文本中提取价格和币种。
        优先取人民币定价，其次日元。

        示例定价文本：
        - "33,000日元 （含税，1385元）" → price=1385, currency=CNY
        - "16,500日元" → price=16500, currency=JPY
        - "1280元" → price=1280, currency=CNY
        """
        if not price_raw:
            return {"price": 0, "currency": "CNY"}

        # 尝试提取人民币定价：xxx元（可能在括号内如 "（含税，1385元）"）
        cny = re.search(r"(\d[\d,]*)\s*元", price_raw)
        if cny:
            price_str = cny.group(1).replace(",", "")
            try:
                return {"price": float(price_str), "currency": "CNY"}
            except ValueError:
                pass

        # 尝试提取日元定价：xxx日元 / xxx,xxx円
        jpy = re.search(r"(\d[\d,]*)\s*(?:日元|円)", price_raw)
        if jpy:
            price_str = jpy.group(1).replace(",", "")
            try:
                return {"price": float(price_str), "currency": "JPY"}
            except ValueError:
                pass

        # 通用数字
        num = re.search(r"(\d[\d,]*)", price_raw)
        if num:
            try:
                return {"price": float(num.group(1).replace(",", "")), "currency": "CNY"}
            except ValueError:
                pass

        return {"price": 0, "currency": "CNY"}

    @staticmethod
    def _normalize_date(text: str) -> Optional[str]:
        """将中文日期转为 YYYY-MM-DD"""
        # "2026年12月" → "2026-12"
        # "2026年12月28日" → "2026-12-28"
        m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})?\s*日?", text)
        if m:
            y, mo, d = m.group(1), m.group(2), m.group(3)
            if d:
                return f"{y}-{mo.zfill(2)}-{d.zfill(2)}"
            return f"{y}-{mo.zfill(2)}"
        return None

    # ==================== 降级方法 ====================

    @staticmethod
    def _fill_defaults(result: dict, ld: dict = None, soup: BeautifulSoup = None,
                       base_url: str = "") -> dict:
        """填充缺失字段的默认值"""
        if not result.get("name"):
            if soup:
                result["name"] = HpoiParser._extract_name(soup)
            result["name"] = result.get("name") or "未知手办"
        if not result.get("image"):
            if soup:
                result["image"] = HpoiParser._extract_image(soup, base_url)
        if not result.get("scale"):
            if ld:
                me = ld.get("mainEntity") or {}
                desc = me.get("description", "")
                text_lines = HpoiParser._get_text_lines_from_desc(desc)
                result["scale"] = HpoiParser._extract_by_keywords(text_lines, ["比例"])
        defaults = {
            "name": "未知手办",
            "japanese_name": None,
            "manufacturer": None,
            "scale": None,
            "original_art": None,
            "work": None,
            "material": None,
            "release_date": None,
            "release_date_text": None,
            "price": 0,
            "currency": "CNY",
            "price_text": None,
            "image": None,
            "attributes": [],
            "production": None,
            "painter": None,
            "size": None,
        }
        for k, v in defaults.items():
            if k not in result or result[k] is None:
                result[k] = v
        return result

    @staticmethod
    def _get_text_lines(soup: BeautifulSoup) -> list:
        text = soup.get_text(separator="\n", strip=True)
        return [line.strip() for line in text.split("\n") if line.strip()]

    @staticmethod
    def _extract_name(soup: BeautifulSoup) -> Optional[str]:
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
            for suffix in [" - HPOI", " | Hpoi手办维基", " | HPOI"]:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
            if title:
                return title
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)
            for suffix in [" - HPOI", " | Hpoi手办维基", " | HPOI", " | 动漫模玩百科"]:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
            if title:
                return title
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return None

    @staticmethod
    def _extract_image(soup: BeautifulSoup, base_url: str) -> Optional[str]:
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            return og_img["content"].strip()
        twitter_img = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_img and twitter_img.get("content"):
            return twitter_img["content"].strip()
        return None

    @staticmethod
    def _extract_by_keywords(lines: list, keywords: list) -> Optional[str]:
        for kw in keywords:
            for line in lines:
                if kw in line:
                    for sep in [": ", "："]:
                        if sep in line:
                            val = line.split(sep, 1)[1].strip()
                            if val and val != kw and len(val) < 100:
                                return val
        return None

    @staticmethod
    def _extract_date(lines: list) -> Optional[str]:
        date_pattern = re.compile(r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})?日?")
        for line in lines:
            if "发售" in line or "发行" in line or "出荷" in line or "出货" in line or "上市" in line:
                match = date_pattern.search(line)
                if match:
                    y, mo, d = match.group(1), match.group(2), match.group(3)
                    if d:
                        return f"{y}-{mo.zfill(2)}-{d.zfill(2)}"
                    return f"{y}-{mo.zfill(2)}"
        return None

    @staticmethod
    def _extract_price(lines: list) -> Dict[str, Any]:
        """降级价格提取"""
        cny = re.compile(r"[¥￥]\s*(\d[\d,]*)|\b(\d[\d,]*)\s*元")
        jpy = re.compile(r"(\d[\d,]*)\s*(?:日元|円|JPY)")
        for line in lines:
            if "定价" not in line and "价格" not in line and "售价" not in line:
                continue
            mc = cny.search(line)
            if mc:
                ps = mc.group(1) or mc.group(2)
                return {"price": float(ps.replace(",", "")), "currency": "CNY"}
            mj = jpy.search(line)
            if mj:
                return {"price": float(mj.group(1).replace(",", "")), "currency": "JPY"}
        return {"price": 0, "currency": "CNY"}
