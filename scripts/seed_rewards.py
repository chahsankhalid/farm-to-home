from database import SessionLocal
from models.reward import Reward

db = SessionLocal()

rewards = [
    Reward(
        name="Free Soup",
        description="Redeem one free soup",
        seed_cost=100,
        reward_type="free_product",
        reward_value="FREE_SOUP",
    ),
    Reward(
        name="Free Bread",
        description="Redeem one free bread",
        seed_cost=150,
        reward_type="free_product",
        reward_value="FREE_BREAD",
    ),
    Reward(
        name="10% Discount",
        description="10% off next order",
        seed_cost=300,
        reward_type="discount",
        reward_value="10_PERCENT",
    ),
]

for reward in rewards:
    exists = (
        db.query(Reward)
        .filter(Reward.name == reward.name)
        .first()
    )

    if not exists:
        db.add(reward)

db.commit()

print("Rewards seeded successfully!")