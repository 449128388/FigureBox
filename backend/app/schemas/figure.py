from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import List, Optional
import re


# ========== Tag Schema ==========
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class Tag(TagBase):
    id: int
    
    class Config:
        from_attributes = True

# 定义正则表达式模式
# 允许中文、英文、日文、数字、空格，常见符号（如 /、×、（）、&、中文冒号、英文冒号等）
ALLOWED_CHARS_PATTERN = re.compile(r'^[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff\u3100-\u312fa-zA-Z0-9\s\/\×\(\)\&\-\.\,\:\;\!\?\#\@\$\%\*\+\=\[\]\{\}\|\<\>\~\`\"\'\\\uff1a\uff08\uff09]*$')
# 材质和尺寸允许更少的特殊字符
SIMPLE_CHARS_PATTERN = re.compile(r'^[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff\u3100-\u312fa-zA-Z0-9\s]*$')
# Emoji 过滤模式
EMOJI_PATTERN = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF\U0001F900-\U0001F9FF]+')


def validate_field(value: str | None, field_name: str, min_length: int, max_length: int, allow_special_chars: bool = True) -> str | None:
    """通用字段验证函数"""
    if value is None:
        return None
    
    # 过滤 emoji
    value = EMOJI_PATTERN.sub('', value)
    
    # 去除首尾空格
    value = value.strip()
    
    # 检查过滤后是否为空（如果原始值不为空但过滤后为空，说明输入的全是emoji）
    if len(value) == 0:
        raise ValueError(f'{field_name}不能只包含特殊字符')
    
    # 长度验证
    if len(value) < min_length:
        raise ValueError(f'{field_name}长度不能少于{min_length}个字符')
    if len(value) > max_length:
        raise ValueError(f'{field_name}长度不能超过{max_length}个字符')
    
    # 字符类型验证
    if allow_special_chars:
        if not ALLOWED_CHARS_PATTERN.match(value):
            raise ValueError(f'{field_name}包含不允许的字符')
    else:
        if not SIMPLE_CHARS_PATTERN.match(value):
            raise ValueError(f'{field_name}包含不允许的字符')
    
    return value


class FigureBase(BaseModel):
    name: str
    japanese_name: str | None = None
    price: float | None = None
    currency: str = "CNY"
    manufacturer: str | None = None
    release_date: date | None = None
    purchase_price: float | None = None
    purchase_currency: str = "CNY"
    purchase_date: date | None = None
    purchase_method: str | None = None
    purchase_type: str | None = None
    quantity: int = 1  # 数量，默认值为1
    market_price: float | None = None
    market_currency: str = "CNY"
    scale: str | None = None
    painting: str | None = None
    original_art: str | None = None
    work: str | None = None
    material: str | None = None
    size: str | None = None
    description: str | None = None
    images: List[str] | None = []

    @field_validator('release_date', 'purchase_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            # 处理 ISO 格式日期时间字符串 (如: 2026-03-06T16:00:00.000Z)
            if 'T' in v:
                # 提取日期部分
                v = v.split('T')[0]
            # 解析日期字符串
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v

    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, v):
        if v is None or v == '':
            raise ValueError('名称不能为空')
        return validate_field(v, '名称', 1, 100)

    @field_validator('japanese_name', mode='before')
    @classmethod
    def validate_japanese_name(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '日文名', 1, 100)

    @field_validator('purchase_method', mode='before')
    @classmethod
    def validate_purchase_method(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '入手途径', 1, 50)

    @field_validator('painting', mode='before')
    @classmethod
    def validate_painting(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '涂装', 1, 40)

    @field_validator('original_art', mode='before')
    @classmethod
    def validate_original_art(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '原画', 1, 40)

    @field_validator('work', mode='before')
    @classmethod
    def validate_work(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '作品', 1, 80)

    @field_validator('manufacturer', mode='before')
    @classmethod
    def validate_manufacturer(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '制造商', 1, 60)

    @field_validator('scale', mode='before')
    @classmethod
    def validate_scale(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '比例', 1, 20)

    @field_validator('material', mode='before')
    @classmethod
    def validate_material(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '材质', 1, 50, allow_special_chars=True)

    @field_validator('size', mode='before')
    @classmethod
    def validate_size(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '尺寸', 1, 50, allow_special_chars=True)


class FigureCreate(FigureBase):
    tag_ids: List[int] = []  # 标签ID列表


class FigureUpdate(BaseModel):
    name: str | None = None
    japanese_name: str | None = None
    manufacturer: str | None = None
    price: float | None = None
    currency: str | None = None
    tag_ids: List[int] | None = None  # 标签ID列表
    release_date: date | None = None
    purchase_price: float | None = None
    purchase_currency: str | None = None
    purchase_date: date | None = None
    purchase_method: str | None = None
    purchase_type: str | None = None
    quantity: int | None = None  # 数量
    market_price: float | None = None
    market_currency: str | None = None
    scale: str | None = None
    painting: str | None = None
    original_art: str | None = None
    work: str | None = None
    material: str | None = None
    size: str | None = None
    description: str | None = None
    images: List[str] | None = None

    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '名称', 1, 100)

    @field_validator('japanese_name', mode='before')
    @classmethod
    def validate_japanese_name(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '日文名', 1, 100)

    @field_validator('purchase_method', mode='before')
    @classmethod
    def validate_purchase_method(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '入手途径', 1, 50)

    @field_validator('painting', mode='before')
    @classmethod
    def validate_painting(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '涂装', 1, 40)

    @field_validator('original_art', mode='before')
    @classmethod
    def validate_original_art(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '原画', 1, 40)

    @field_validator('work', mode='before')
    @classmethod
    def validate_work(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '作品', 1, 80)

    @field_validator('manufacturer', mode='before')
    @classmethod
    def validate_manufacturer(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '制造商', 1, 60)

    @field_validator('scale', mode='before')
    @classmethod
    def validate_scale(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '比例', 1, 20)

    @field_validator('material', mode='before')
    @classmethod
    def validate_material(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '材质', 1, 50, allow_special_chars=True)

    @field_validator('size', mode='before')
    @classmethod
    def validate_size(cls, v):
        if v is None or v == '':
            return None
        return validate_field(v, '尺寸', 1, 50, allow_special_chars=True)


class Figure(FigureBase):
    id: int
    tags: List[Tag] = []  # 返回完整的标签信息
    average_purchase_price: float = 0  # 平均入手价格（根据订单自动计算）

    class Config:
        from_attributes = True


# 精简的手办列表响应模型（用于列表查询，减少数据传输）
class FigureListItem(BaseModel):
    id: int
    name: str
    japanese_name: str | None = None
    price: float | None = None
    currency: str = "CNY"
    market_price: float | None = None
    market_currency: str = "CNY"
    manufacturer: str | None = None
    release_date: date | None = None
    purchase_price: float | None = None
    purchase_currency: str = "CNY"
    purchase_date: date | None = None
    purchase_method: str | None = None
    purchase_type: str | None = None
    quantity: int = 1  # 数量，默认值为1
    scale: str | None = None
    painting: str | None = None
    original_art: str | None = None
    work: str | None = None
    material: str | None = None
    size: str | None = None
    description: str | None = None
    # 图片只返回第一张或空，减少数据量
    image: str | None = None
    tags: List[Tag] = []

    class Config:
        from_attributes = True
