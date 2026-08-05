"""
dashboard 子包入口

资产看板相关 API 路由聚合包（2026-08-04 重组）

子模块：
- assets:        资产看板（dashboard / 价格更新 / 补仓 / 持仓筛选 / 年度限额 / 汇率）
- market:        行情看板（HPI / 成分股 / 板块排行 / K线）
- trade_records: 交易记录（大盘统计 / 账单导出 / 买入订单 / 卖出订单 / 尾款支付）
- collector:     收藏家看板（概览 / 高价值藏品 / 标签云 / 动态流 / 评分 / 隐私 / 分享）

子包演进：
- 2026-08-04 #46：trade_records 从 app/api/records/ 迁移而来
- 2026-08-04 #47：market 从 app/api/market/ 迁移而来
- 2026-08-04 #48：assets 从 app/api/assets/ 迁移而来
- 2026-08-04 #49：collector 从 app/api/collector/ 迁移而来
"""
