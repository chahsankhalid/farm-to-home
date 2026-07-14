from sqlalchemy.orm import Session

from models.customer import Customer


def get_by_shopify_customer_id(
    db: Session,
    shopify_customer_id: str,
):
    return (
        db.query(Customer)
        .filter(Customer.shopify_customer_id == shopify_customer_id)
        .first()
    )


def create_customer(
    db: Session,
    shopify_customer_id: str,
    email: str,
):
    customer = Customer(
        shopify_customer_id=shopify_customer_id,
        email=email,
        current_balance=0,
    )

    db.add(customer)
    db.flush()
    db.refresh(customer)

    return customer


def update_balance(
    db: Session,
    customer: Customer,
    amount: int,
):
    customer.current_balance += amount

    db.flush()
    db.refresh(customer)

    return customer

def deduct_balance(
    db: Session,
    customer: Customer,
    amount: int,
):
    customer.current_balance -= amount

    db.flush()

    db.refresh(customer)

    return customer