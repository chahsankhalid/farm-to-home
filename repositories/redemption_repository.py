from sqlalchemy.orm import Session

from models.redemption import Redemption


def create_redemption(
    db: Session,
    customer_id: int,
    reward_id: int,
):
    redemption = Redemption(
        customer_id=customer_id,
        reward_id=reward_id,
        status="completed",
    )

    db.add(redemption)
    db.flush()
    db.refresh(redemption)

    return redemption