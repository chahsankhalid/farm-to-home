from fastapi import HTTPException

from recharge import (
    get_customer_by_shopify_id,
    subscription_belongs_to_customer,
    update_subscription_quantity
)


def update_extra(
    shopify_customer_id,
    subscription_id,
    quantity
):

    customer = get_customer_by_shopify_id(
        shopify_customer_id
    )

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

    subscription = update_subscription_quantity(
        subscription_id,
        quantity
    )

    return {
        "success": True,
        "subscription": subscription
    }