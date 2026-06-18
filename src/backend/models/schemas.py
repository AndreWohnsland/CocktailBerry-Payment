from sqlmodel import Field, SQLModel

from src.backend.models.types import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS, Money


class BookCocktailRequest(SQLModel):
    """Request schema for booking a cocktail."""

    name: str = Field(min_length=1, description="Name of the cocktail, used for logging")
    price: Money = Field(
        ge=0,
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        description="Amount to subtract",
    )
    is_alcoholic: bool = Field(description="Whether cocktail contains alcohol")


class BalanceUpdateRequest(SQLModel):
    """Request schema for updating balance."""

    amount: Money = Field(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        description="Amount to add (negative to subtract)",
    )
