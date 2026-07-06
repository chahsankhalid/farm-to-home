from fastapi import HTTPException

from recharge import (
    get_customer_by_shopify_id,
    subscription_belongs_to_customer,
    delete_subscription
)


def remove_extra(shopify_customer_id, subscription_id):

    customer = get_customer_by_shopify_id(shopify_customer_id)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Recharge customer not found."
        )

    recharge_customer_id = customer["id"]

    if not subscription_belongs_to_customer(
        recharge_customer_id,
        subscription_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied."
        )

    return delete_subscription(subscription_id)