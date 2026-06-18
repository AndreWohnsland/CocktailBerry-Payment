from datetime import datetime
from decimal import Decimal

from pydantic import field_serializer
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel

from src.backend.models.types import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS, Money


class UserBase(SQLModel):
    """Base user fields shared between create and response."""

    nfc_id: str = Field(index=True, unique=True, min_length=1, description="NFC card ID", primary_key=True)
    is_adult: bool = Field(default=False, description="Whether user is 18 or older")
    balance: Money = Field(
        default=Decimal("0"),
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        description="User balance",
    )


class User(UserBase, table=True):
    """Database model for users."""

    __tablename__ = "users"  # type: ignore[assignment]


class UserCreate(UserBase):
    """Schema for creating a new user."""


class UserUpdate(SQLModel):
    """Schema for updating an existing user."""

    is_adult: bool | None = Field(default=None, description="Whether user is 18 or older")
    balance: Money | None = Field(
        default=None,
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        description="User balance",
    )


class PaymentLog(SQLModel, table=True):
    """Database model for payment logs."""

    __tablename__ = "payment_logs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    nfc_id: str = Field(index=True, description="NFC card ID")
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    amount: Money = Field(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        description="Transaction amount",
    )
    current_balance: Money = Field(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        description="User balance after the transaction",
    )
    description: str = Field(description="Description of the transaction")

    @field_serializer("created_at", when_used="json")
    def _serialize_created_at(self, value: datetime | None) -> str | None:
        """Render the timestamp as 'YYYY-MM-DD HH:MM:SS' in JSON output."""
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None
