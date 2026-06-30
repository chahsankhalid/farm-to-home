from fastapi import APIRouter

from services.add_extra import create_extra_subscription
from services.remove_extra import remove_extra
from services.get_extras import get_extras

router = APIRouter()


@router.post("/add-extra")
def add_extra(data: dict):

    return create_extra_subscription(
        shopify_customer_id=data["shopify_customer_id"],
        variant_id=data["variant_id"]
    )


@router.delete("/remove-extra/{subscription_id}")
def delete_extra(subscription_id: int):

    return remove_extra(subscription_id)


@router.get("/extras/{shopify_customer_id}")
def extras(shopify_customer_id: str):

    return get_extras(shopify_customer_id)