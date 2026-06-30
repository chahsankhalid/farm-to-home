from recharge import (
    get_customer_by_shopify_id,
    get_extra_subscriptions
)


def get_extras(shopify_customer_id):

    customer = get_customer_by_shopify_id(
        shopify_customer_id
    )

    recharge_customer_id = customer["id"]

    return get_extra_subscriptions(
        recharge_customer_id
    )