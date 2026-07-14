from sqlalchemy.orm import Session

from recharge import get_charges, get_customer


from repositories.transaction_repository import (
    get_by_recharge_charge_id,
)

from services.seeds import (
    award_seeds,
    get_or_create_customer,
)
from services.seed_rules import calculate_seeds


def sync_recharge_rewards(db: Session):

    charges = get_charges()["charges"]

    awarded = 0

    for charge in charges:

        try:

            # Skip if already processed
            if get_by_recharge_charge_id(
                db,
                str(charge["id"]),
            ):
                continue

            # Get Recharge customer
            recharge_customer = get_customer(
                charge["customer_id"]
            )["customer"]

            # Create or fetch our local customer
            customer = get_or_create_customer(
                db=db,
                shopify_customer_id=recharge_customer["shopify_customer_id"],
                email=recharge_customer["email"],
            )

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

        except Exception as e:
            continue

    return {
        "status": "success",
        "awarded": awarded,
    }