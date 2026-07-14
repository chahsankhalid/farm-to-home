from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    shopify_customer_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String,
        nullable=False
    )

    current_balance = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    transactions = relationship(
        "SeedTransaction",
        back_populates="customer",
        cascade="all, delete-orphan",
    )