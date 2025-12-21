from datetime import datetime

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user fields shared between create and response."""

    nfc_id: str = Field(index=True, unique=True, min_length=1, description="NFC card ID", primary_key=True)
    is_adult: bool = Field(default=False, description="Whether user is 18 or older")
    balance: float = Field(default=0.0, description="User balance")


class User(UserBase, table=True):
    """Database model for users."""

    __tablename__ = "users"  # type: ignore[assignment]


class UserCreate(UserBase):
    """Schema for creating a new user."""


class UserUpdate(SQLModel):
    """Schema for updating an existing user."""

    is_adult: bool | None = Field(default=None, description="Whether user is 18 or older")
    balance: float | None = Field(default=None, description="User balance")


class PaymentLog(SQLModel, table=True):
    """Database model for payment logs."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")})  # type: ignore

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
    amount: float = Field(description="Transaction amount")
    current_balance: float = Field(description="User balance after the transaction")
    description: str = Field(description="Description of the transaction")
