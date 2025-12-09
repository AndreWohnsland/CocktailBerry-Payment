from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.backend.constants import MIN_BALANCE
from src.backend.models.schemas import UserCreate, UserUpdate
from src.backend.models.user import User


def get_user_by_nfc(db: Session, nfc_id: str) -> User | None:
    return db.query(User).filter(User.nfc_id == nfc_id).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    existing_user = get_user_by_nfc(db, user.nfc_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with NFC ID {user.nfc_id} already exists",
        )
    db_user = User(nfc_id=user.nfc_id, name=user.name, is_adult=user.is_adult, balance=0.0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, nfc_id: str, user_update: UserUpdate) -> User:
    db_user = get_user_by_nfc(db, nfc_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.is_adult is not None:
        db_user.is_adult = user_update.is_adult
    if user_update.balance is not None:
        db_user.balance = user_update.balance

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, nfc_id: str) -> None:
    db_user = get_user_by_nfc(db, nfc_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(db_user)
    db.commit()


def update_balance(db: Session, nfc_id: str, amount: float) -> User:
    db_user = get_user_by_nfc(db, nfc_id)
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
    db.commit()
    db.refresh(db_user)
    return db_user


def book_cocktail(db: Session, nfc_id: str, amount: float, is_alcoholic: bool) -> User:
    db_user = get_user_by_nfc(db, nfc_id)
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
    db.commit()
    db.refresh(db_user)
    return db_user
