from sqlmodel import Field, SQLModel


class BookCocktailRequest(SQLModel):
    """Request schema for booking a cocktail."""

    name: str = Field(min_length=1, description="Name of the cocktail, used for logging")
    price: float = Field(gt=0, description="Amount to subtract")
    is_alcoholic: bool = Field(description="Whether cocktail contains alcohol")


class BalanceUpdateRequest(SQLModel):
    """Request schema for updating balance."""

    amount: float = Field(description="Amount to add (negative to subtract)")
