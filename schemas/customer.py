from pydantic import BaseModel


class CustomerRequest(BaseModel):
    shopify_customer_id: str
    email: str