from fastapi import HTTPException

from recharge import (
    get_customer_by_shopify_id,
    get_extra_subscriptions
)


def get_extras(shopify_customer_id):

    customer = get_customer_by_shopify_id(
        shopify_customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Recharge customer not found."
        )

    recharge_customer_id = customer["id"]

    return get_extra_subscriptions(
        recharge_customer_id
    )