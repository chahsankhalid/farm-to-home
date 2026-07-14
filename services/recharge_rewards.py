from sqlalchemy.orm import Session

from recharge import get_charges

from repositories.customer_repository import get_by_email
from repositories.transaction_repository import (
    get_by_recharge_charge_id,
)

from services.seeds import award_seeds
from services.seed_rules import calculate_seeds


def sync_recharge_rewards(db: Session):

    charges = get_charges()["charges"]

    awarded = 0

    for charge in charges:

        # Already processed?
        if get_by_recharge_charge_id(
            db,
            str(charge["id"]),
        ):
            continue

        # Find our customer using email
        customer = get_by_email(
            db,
            charge["email"],
        )

        if not customer:
            continue

        # Business rule:
        # 1€ spent = 1 Seed
        total = float(charge["total_line_items_price"])

        seeds = calculate_seeds(total)

        award_seeds(
            db=db,
            shopify_customer_id=customer.shopify_customer_id,
            email=customer.email,
            amount=seeds,
            reason=f"Recharge Charge #{charge['id']}",
            recharge_charge_id=str(charge["id"]),
        )

        awarded += 1

    return {
        "status": "success",
        "awarded": awarded,
    }