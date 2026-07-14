from sqlalchemy.orm import Session

from repositories.customer_repository import get_by_shopify_customer_id
from repositories.reward_repository import get_active_rewards
from repositories.transaction_repository import get_customer_transactions


def get_dashboard(
    db: Session,
    shopify_customer_id: str,
):
    print("🔍 Looking for customer:", shopify_customer_id)

    customer = get_by_shopify_customer_id(
        db,
        shopify_customer_id,
    )

    print("🔍 Customer found:", customer)

    if customer is None:
        print("❌ Customer NOT found")
        return None

    rewards = get_active_rewards(db)
    print("✅ Rewards:", len(rewards))

    history = get_customer_transactions(
        db,
        customer.id,
    )

    print("✅ History:", len(history))

    return {
        "customer": customer,
        "rewards": rewards,
        "history": history,
    }