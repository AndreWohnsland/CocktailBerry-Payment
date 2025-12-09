from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.backend.core.nfc_manager import nfc_manager
from src.backend.db.database import get_db, init_db
from src.backend.models.schemas import (
    BalanceUpdateRequest,
    BookCocktailRequest,
    NFCReadResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.backend.service import user_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    init_db()
    nfc_manager.start()
    yield
    # Shutdown
    nfc_manager.stop()


app = FastAPI(
    title="CocktailBerry Payment API",
    description="Payment and balance management service for CocktailBerry",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "CocktailBerry Payment API"}


# NFC endpoints
@app.get("/api/nfc/scan", response_model=NFCReadResponse | None)
def scan_nfc() -> NFCReadResponse | None:
    """Get the latest scanned NFC ID (non-blocking)."""
    nfc_id = nfc_manager.get_latest_nfc_id()
    if nfc_id:
        return NFCReadResponse(nfc_id=nfc_id)
    return None


# User CRUD endpoints
@app.get("/api/users")
def list_users(skip: int = 0, limit: int = 100, db: Annotated[Session, Depends(get_db)] = ...) -> list[UserResponse]:
    """List all users."""
    return user_service.get_users(db, skip=skip, limit=limit)


@app.get("/api/users/{nfc_id}")
def get_user(nfc_id: str, db: Annotated[Session, Depends(get_db)] = ...) -> UserResponse:
    """Get a user by NFC ID."""
    user = user_service.get_user_by_nfc(db, nfc_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.post("/api/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)] = ...) -> UserResponse:
    """Create a new user."""
    return user_service.create_user(db, user)


@app.put("/api/users/{nfc_id}")
def update_user(nfc_id: str, user_update: UserUpdate, db: Annotated[Session, Depends(get_db)] = ...) -> UserResponse:
    """Update a user by NFC ID."""
    return user_service.update_user(db, nfc_id, user_update)


@app.delete("/api/users/{nfc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(nfc_id: str, db: Annotated[Session, Depends(get_db)] = ...) -> None:
    """Delete a user by NFC ID."""
    user_service.delete_user(db, nfc_id)


# Balance and booking endpoints
@app.post("/api/balance/update")
def update_balance(
    balance_request: BalanceUpdateRequest, db: Annotated[Session, Depends(get_db)] = ...
) -> UserResponse:
    """Update user balance (add or subtract)."""
    return user_service.update_balance(db, balance_request.nfc_id, balance_request.amount)


@app.post("/api/cocktails/book")
def book_cocktail(booking: BookCocktailRequest, db: Annotated[Session, Depends(get_db)] = ...) -> UserResponse:
    """Book a cocktail (subtract amount from balance with age verification)."""
    return user_service.book_cocktail(db, booking.nfc_id, booking.amount, booking.is_alcoholic)
