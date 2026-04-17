from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base

class AssetPriceHistory(Base):
    """
    资产价格历史记录模型 - 记录手办价格变化历史
    
    功能说明：
    - 记录手办每次价格更新的历史
    - 用于生成价格趋势图表
    - 支持资产增值分析
    
    关联关系：
    - figure: 多对一关联 Figure 表
    """
    __tablename__ = "asset_price_history"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 记录唯一标识ID
    
    # 外键关联
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False)  # 关联手办ID
    
    # 价格信息
    current_price = Column(Float, nullable=False)  # 当前估价/记录时的价格
    date = Column(DateTime(timezone=True), server_default=func.now())  # 记录日期时间

    # 关系
    figure = relationship("Figure")  # 关联手办对象


class AssetAlert(Base):
    """
    资产预警设置模型 - 用户设置的价格预警
    
    功能说明：
    - 允许用户为手办设置价格预警
    - 当价格达到设定阈值时触发提醒
    - 支持价格上涨和下跌预警
    
    预警类型说明：
    - price_drop: 价格下跌预警（低于设定值提醒）
    - price_rise: 价格上涨预警（高于设定值提醒）
    
    关联关系：
    - user: 多对一关联 User 表
    - figure: 多对一关联 Figure 表
    """
    __tablename__ = "asset_alerts"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 预警设置唯一标识ID
    
    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联用户ID
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False)  # 关联手办ID
    
    # 预警配置
    alert_type = Column(String(50), nullable=False)  # 预警类型：price_drop（价格下跌）、price_rise（价格上涨）等
    threshold = Column(Float, nullable=False)  # 预警阈值（触发提醒的价格值）
    is_active = Column(Integer, default=1)  # 是否激活（1=激活，0=禁用）
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 创建时间

    # 关系
    user = relationship("User")  # 关联用户对象
    figure = relationship("Figure")  # 关联手办对象


class AssetTransaction(Base):
    """
    资产交易记录模型 - 记录手办的买卖交易

    功能说明：
    - 记录手办的买入和卖出交易
    - 用于计算投资收益
    - 支持交易备注记录
    - 支持股票式补仓功能（记录数量、剩余持仓等）

    交易类型说明：
    - buy: 买入/购买
    - sell: 卖出/转让

    关联关系：
    - user: 多对一关联 User 表
    - figure: 多对一关联 Figure 表
    - order: 多对一关联 Order 表（买入交易关联订单）
    """
    __tablename__ = "asset_transactions"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 交易记录唯一标识ID

    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联用户ID
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False)  # 关联手办ID
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # 关联订单ID（买入交易时关联）

    # 交易信息
    transaction_type = Column(String(50), nullable=False)  # 交易类型：buy（买入）、sell（卖出）
    price = Column(Float, nullable=False)  # 交易价格（单价）
    quantity = Column(Integer, nullable=False, default=1)  # 交易数量
    total_amount = Column(Float, nullable=False)  # 交易总金额（price × quantity）
    remaining_quantity = Column(Integer, nullable=True)  # 单条交易记录剩余持仓数量（用于部分卖出后的持仓计算）,不是总库存的汇总值
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())  # 交易日期时间
    notes = Column(String(255))  # 交易备注/说明
    
    # 软删除字段
    is_active = Column(Boolean, default=True)  # 是否激活
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # 删除时间

    # 关系
    user = relationship("User")  # 关联用户对象
    figure = relationship("Figure")  # 关联手办对象
    order = relationship("Order")  # 关联订单对象


class StockIndexCache(Base):
    """
    股票指数缓存模型 - 缓存上证指数等市场指数数据
    
    功能说明：
    - 缓存股票指数（如上证指数）的当前数据
    - 用于对比手办资产与市场表现
    - 控制API请求频率（避免频繁调用外部API）
    
    字段说明：
    - 存储指数代码、名称、当前值、涨跌等
    - 记录请求次数和日期（用于限流）
    """
    __tablename__ = "stock_index_cache"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 缓存记录唯一标识ID
    
    # 指数基本信息
    index_code = Column(String(20), nullable=False, unique=True, index=True)  # 指数代码，如 sh000001（上证指数）
    index_name = Column(String(50), nullable=False)  # 指数名称（如：上证指数）
    
    # 指数数据
    current_value = Column(Float, nullable=False)  # 当前指数值
    change_value = Column(Float, default=0)  # 涨跌值（相对于昨日收盘）
    change_percentage = Column(Float, default=0)  # 涨跌幅百分比
    
    # 缓存控制
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # 最后更新时间
    request_count = Column(Integer, default=0)  # 当日请求次数（用于限流控制）
    request_date = Column(Date, nullable=False)  # 请求日期（用于按天统计）


class StockIndexHistory(Base):
    """
    上证指数历史记录模型 - 保存每次请求的历史数据
    
    功能说明：
    - 记录每次获取的指数详细数据
    - 用于生成指数走势图
    - 支持历史数据分析
    
    与 StockIndexCache 的区别：
    - Cache：只保存最新数据，用于快速查询
    - History：保存所有历史记录，用于趋势分析
    """
    __tablename__ = "stock_index_history"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 历史记录唯一标识ID
    
    # 指数基本信息
    index_code = Column(String(20), nullable=False, index=True)  # 指数代码，如 sh000001
    index_name = Column(String(50), nullable=False)  # 指数名称
    
    # 指数详细数据
    current_value = Column(Float, nullable=False)  # 当前指数值
    change_value = Column(Float, default=0)  # 涨跌值
    change_percentage = Column(Float, default=0)  # 涨跌幅百分比
    prev_close = Column(Float, nullable=True)  # 昨日收盘价
    open_value = Column(Float, nullable=True)  # 今日开盘价
    
    # 时间信息
    request_time = Column(DateTime(timezone=True), server_default=func.now())  # 请求时间（精确到秒）
    request_date = Column(Date, nullable=False)  # 请求日期（用于按天分组）

    # 索引优化
    __table_args__ = (
        {'mysql_engine': 'InnoDB'},
    )


class AssetValueCache(Base):
    """
    资产市值缓存模型 - 缓存用户每日资产总市值
    
    功能说明：
    - 记录用户每日的资产总市值
    - 用于计算日涨跌（对比昨日市值）
    - 支持资产趋势分析
    
    关联关系：
    - user: 多对一关联 User 表
    """
    __tablename__ = "asset_value_cache"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 缓存记录唯一标识ID
    
    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联用户ID
    
    # 资产数据
    total_value = Column(Float, nullable=False)  # 当日总市值（所有手办当前价值总和）
    cache_date = Column(Date, nullable=False)  # 缓存日期（哪一天的数据）
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 记录创建时间

    # 关系
    user = relationship("User")  # 关联用户对象

class UserSettings(Base):
    """用户设置（年度手办消费上限等）"""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    annual_spending_limit = Column(Float, default=0)  # 年度手办消费上限（0表示未设置）
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # 更新时间

    # 关系
    user = relationship("User") # 关联用户对象


class OrderTransaction(Base):
    """
    订单资金流水记录模型 - 记录手办的真实资金变动（资金账）

    功能说明：
    - 只记录有真实资金流动的交易
    - 严禁记录无资金流动的场景（库存调整、价格调整等）
    - 支持资金流向分析和财务报表

    交易类型说明：
    - buy: 买入支出（订单支付、定金、尾款）
    - sell: 卖出收入（闲鱼出售等）
    - refund: 退款收入（退货/取消订单）
    - fee: 手续费支出（平台扣费）

    资金流向说明：
    - in: 资金流入（收入）
    - out: 资金流出（支出）

    关联关系：
    - user: 多对一关联 User 表
    - figure: 多对一关联 Figure 表
    - order: 多对一关联 Order 表（可选）
    """
    __tablename__ = "order_transactions"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 资金流水记录唯一标识ID

    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联用户ID
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False)  # 关联手办ID
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # 关联订单ID（可选）

    # 交易信息
    transaction_type = Column(String(50), nullable=False)  # 交易类型：buy(买入)/sell(卖出)/refund(退款)/fee(手续费)
    direction = Column(String(10), nullable=False, default="out")  # 资金流向：in(收入)/out(支出)
    quantity = Column(Integer, default=1)  # 交易数量
    unit_price = Column(Float, nullable=False)  # 交易单价
    total_amount = Column(Float, nullable=False)  # 交易总金额（unit_price × quantity）
    currency = Column(String(10), default="CNY")  # 货币类型

    # 交易详情
    payment_method = Column(String(50))  # 支付方式：支付宝/微信/银行卡/现金等
    platform = Column(String(50))  # 交易平台：淘宝/闲鱼/AmiAmi/京东/线下等

    # 时间字段
    transaction_date = Column(DateTime(timezone=True), nullable=False)  # 交易发生时间（业务时间）
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 系统记录时间

    # 备注
    notes = Column(String(255))  # 交易备注/说明

    # 软删除字段
    is_active = Column(Boolean, default=True)  # 是否激活
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # 删除时间

    # 关系
    user = relationship("User")  # 关联用户对象
    figure = relationship("Figure")  # 关联手办对象
    order = relationship("Order")  # 关联订单对象