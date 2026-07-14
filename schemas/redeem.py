from pydantic import BaseModel


class RedeemRewardRequest(BaseModel):
    shopify_customer_id: str
    reward_id: int