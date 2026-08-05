"""
资产交易删除服务
提供删除资产交易记录的业务逻辑
"""
from sqlalchemy.orm import Session

from app.models.asset_transaction import AssetTransaction


class AssetTransactionDeleteService:
    """资产交易删除服务类"""

    @staticmethod
    def delete_transaction(
        db: Session,
        transaction_id: int,
        user_id: int
    ) -> bool:
        """
        删除交易记录

        Args:
            db: 数据库会话
            transaction_id: 交易记录ID
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        transaction = db.query(AssetTransaction).filter(
            AssetTransaction.id == transaction_id,
            AssetTransaction.user_id == user_id
        ).first()

        if not transaction:
            return False

        db.delete(transaction)
        db.flush()
        return True
