from sqlalchemy.orm import Session

from repositories.transaction_repository import get_by_order_id
from services.seed_rules import calculate_seeds
from services.seeds import award_seeds


def process_paid_order(
    db: Session,
    order,
):

    print(f"Order ID: {order.id}")
    print(f"Customer ID: {order.customer.id}")
    print(f"Email: {order.customer.email}")
    print(f"Total: {order.total_price}")

    existing_transaction = get_by_order_id(
        db,
        str(order.id),
    )

    if existing_transaction:
        print("Duplicate order")
        return None

    earned_seeds = calculate_seeds(
        float(order.total_price)
    )

    print(f"Seeds awarded: {earned_seeds}")

    customer = award_seeds(
        db=db,
        shopify_customer_id=str(order.customer.id),
        email=order.customer.email,
        amount=earned_seeds,
        reason=f"Shopify Order #{order.id}",
        order_id=str(order.id),
    )

    print(f"New balance: {customer.current_balance}")

    return customer