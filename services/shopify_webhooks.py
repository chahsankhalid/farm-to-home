from sqlalchemy.orm import Session

from services.seed_rules import calculate_seeds
from services.seeds import award_seeds
from repositories.transaction_repository import get_by_order_id


def process_paid_order(
    db: Session,
    order,
):

    existing_transaction = get_by_order_id(
        db,
        str(order.id),
    )

    if existing_transaction:
        return None

    earned_seeds = calculate_seeds(
        float(order.total_price)
    )

    customer = award_seeds(
        db=db,
        shopify_customer_id=str(order.customer.id),
        email=order.customer.email,
        amount=earned_seeds,
        reason=f"Order #{order.id}",
        order_id=str(order.id),
    )

    return customer