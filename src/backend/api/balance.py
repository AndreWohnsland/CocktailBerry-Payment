from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.backend.models.schemas import BalanceUpdateRequest, BookCocktailRequest
from src.backend.models.user import User
from src.backend.service.user_service import UserService, get_user_service

router = APIRouter(tags=["balance"])


@router.post("/users/{nfc_id}/balance/top-up")
def update_balance(
    nfc_id: str,
    balance_request: BalanceUpdateRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """Top up user balance (add or subtract). nfc_id is provided in the URL path."""
    return user_service.update_balance(nfc_id, balance_request.amount)


@router.post(
    "/users/{nfc_id}/cocktails/book",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User is underage and cannot purchase alcoholic cocktails",
            "content": {
                "application/json": {"example": {"detail": "User is underage and cannot purchase alcoholic cocktails"}}
            },
        },
        status.HTTP_402_PAYMENT_REQUIRED: {
            "description": "Insufficient balance to complete the purchase",
            "content": {
                "application/json": {"example": {"detail": "Insufficient balance. Current: 5.00, Required: 10.00"}}
            },
        },
    },
)
def book_cocktail(
    nfc_id: str,
    booking: BookCocktailRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """Book a cocktail (subtract amount from balance with age verification).

    Deducts the specified amount from the user's balance for a cocktail purchase.
    Performs age verification if the cocktail is alcoholic.
    """
    return user_service.book_cocktail(nfc_id, booking.price, booking.is_alcoholic, booking.name)
