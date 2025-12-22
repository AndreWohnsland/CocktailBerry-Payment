"""Tests for user service layer."""

import pytest
from fastapi import HTTPException, status

from src.backend.constants import MIN_BALANCE
from src.backend.models.user import User, UserCreate, UserUpdate
from src.backend.service.user_service import PaymentLogOptions, UserService


class TestGetUser:
    """Tests for getting users."""

    def test_get_user_by_nfc_success(self, user_service: UserService, sample_user: User) -> None:
        """Test getting a user by NFC ID."""
        user = user_service.get_user_by_nfc(sample_user.nfc_id)
        assert user is not None
        assert user.nfc_id == sample_user.nfc_id

    def test_get_user_by_nfc_not_found(self, user_service: UserService) -> None:
        """Test getting a non-existent user by NFC ID."""
        user = user_service.get_user_by_nfc("NONEXISTENT")
        assert user is None

    def test_get_users_list(self, user_service: UserService, sample_user: User, sample_minor: User) -> None:
        """Test getting list of users."""
        users = user_service.get_users()
        assert len(users) >= 2  # noqa: PLR2004
        nfc_ids = [u.nfc_id for u in users]
        assert sample_user.nfc_id in nfc_ids
        assert sample_minor.nfc_id in nfc_ids

    def test_get_users_with_pagination(self, user_service: UserService, sample_user: User) -> None:
        """Test getting users with pagination."""
        users = user_service.get_users(skip=0, limit=1)
        assert len(users) == 1


class TestCreateUser:
    """Tests for creating users."""

    def test_create_user_success(self, user_service: UserService) -> None:
        """Test creating a new user."""
        user_create = UserCreate(nfc_id="NEW123", is_adult=True)
        user = user_service.create_user(user_create)

        assert user.nfc_id == "NEW123"
        assert user.is_adult is True
        assert user.balance == 0.0

        log = next(log for log in user_service.get_payment_logs(user.nfc_id) if log.nfc_id == user.nfc_id)
        assert log is not None
        assert log.description == PaymentLogOptions.CREATED
        assert log.amount == 0.0

    def test_create_user_duplicate_nfc(self, user_service: UserService, sample_user: User) -> None:
        """Test creating a user with duplicate NFC ID raises exception."""
        user_create = UserCreate(nfc_id=sample_user.nfc_id, is_adult=False)

        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(user_create)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in exc_info.value.detail

    def test_create_user_minor(self, user_service: UserService) -> None:
        """Test creating a minor user."""
        user_create = UserCreate(nfc_id="MINOR789", is_adult=False)
        user = user_service.create_user(user_create)

        assert user.is_adult is False
        assert user.balance == 0.0


class TestUpdateUser:
    """Tests for updating users."""

    def test_update_user_adult_status(self, user_service: UserService, sample_minor: User) -> None:
        """Test updating user adult status."""
        user_update = UserUpdate(is_adult=True)
        user = user_service.update_user(sample_minor.nfc_id, user_update)

        assert user.is_adult is True

    def test_update_user_balance(self, user_service: UserService, sample_user: User) -> None:
        """Test updating user balance directly."""
        new_balance = 100.0
        user_update = UserUpdate(balance=new_balance)
        user = user_service.update_user(sample_user.nfc_id, user_update)

        assert user.balance == new_balance

    def test_update_user_not_found(self, user_service: UserService) -> None:
        """Test updating non-existent user raises exception."""
        user_update = UserUpdate(is_adult=True)

        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user("NONEXISTENT", user_update)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user_multiple_fields(self, user_service: UserService, sample_user: User) -> None:
        """Test updating multiple user fields at once."""
        new_balance = 75.0
        user_update = UserUpdate(is_adult=False, balance=new_balance)
        user = user_service.update_user(sample_user.nfc_id, user_update)

        assert user.is_adult is False
        assert user.balance == new_balance

        log = next(log for log in user_service.get_payment_logs(user.nfc_id) if log.nfc_id == user.nfc_id)
        assert log is not None
        assert log.description == PaymentLogOptions.UPDATED
        assert log.amount == new_balance


class TestDeleteUser:
    """Tests for deleting users."""

    def test_delete_user_success(self, user_service: UserService, sample_user: User) -> None:
        """Test deleting a user."""
        user_service.delete_user(sample_user.nfc_id)

        log = next(log for log in user_service.get_payment_logs(sample_user.nfc_id) if log.nfc_id == sample_user.nfc_id)
        assert log is not None
        assert log.description == PaymentLogOptions.DELETED

    def test_delete_user_not_found(self, user_service: UserService) -> None:
        """Test deleting non-existent user raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            user_service.delete_user("NONEXISTENT")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateBalance:
    """Tests for updating user balance."""

    def test_update_balance_add(self, user_service: UserService, sample_user: User) -> None:
        """Test adding to user balance."""
        original_balance = sample_user.balance
        user = user_service.update_balance(sample_user.nfc_id, 25.0)

        assert user.balance == original_balance + 25.0

        log = next(log for log in user_service.get_payment_logs(user.nfc_id) if log.nfc_id == user.nfc_id)
        assert log is not None
        assert log.description == PaymentLogOptions.TOP_UP
        assert log.amount == 25.0  # noqa: PLR2004

    def test_update_balance_subtract(self, user_service: UserService, sample_user: User) -> None:
        """Test subtracting from user balance."""
        original_balance = sample_user.balance
        user = user_service.update_balance(sample_user.nfc_id, -10.0)

        assert user.balance == original_balance - 10.0

    def test_update_balance_below_minimum(self, user_service: UserService, sample_user: User) -> None:
        """Test updating balance below minimum raises exception."""
        # Try to subtract enough to go below MIN_BALANCE
        amount = sample_user.balance + abs(MIN_BALANCE) + 100.0

        with pytest.raises(HTTPException) as exc_info:
            user_service.update_balance(sample_user.nfc_id, -amount)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot go below" in exc_info.value.detail

    def test_update_balance_user_not_found(self, user_service: UserService) -> None:
        """Test updating balance for non-existent user raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_balance("NONEXISTENT", 10.0)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestBookCocktail:
    """Tests for booking cocktails."""

    def test_book_cocktail_success(self, user_service: UserService, sample_user: User) -> None:
        """Test booking a cocktail successfully."""
        original_balance = sample_user.balance
        amount = 5.50

        user = user_service.book_cocktail(sample_user.nfc_id, amount, is_alcoholic=False, name="cocktail")

        assert user.balance == original_balance - amount

    def test_book_alcoholic_cocktail_adult(self, user_service: UserService, sample_user: User) -> None:
        """Test adult can book alcoholic cocktail."""
        original_balance = sample_user.balance
        amount = 7.50

        user = user_service.book_cocktail(sample_user.nfc_id, amount, is_alcoholic=True, name="cocktail")

        assert user.balance == original_balance - amount

    def test_book_alcoholic_cocktail_minor(self, user_service: UserService, sample_minor: User) -> None:
        """Test minor cannot book alcoholic cocktail."""
        with pytest.raises(HTTPException) as exc_info:
            user_service.book_cocktail(sample_minor.nfc_id, 5.0, is_alcoholic=True, name="cocktail")

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "underage" in exc_info.value.detail.lower()

    def test_book_cocktail_insufficient_balance(self, user_service: UserService, sample_user: User) -> None:
        """Test booking cocktail with insufficient balance raises exception."""
        amount = sample_user.balance + 100.0

        with pytest.raises(HTTPException) as exc_info:
            user_service.book_cocktail(sample_user.nfc_id, amount, is_alcoholic=False, name="cocktail")

        assert exc_info.value.status_code == status.HTTP_402_PAYMENT_REQUIRED
        assert "Insufficient balance" in exc_info.value.detail

    def test_book_cocktail_user_not_found(self, user_service: UserService) -> None:
        """Test booking cocktail for non-existent user raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            user_service.book_cocktail("NONEXISTENT", 5.0, is_alcoholic=False, name="cocktail")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_book_non_alcoholic_cocktail_minor(self, user_service: UserService, sample_minor: User) -> None:
        """Test minor can book non-alcoholic cocktail."""
        original_balance = sample_minor.balance
        amount = 4.50

        user = user_service.book_cocktail(sample_minor.nfc_id, amount, is_alcoholic=False, name="cocktail")

        assert user.balance == original_balance - amount

    def test_book_cocktail_exact_balance(self, user_service: UserService, sample_user: User) -> None:
        """Test booking cocktail with exact balance."""
        amount = sample_user.balance

        user = user_service.book_cocktail(sample_user.nfc_id, amount, is_alcoholic=False, name="cocktail")

        assert user.balance == 0.0

    def test_book_cocktail_create_log(self, user_service: UserService, sample_user: User) -> None:
        """Test that booking a cocktail creates a payment log."""
        amount = 5.0
        name = "Mojito"

        user_service.book_cocktail(sample_user.nfc_id, amount, is_alcoholic=False, name=name)
        logs = user_service.get_payment_logs(sample_user.nfc_id)
        first_log = next(log for log in logs if log.nfc_id == sample_user.nfc_id)
        assert first_log is not None
        assert first_log.description == name
        assert first_log.amount == -amount
        first_log.created_at


class TestPaymentLogs:
    """Tests for payment log retrieval."""

    def test_get_payment_logs(self, user_service: UserService, sample_user: User) -> None:
        """Test retrieving payment logs for a user."""
        # Create some payment logs
        user_service.log_payment_event(sample_user.nfc_id, 20.0, 20.0, "Account Top-up")
        user_service.log_payment_event(sample_user.nfc_id, 5.0, 15.0, "Test Cocktail")

        logs = user_service.get_payment_logs(sample_user.nfc_id)
        assert len(logs) >= 2  # noqa: PLR2004
        descriptions = [log.description for log in logs]
        assert "Account Top-up" in descriptions
        assert any("Cocktail" in desc for desc in descriptions)

        # also test that created_at is populated
        for log in logs:
            assert log.created_at is not None

    def test_get_all_payment_logs(self, user_service: UserService, sample_user: User, sample_minor: User) -> None:
        """Test retrieving all payment logs."""
        # Create some payment logs for both users
        user_service.log_payment_event(sample_user.nfc_id, 15.0, 15.0, "Account Top-up")
        user_service.log_payment_event(sample_minor.nfc_id, 10.0, 25.0, "Account Top-up")

        all_logs = user_service.get_all_payment_logs()
        assert len(all_logs) >= 2  # noqa: PLR2004
        nfc_ids = [log.nfc_id for log in all_logs]
        assert sample_user.nfc_id in nfc_ids
        assert sample_minor.nfc_id in nfc_ids
