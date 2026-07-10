from fastapi import HTTPException

from recharge import (
    get_customer_by_shopify_id,
    get_addresses,
    get_subscriptions,
    create_subscription,
    get_extra_subscription_by_variant,
    update_subscription_quantity
)


def create_extra_subscription(
    shopify_customer_id,
    variant_id,
    quantity=1
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
    
    existing = get_extra_subscription_by_variant(
    recharge_customer_id,
    variant_id
)

    if existing:

        updated = update_subscription_quantity(
            existing["id"],
            quantity
        )

        return {
            "success": True,
            "subscription": updated["subscription"]
        }

    addresses = get_addresses(recharge_customer_id).get("addresses", [])

    if not addresses:
        raise HTTPException(
            status_code=400,
            detail="Customer has no delivery address."
        )

    subscriptions = get_subscriptions(recharge_customer_id).get("subscriptions", [])

    if not subscriptions:
        raise HTTPException(
            status_code=400,
            detail="Customer has no active subscription."
        )

    address = next(iter(addresses), None)
    subscription = next(iter(subscriptions), None)

    new_subscription = create_subscription(
        address_id=address["id"],
        variant_id=variant_id,
        quantity=quantity,
        next_charge_date=subscription["next_charge_scheduled_at"]
    )

    return {
        "success": True,
        "subscription": new_subscription["subscription"]
    }