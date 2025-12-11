from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user fields shared between create and response."""

    nfc_id: str = Field(index=True, unique=True, min_length=1, description="NFC card ID", primary_key=True)
    is_adult: bool = Field(default=False, description="Whether user is 18 or older")


class User(UserBase, table=True):
    """Database model for users."""

    __tablename__ = "users"  # type: ignore[assignment]

    balance: float = Field(default=0.0, description="User balance")


class UserCreate(UserBase):
    """Schema for creating a new user."""


class UserUpdate(SQLModel):
    """Schema for updating an existing user."""

    is_adult: bool | None = Field(default=None, description="Whether user is 18 or older")
    balance: float | None = Field(default=None, description="User balance")
