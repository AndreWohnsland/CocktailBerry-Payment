from pydantic import BaseModel, Field


class UserBase(BaseModel):
    nfc_id: str = Field(..., min_length=1, description="NFC card ID")
    name: str = Field(..., min_length=1, description="User name")
    is_adult: bool = Field(default=False, description="Whether user is 18 or older")


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, description="User name")
    is_adult: bool | None = Field(None, description="Whether user is 18 or older")
    balance: float | None = Field(None, description="User balance")


class UserResponse(UserBase):
    id: int
    balance: float

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class BookCocktailRequest(BaseModel):
    nfc_id: str = Field(..., min_length=1, description="NFC card ID")
    amount: float = Field(..., gt=0, description="Amount to subtract")
    is_alcoholic: bool = Field(..., description="Whether cocktail contains alcohol")


class BalanceUpdateRequest(BaseModel):
    nfc_id: str = Field(..., min_length=1, description="NFC card ID")
    amount: float = Field(..., description="Amount to add (negative to subtract)")


class NFCReadResponse(BaseModel):
    nfc_id: str
