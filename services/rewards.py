from sqlalchemy.orm import Session

from repositories.reward_repository import get_active_rewards


def list_rewards(db: Session):
    return get_active_rewards(db)