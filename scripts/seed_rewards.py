from database import SessionLocal
from models.reward import Reward

db = SessionLocal()

rewards = [
    {
        "name": "We plant a tree",
        "description": "A real tree planted at Quinta Terramay in your name.",
        "seed_cost": 100,
        "reward_type": "tree",
        "reward_value": "TREE",
    },
    {
        "name": "Community spotlight",
        "description": "Your business or project featured on Farm to Home's Instagram and Facebook.",
        "seed_cost": 200,
        "reward_type": "community",
        "reward_value": "COMMUNITY",
    },
    {
        "name": "Free week of The Weekly",
        "description": "One complimentary delivery — 1 bread, 2 soups, 2 mains.",
        "seed_cost": 500,
        "reward_type": "subscription",
        "reward_value": "FREE_WEEKLY",
    },
    {
        "name": "Private farm tour & lunch",
        "description": "Tour of Quinta Terramay and lunch at our restaurant with wine (outside summer season).",
        "seed_cost": 1000,
        "reward_type": "experience",
        "reward_value": "FARM_TOUR",
    },
]

existing_rewards = (
    db.query(Reward)
    .order_by(Reward.id)
    .all()
)

for index, reward_data in enumerate(rewards):

    if index < len(existing_rewards):
        reward = existing_rewards[index]

        reward.name = reward_data["name"]
        reward.description = reward_data["description"]
        reward.seed_cost = reward_data["seed_cost"]
        reward.reward_type = reward_data["reward_type"]
        reward.reward_value = reward_data["reward_value"]

    else:
        db.add(Reward(**reward_data))

db.commit()
db.close()

print("✅ Rewards updated successfully!")