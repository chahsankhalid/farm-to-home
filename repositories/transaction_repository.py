from sqlalchemy.orm import Session

from models.seed_transaction import SeedTransaction
from enums.transaction_type import TransactionType


def create_transaction(
    db: Session,
    customer_id: int,
    amount: int,
    reason: str,
    transaction_type: TransactionType,
    order_id: str | None = None,
    recharge_charge_id: str | None = None,
):
    transaction = SeedTransaction(
        customer_id=customer_id,
        amount=amount,
        reason=reason,
        transaction_type=transaction_type,
        order_id=order_id,
        recharge_charge_id=recharge_charge_id,
    )

    db.add(transaction)
    db.flush()
    db.refresh(transaction)

    return transaction

def get_by_order_id(
    db: Session,
    order_id: str,
):
    return (
        db.query(SeedTransaction)
        .filter(SeedTransaction.order_id == order_id)
        .first()
    )
    
def get_customer_transactions(
    db: Session,
    customer_id: int,
):
    return (
        db.query(SeedTransaction)
        .filter(
            SeedTransaction.customer_id == customer_id
        )
        .order_by(
            SeedTransaction.created_at.desc()
        )
        .all()
    )