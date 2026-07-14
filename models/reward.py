from sqlalchemy import Boolean, Column, Integer, String

from database import Base


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String,
        nullable=False,
    )

    description = Column(
        String,
        nullable=False,
    )

    seed_cost = Column(
        Integer,
        nullable=False,
    )

    reward_type = Column(
        String,
        nullable=False,
    )

    reward_value = Column(
        String,
        nullable=False,
    )

    active = Column(
        Boolean,
        default=True,
    )