from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from src.backend.constants import MIN_BALANCE
from src.backend.db.database import get_db
from src.backend.models.user import User, UserCreate, UserUpdate


class UserService:
    """Service for managing users."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_nfc(self, nfc_id: str) -> User | None:
        return self.db.exec(select(User).where(User.nfc_id == nfc_id)).first()

    def get_users(self, skip: int = 0, limit: int = 1000) -> list[User]:
        return list(self.db.exec(select(User).offset(skip).limit(limit)).all())

    def create_user(self, user: UserCreate) -> User:
        existing_user = self.get_user_by_nfc(user.nfc_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with NFC ID {user.nfc_id} already exists",
            )
        db_user = User.model_validate(user)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, nfc_id: str, user_update: UserUpdate) -> User:
        db_user = self.get_user_by_nfc(nfc_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        db_user.sqlmodel_update(user_update.model_dump(exclude_unset=True))
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, nfc_id: str) -> None:
        db_user = self.get_user_by_nfc(nfc_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.db.delete(db_user)
        self.db.commit()

    def update_balance(self, nfc_id: str, amount: float) -> User:
        db_user = self.get_user_by_nfc(nfc_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        new_balance = db_user.balance + amount
        # Prevent extreme negative balances for data integrity
        if new_balance < MIN_BALANCE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Balance cannot go below €{MIN_BALANCE:.2f}. "
                    f"Current: {db_user.balance:.2f}, Requested: {amount:.2f}"
                ),
            )

        db_user.balance = new_balance
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def book_cocktail(self, nfc_id: str, amount: float, is_alcoholic: bool) -> User:
        db_user = self.get_user_by_nfc(nfc_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if is_alcoholic and not db_user.is_adult:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is underage and cannot purchase alcoholic cocktails",
            )

        if db_user.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient balance. Current: {db_user.balance:.2f}, Required: {amount:.2f}",
            )

        db_user.balance -= amount
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    """Dependency to get UserService with injected database session."""
    return UserService(db)
