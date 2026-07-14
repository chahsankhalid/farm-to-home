from sqlalchemy.orm import Session

from repositories.transaction_repository import get_by_order_id
from services.seed_rules import calculate_seeds
from services.seeds import award_seeds


def process_paid_order(
    db: Session,
    order,
):

    if order.financial_status.lower() != "paid":
        return None

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
        reason=f"Shopify Order #{order.id}",
        order_id=str(order.id),
    )

    return customer