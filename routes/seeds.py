from fastapi import APIRouter
from services.db_test import test_database_connection

from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from services.seeds import get_customer_balance

from schemas.customer import CustomerRequest
from services.seeds import get_or_create_customer

from schemas.award import AwardSeedsRequest
from services.seeds import award_seeds

from services.rewards import list_rewards

from schemas.redeem import RedeemRewardRequest
from services.redemption import redeem_reward
from services.history import get_history
from services.dashboard import get_dashboard
from models.reward import Reward

print("✅ SEEDS ROUTER LOADED") 

router = APIRouter(
    prefix="/seeds",
    tags=["Terramay Seeds"]
)

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Terramay Seeds API"
    }

@router.get("/db-test")
def database_test():
    connected = test_database_connection()

    if connected:
        return {"database": "connected"}

    return {"database": "failed"}

@router.get("/balance/{shopify_customer_id}")
def balance(
    shopify_customer_id: str,
    db: Session = Depends(get_db),
):
    balance = get_customer_balance(db, shopify_customer_id)

    return {
        "shopify_customer_id": shopify_customer_id,
        "balance": balance,
    }
    
@router.post("/customer")
def create_customer(
    request: CustomerRequest,
    db: Session = Depends(get_db),
):
    customer = get_or_create_customer(
        db=db,
        shopify_customer_id=request.shopify_customer_id,
        email=request.email,
    )

    return {
        "id": customer.id,
        "shopify_customer_id": customer.shopify_customer_id,
        "email": customer.email,
        "balance": customer.current_balance,
    }
    
@router.post("/award")
def award(
    request: AwardSeedsRequest,
    db: Session = Depends(get_db),
):
    customer = award_seeds(
        db=db,
        shopify_customer_id=request.shopify_customer_id,
        email=request.email,
        amount=request.amount,
        reason=request.reason,
        order_id=request.order_id,
    )

    return {
        "customer_id": customer.id,
        "shopify_customer_id": customer.shopify_customer_id,
        "balance": customer.current_balance,
    }
    
@router.get("/rewards")
def rewards(
    db: Session = Depends(get_db),
):
    rewards = list_rewards(db)

    return rewards

@router.post("/redeem")
def redeem(
    request: RedeemRewardRequest,
    db: Session = Depends(get_db),
):
    customer = redeem_reward(
        db=db,
        shopify_customer_id=request.shopify_customer_id,
        reward_id=request.reward_id,
    )

    return {
        "status": "success",
        "customer_id": customer.id,
        "balance": customer.current_balance,
    }
    
@router.get("/history/{shopify_customer_id}")
def history(
    shopify_customer_id: str,
    db: Session = Depends(get_db),
):
    history = get_history(
        db,
        shopify_customer_id,
    )

    return history

@router.get("/dashboard/{shopify_customer_id}")
def dashboard(
    shopify_customer_id: str,
    db: Session = Depends(get_db),
):
    dashboard = get_dashboard(
        db,
        shopify_customer_id,
    )

    if dashboard is None:
        return {
            "balance": 0,
            "rewards": list_rewards(db),
            "history": [],
        }

    return {
        "balance": dashboard["customer"].current_balance,
        "rewards": dashboard["rewards"],
        "history": dashboard["history"],
    }

@router.post("/seed-rewards")
def seed_rewards(db: Session = Depends(get_db)):
    rewards = [
        {
            "name": "Free Soup",
            "description": "Redeem one free soup",
            "seed_cost": 100,
            "reward_type": "free_product",
            "reward_value": "FREE_SOUP",
        },
        {
            "name": "Free Bread",
            "description": "Redeem one free bread",
            "seed_cost": 150,
            "reward_type": "free_product",
            "reward_value": "FREE_BREAD",
        },
        {
            "name": "10% Discount",
            "description": "10% off next order",
            "seed_cost": 300,
            "reward_type": "discount",
            "reward_value": "10_PERCENT",
        },
    ]

    added = 0

    for item in rewards:
        exists = (
            db.query(Reward)
            .filter(Reward.name == item["name"])
            .first()
        )

        if not exists:
            db.add(Reward(**item))
            added += 1

    db.commit()

    return {
        "status": "success",
        "added": added,
    }