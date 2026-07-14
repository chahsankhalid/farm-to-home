from sqlalchemy.orm import Session

from repositories.customer_repository import (
    get_by_shopify_customer_id,
)

from repositories.transaction_repository import (
    get_customer_transactions,
)


def get_history(
    db: Session,
    shopify_customer_id: str,
):
    customer = get_by_shopify_customer_id(
        db,
        shopify_customer_id,
    )

    if not customer:
        return []

    return get_customer_transactions(
        db,
        customer.id,
    )