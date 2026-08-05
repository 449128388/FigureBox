"""
资产交易变更服务
提供修改资产交易记录的业务逻辑
"""
from sqlalchemy.orm import Session

from app.models.asset_transaction import AssetTransaction


class AssetTransactionChangeService:
    """资产交易变更服务类"""

    @staticmethod
    def update_transaction_notes(
        db: Session,
        transaction_id: int,
        user_id: int,
        notes: str
    ) -> bool:
        """
        更新交易记录备注

        Args:
            db: 数据库会话
            transaction_id: 交易记录ID
            user_id: 用户ID
            notes: 新的备注内容

        Returns:
            是否更新成功
        """
        transaction = db.query(AssetTransaction).filter(
            AssetTransaction.id == transaction_id,
            AssetTransaction.user_id == user_id
        ).first()

        if not transaction:
            return False

        transaction.notes = notes
        db.flush()
        return True
