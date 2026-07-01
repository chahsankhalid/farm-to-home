from recharge import (
    get_customer_by_shopify_id,
    get_addresses,
    get_subscriptions,
    create_subscription
)

def create_extra_subscription(
    shopify_customer_id,
    variant_id
):

    customer = get_customer_by_shopify_id(
        shopify_customer_id
    )

    recharge_customer_id = customer["id"]

    address = get_addresses(
        recharge_customer_id
    )["addresses"][0]

    subscription = get_subscriptions(
        recharge_customer_id
    )["subscriptions"][0]

    subscription = create_subscription(
        address_id=address["id"],
        variant_id=variant_id,
        next_charge_date=subscription["next_charge_scheduled_at"]
    )

    return {
        "success": True,
        "subscription": subscription["subscription"]
    }