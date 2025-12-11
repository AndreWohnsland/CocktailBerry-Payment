from sqlmodel import Field, SQLModel


class BookCocktailRequest(SQLModel):
    """Request schema for booking a cocktail."""

    nfc_id: str = Field(min_length=1, description="NFC card ID")
    price: float = Field(gt=0, description="Amount to subtract")
    is_alcoholic: bool = Field(description="Whether cocktail contains alcohol")


class BalanceUpdateRequest(SQLModel):
    """Request schema for updating balance."""

    nfc_id: str = Field(min_length=1, description="NFC card ID")
    amount: float = Field(description="Amount to add (negative to subtract)")
