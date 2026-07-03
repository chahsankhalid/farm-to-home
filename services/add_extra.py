from fastapi import HTTPException

from recharge import (
    get_customer_by_shopify_id,
    get_addresses,
    get_subscriptions,
    create_subscription,
    customer_has_extra_variant
)


def create_extra_subscription(
    shopify_customer_id,
    variant_id
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
    
    if customer_has_extra_variant(
        recharge_customer_id,
        variant_id
    ):
        raise HTTPException(
            status_code=400,
            detail="This extra is already in the subscription."
        )

    addresses = get_addresses(
        recharge_customer_id
    )["addresses"]

    if not addresses:
        raise HTTPException(
            status_code=400,
            detail="Customer has no delivery address."
        )

    subscriptions = get_subscriptions(
        recharge_customer_id
    )["subscriptions"]

    if not subscriptions:
        raise HTTPException(
            status_code=400,
            detail="Customer has no active subscription."
        )

    address = addresses[0]
    subscription = subscriptions[0]

    subscription = create_subscription(
        address_id=address["id"],
        variant_id=variant_id,
        next_charge_date=subscription["next_charge_scheduled_at"]
    )

    return {
        "success": True,
        "subscription": subscription["subscription"]
    }