from pydantic import BaseModel


class AwardSeedsRequest(BaseModel):
    shopify_customer_id: str
    email: str
    amount: int
    reason: str
    order_id: str | None = None