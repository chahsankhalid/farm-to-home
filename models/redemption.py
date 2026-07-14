from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.sql import func

from database import Base


class Redemption(Base):
    __tablename__ = "redemptions"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
    )

    reward_id = Column(
        Integer,
        ForeignKey("rewards.id"),
        nullable=False,
    )

    status = Column(
        String,
        default="completed",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )