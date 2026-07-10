import requests
from config import BASE_URL, HEADERS
from fastapi import HTTPException


def get_subscriptions(customer_id):

    response = requests.get(
        f"{BASE_URL}/subscriptions",
        headers=HEADERS,
        params={
            "customer_id": customer_id,
            "limit": 50
        }
    )

    response.raise_for_status()

    return response.json()


def get_addresses(customer_id):

    response = requests.get(
        f"{BASE_URL}/addresses",
        headers=HEADERS,
        params={
            "customer_id": customer_id
        }
    )

    response.raise_for_status()

    return response.json()


def create_subscription(address_id, variant_id, quantity, next_charge_date):

    payload = {
        "address_id": address_id,
        "shopify_variant_id": int(variant_id),
        "quantity": int(quantity),

        "order_interval_unit": "week",
        "order_interval_frequency": "1",
        "charge_interval_frequency": "1",

        "next_charge_scheduled_at": next_charge_date,

        "properties": [
            {
                "name": "subscription_type",
                "value": "extra"
            },
            {
                "name": "subscriber_discount",
                "value": "25"
            }
        ]
    }

    response = requests.post(
        f"{BASE_URL}/subscriptions",
        headers=HEADERS,
        json=payload
    )

    response.raise_for_status()

    return response.json()

def delete_subscription(subscription_id):

    response = requests.delete(
        f"{BASE_URL}/subscriptions/{subscription_id}",
        headers=HEADERS
    )
    response.raise_for_status()

    return {
        "success": True
    }

def get_extra_subscriptions(customer_id):

    subscriptions = get_subscriptions(customer_id)["subscriptions"]

    extras = []

    for subscription in subscriptions:
        properties = subscription.get("properties", [])
        is_extra = False
        for prop in properties:
            if (
                prop["name"] == "subscription_type"
                and prop["value"] == "extra"
            ):
                is_extra = True
                break

        if is_extra:

            extras.append({
                "subscription_id": subscription["id"],
                "variant_id": subscription["shopify_variant_id"],
                "title": subscription["product_title"],
                "price": subscription["price"],
                "quantity": subscription.get("quantity", 1)
            })

    return extras

def get_customer_by_shopify_id(shopify_customer_id):

    response = requests.get(
        f"{BASE_URL}/customers",
        headers=HEADERS,
        params={
            "shopify_customer_id": shopify_customer_id
        }
    )

    response.raise_for_status()

    customers = response.json()["customers"]

    if not customers:
        raise HTTPException(
            status_code=404,
            detail="Recharge customer not found."
        )

    return customers[0]

def subscription_belongs_to_customer(recharge_customer_id, subscription_id):

    subscriptions = get_subscriptions(
        recharge_customer_id
    )["subscriptions"]

    return any(
        subscription["id"] == int(subscription_id)
        for subscription in subscriptions
    )
    
def customer_has_extra_variant(customer_id, variant_id):

    subscriptions = get_subscriptions(customer_id)["subscriptions"]

    return any(
        subscription["shopify_variant_id"] == int(variant_id)
        for subscription in subscriptions
    )
    
def update_subscription_quantity(subscription_id, quantity):

    payload = {
        "quantity": int(quantity)
    }

    response = requests.put(
        f"{BASE_URL}/subscriptions/{subscription_id}",
        headers=HEADERS,
        json=payload
    )

    response.raise_for_status()

    return response.json()