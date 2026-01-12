import logging
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from src.backend.constants import MIN_BALANCE
from src.backend.core.config import config
from src.backend.db.database import get_db
from src.backend.models.user import PaymentLog, User, UserCreate, UserUpdate

_logger = logging.getLogger(__name__)


class PaymentLogOptions(StrEnum):
    CREATED = "Created"
    UPDATED = "Updated"
    DELETED = "Deleted"
    TOP_UP = "Top Up"


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
        self.log_payment_event(
            nfc_id=db_user.nfc_id,
            amount=db_user.balance,
            current_balance=db_user.balance,
            description=PaymentLogOptions.CREATED,
            commit=False,
        )
        self.db.commit()
        self.db.refresh(db_user)
        _logger.info(f"Created new user with NFC ID {db_user.nfc_id}")
        return db_user

    def update_user(self, nfc_id: str, user_update: UserUpdate) -> User:
        db_user = self.get_user_by_nfc(nfc_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        db_user.sqlmodel_update(user_update.model_dump(exclude_unset=True))
        self.db.add(db_user)
        self.log_payment_event(
            nfc_id=db_user.nfc_id,
            amount=user_update.balance or 0.0,
            current_balance=db_user.balance,
            description=PaymentLogOptions.UPDATED,
            commit=False,
        )
        self.db.commit()
        self.db.refresh(db_user)
        _logger.info(f"Updated user with NFC ID {db_user.nfc_id}")
        return db_user

    def delete_user(self, nfc_id: str) -> None:
        db_user = self.get_user_by_nfc(nfc_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.db.delete(db_user)
        self.log_payment_event(
            nfc_id=db_user.nfc_id,
            amount=0.0,
            current_balance=0.0,
            description=PaymentLogOptions.DELETED,
            commit=False,
        )
        self.db.commit()
        _logger.info(f"Deleted user with NFC ID {db_user.nfc_id}")

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
        self.log_payment_event(
            nfc_id=db_user.nfc_id,
            amount=amount,
            current_balance=new_balance,
            description=PaymentLogOptions.TOP_UP,
            commit=False,
        )
        self.db.commit()
        self.db.refresh(db_user)
        _logger.info(f"Updated balance for NFC ID {db_user.nfc_id}: {amount:.2f}, new balance: {new_balance:.2f}")
        return db_user

    def book_cocktail(self, nfc_id: str, amount: float, is_alcoholic: bool, name: str) -> User:
        db_user = self.get_user_by_nfc(nfc_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Master key users: log booking but don't deduct balance
        if nfc_id in config.master_keys:
            _logger.info(
                f"Master key booking: '{name}' for NFC ID {nfc_id} (price: {amount:.2f}, alcoholic: {is_alcoholic})"
            )
            return db_user

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
        self.log_payment_event(
            nfc_id=nfc_id,
            amount=-amount,
            current_balance=db_user.balance,
            description=name,
            commit=False,
        )
        self.db.commit()
        self.db.refresh(db_user)
        _logger.info(
            f"Booked cocktail '{name}' for NFC ID {db_user.nfc_id}: -{amount:.2f}, new balance: {db_user.balance:.2f}"
        )
        return db_user

    def log_payment_event(
        self,
        nfc_id: str,
        amount: float,
        current_balance: float,
        description: str,
        commit: bool = True,
    ) -> None:
        transaction = PaymentLog(nfc_id=nfc_id, amount=amount, current_balance=current_balance, description=description)
        self.db.add(transaction)
        if commit:
            self.db.commit()

    def get_payment_logs(self, nfc_id: str) -> list[PaymentLog]:
        return list(
            self.db.exec(
                select(PaymentLog)
                .where(PaymentLog.nfc_id == nfc_id)
                .order_by(PaymentLog.created_at.desc(), PaymentLog.current_balance.asc())  # type: ignore
            ).all()
        )

    def get_all_payment_logs(self) -> list[PaymentLog]:
        return list(self.db.exec(select(PaymentLog)).all())


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    """Dependency to get UserService with injected database session."""
    return UserService(db)
