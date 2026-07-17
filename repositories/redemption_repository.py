from sqlalchemy.orm import Session

from models.redemption import Redemption


def create_redemption(
    db: Session,
    customer_id: int,
    reward_id: int,
    seeds_spent: int,
):
    redemption = Redemption(
        customer_id=customer_id,
        reward_id=reward_id,
        seeds_spent=seeds_spent,
        status="PENDING",
    )

    db.add(redemption)
    db.flush()
    db.refresh(redemption)

    return redemption


def get_redemption(
    db: Session,
    redemption_id: int,
):
    return (
        db.query(Redemption)
        .filter(Redemption.id == redemption_id)
        .first()
    )


def list_redemptions(
    db: Session,
):
    return (
        db.query(Redemption)
        .order_by(Redemption.created_at.desc())
        .all()
    )


def update_status(
    db: Session,
    redemption: Redemption,
    status: str,
):
    redemption.status = status

    db.commit()
    db.refresh(redemption)

    return redemption