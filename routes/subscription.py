from fastapi import APIRouter
from pydantic import BaseModel

from services.add_extra import create_extra_subscription
from services.remove_extra import remove_extra
from services.get_extras import get_extras
from services.update_extra import update_extra

router = APIRouter()


class AddExtraRequest(BaseModel):
    shopify_customer_id: str
    variant_id: int
    quantity: int = 1


@router.post("/add-extra")
def add_extra(data: AddExtraRequest):

    return create_extra_subscription(
        shopify_customer_id=data.shopify_customer_id,
        variant_id=data.variant_id,
        quantity=data.quantity
    )


class RemoveExtraRequest(BaseModel):
    shopify_customer_id: str
    subscription_id: int


@router.delete("/remove-extra")
def delete_extra(data: RemoveExtraRequest):

    return remove_extra(
        shopify_customer_id=data.shopify_customer_id,
        subscription_id=data.subscription_id
    )


class UpdateExtraRequest(BaseModel):
    shopify_customer_id: str
    subscription_id: int
    quantity: int


@router.patch("/update-extra")
def patch_extra(data: UpdateExtraRequest):

    return update_extra(
        shopify_customer_id=data.shopify_customer_id,
        subscription_id=data.subscription_id,
        quantity=data.quantity
    )


@router.get("/extras/{shopify_customer_id}")
def extras(shopify_customer_id: str):

    return get_extras(shopify_customer_id)