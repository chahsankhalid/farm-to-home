from fastapi import APIRouter

from schemas.shopify_order import ShopifyOrderPaid

from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from services.shopify_webhooks import process_paid_order

router = APIRouter(
    prefix="/webhooks",
    tags=["Shopify Webhooks"],
)


@router.post("/orders-paid")
async def orders_paid(
    order: ShopifyOrderPaid,
    db: Session = Depends(get_db),
):

    customer = process_paid_order(
        db=db,
        order=order,
    )

    if customer is None:
        return {
            "status": "duplicate",
            "message": "Seeds already awarded for this order."
        }

    return {
        "status": "success",
        "customer_id": customer.id,
        "balance": customer.current_balance,
    }