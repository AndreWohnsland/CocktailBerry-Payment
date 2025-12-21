from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.backend.models.user import PaymentLog, User, UserCreate, UserUpdate
from src.backend.service.user_service import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    skip: int = 0,
    limit: int = 1000,
) -> list[User]:
    """List all users."""
    return user_service.get_users(skip=skip, limit=limit)


@router.get("/{nfc_id}")
def get_user(nfc_id: str, user_service: Annotated[UserService, Depends(get_user_service)]) -> User:
    """Get a user by NFC ID."""
    user = user_service.get_user_by_nfc(nfc_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, user_service: Annotated[UserService, Depends(get_user_service)]) -> User:
    """Create a new user."""
    return user_service.create_user(user)


@router.put("/{nfc_id}")
def update_user(
    nfc_id: str,
    user_update: UserUpdate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """Update a user by NFC ID."""
    return user_service.update_user(nfc_id, user_update)


@router.delete("/{nfc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(nfc_id: str, user_service: Annotated[UserService, Depends(get_user_service)]) -> None:
    """Delete a user by NFC ID."""
    user_service.delete_user(nfc_id)


@router.get("/{nfc_id}/history", tags=["history"])
def get_user_history(nfc_id: str, user_service: Annotated[UserService, Depends(get_user_service)]) -> list[PaymentLog]:
    """Get transaction history for a user by NFC ID."""
    logs = user_service.get_payment_logs(nfc_id)
    if not logs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No logs for {nfc_id} found")
    return logs
