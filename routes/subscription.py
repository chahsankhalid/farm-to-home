from fastapi import APIRouter
from pydantic import BaseModel

from services.add_extra import create_extra_subscription
from services.remove_extra import remove_extra
from services.get_extras import get_extras

router = APIRouter()

class AddExtraRequest(BaseModel):
    shopify_customer_id: str
    variant_id: int
    
    
@router.post("/add-extra")
def add_extra(data: AddExtraRequest):

    return create_extra_subscription(
        shopify_customer_id=data.shopify_customer_id,
        variant_id=data.variant_id
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


@router.get("/extras/{shopify_customer_id}")
def extras(shopify_customer_id: str):

    return get_extras(shopify_customer_id)