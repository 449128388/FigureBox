"""
订单资金流水服务 - 主服务类
整合交易创建、查询、删除等子服务

核心原则：
- 只记录有真实资金流动的交易
- 严禁记录无资金流动的场景（库存调整、价格调整等）
- 资金账与库存账完全解耦

必须记录的场景（有真实资金流动）：
- 订单支付（买入）：trans_type='buy', direction='out'
- 订单收款（卖出）：trans_type='sell', direction='in'
- 定金支付：trans_type='deposit', direction='out'
- 尾款支付：trans_type='buy', direction='out'
- 退款（退货/取消）：trans_type='refund', direction='in'
- 平台手续费：trans_type='fee', direction='out'

严禁记录的场景（无资金流动）：
- 库存调整（纠错）：不记录，或记 amount=0（占位）
- 冲正库存（数量减少）：不记录，库存账用 adjust 类型
- 价格调整（估值变化）：不记录，这是资产重估，非现金流
- 自动创建手办（无订单）：不记录，等补录订单后再记
"""

from .transaction_create_service import TransactionCreateService
from .transaction_query_service import TransactionQueryService
from .transaction_delete_service import TransactionDeleteService
from .transaction_change_service import TransactionChangeService


class OrderTransactionService:
    """
    订单资金流水服务类
    
    采用组合模式整合各子服务：
    - TransactionCreateService: 交易创建
    - TransactionQueryService: 交易查询统计
    - TransactionDeleteService: 交易删除
    
    使用方式：
        from app.services.order_transaction_service import OrderTransactionService
        
        # 创建买入交易
        OrderTransactionService.create_buy_transaction(db, user_id, figure_id, ...)
        
        # 查询手办总支出
        total = OrderTransactionService.get_figure_total_spending(db, user_id, figure_id)
        
        # 删除订单相关交易
        count = OrderTransactionService.delete_transactions_by_order(db, user_id, order_id)
    """

    # ===== 交易创建方法 =====
    
    @staticmethod
    def create_buy_transaction(*args, **kwargs):
        """创建买入交易记录（资金流出）"""
        return TransactionCreateService.create_buy_transaction(*args, **kwargs)

    @staticmethod
    def create_sell_transaction(*args, **kwargs):
        """创建卖出交易记录（资金流入）"""
        return TransactionCreateService.create_sell_transaction(*args, **kwargs)

    @staticmethod
    def create_deposit_transaction(*args, **kwargs):
        """创建定金交易记录（资金流出）"""
        return TransactionCreateService.create_deposit_transaction(*args, **kwargs)

    @staticmethod
    def create_refund_transaction(*args, **kwargs):
        """创建退款交易记录（资金流入）"""
        return TransactionCreateService.create_refund_transaction(*args, **kwargs)

    @staticmethod
    def create_fee_transaction(*args, **kwargs):
        """创建手续费交易记录（资金流出）"""
        return TransactionCreateService.create_fee_transaction(*args, **kwargs)

    @staticmethod
    def create_transaction_from_order(*args, **kwargs):
        """从订单创建买入交易记录"""
        return TransactionCreateService.create_transaction_from_order(*args, **kwargs)

    # ===== 交易查询方法 =====

    @staticmethod
    def get_figure_total_spending(*args, **kwargs):
        """获取手办的总支出金额"""
        return TransactionQueryService.get_figure_total_spending(*args, **kwargs)

    @staticmethod
    def get_figure_total_income(*args, **kwargs):
        """获取手办的总收入金额"""
        return TransactionQueryService.get_figure_total_income(*args, **kwargs)

    @staticmethod
    def get_user_total_spending(*args, **kwargs):
        """获取用户总支出金额"""
        return TransactionQueryService.get_user_total_spending(*args, **kwargs)

    @staticmethod
    def get_user_total_income(*args, **kwargs):
        """获取用户总收入金额"""
        return TransactionQueryService.get_user_total_income(*args, **kwargs)

    @staticmethod
    def get_transactions_by_figure(*args, **kwargs):
        """获取手办的所有交易记录"""
        return TransactionQueryService.get_transactions_by_figure(*args, **kwargs)

    @staticmethod
    def get_transactions_by_order(*args, **kwargs):
        """获取订单的所有交易记录"""
        return TransactionQueryService.get_transactions_by_order(*args, **kwargs)

    # ===== 交易删除方法 =====

    @staticmethod
    def delete_transactions_by_figure(*args, **kwargs):
        """软删除手办相关的所有资金流水记录"""
        return TransactionDeleteService.delete_transactions_by_figure(*args, **kwargs)

    @staticmethod
    def delete_transactions_by_order(*args, **kwargs):
        """软删除订单相关的所有资金流水记录"""
        return TransactionDeleteService.delete_transactions_by_order(*args, **kwargs)

    @staticmethod
    def delete_transaction_by_id(*args, **kwargs):
        """软删除单条交易记录"""
        return TransactionDeleteService.delete_transaction_by_id(*args, **kwargs)

    # ===== 交易变更追踪方法 =====

    @staticmethod
    def detect_and_record_changes(*args, **kwargs):
        """检测订单变更并记录相应的资金流水"""
        return TransactionChangeService.detect_and_record_changes(*args, **kwargs)

    @staticmethod
    def get_transaction_history(*args, **kwargs):
        """获取订单的资金流水历史（按时间排序）"""
        return TransactionChangeService.get_transaction_history(*args, **kwargs)

    @staticmethod
    def calculate_running_total(*args, **kwargs):
        """计算订单的累计支付金额"""
        return TransactionChangeService.calculate_running_total(*args, **kwargs)
