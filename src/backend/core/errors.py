"""Domain errors raised by the service layer.

These carry domain data only — never an HTTP status. The single mapping from a
domain error to an HTTP response lives at the seam in ``core.exception_handlers``.
Each error's ``str()`` is the user-facing detail message, rendered in the
configured language via the backend ``translations`` singleton (so both the API
detail and the logs follow ``LANGUAGE``).
"""

from decimal import Decimal

from src.backend.i18n.translator import translations as t


class DomainError(Exception):
    """Base class for domain errors raised by the service layer."""


class UserNotFound(DomainError):
    """No account exists for the given NFC ID."""

    def __init__(self, nfc_id: str) -> None:
        self.nfc_id = nfc_id
        super().__init__(t.err_user_not_found)


class DuplicateNfc(DomainError):
    """An account already exists for the given NFC ID."""

    def __init__(self, nfc_id: str) -> None:
        self.nfc_id = nfc_id
        super().__init__(t.err_duplicate_nfc.format(nfc_id=nfc_id))


class BalanceBelowMinimum(DomainError):
    """A balance change would drop the balance below zero (the non-negative floor)."""

    def __init__(self, current: Decimal, requested: Decimal) -> None:
        self.current = current
        self.requested = requested
        super().__init__(t.err_balance_below_minimum.format(current=f"{current:.2f}", requested=f"{requested:.2f}"))


class UnderageBooking(DomainError):
    """A minor attempted to book an alcoholic cocktail."""

    def __init__(self, nfc_id: str) -> None:
        self.nfc_id = nfc_id
        super().__init__(t.err_underage_booking)


class InsufficientBalance(DomainError):
    """The balance is too low to cover the requested charge."""

    def __init__(self, current: Decimal, required: Decimal) -> None:
        self.current = current
        self.required = required
        super().__init__(t.err_insufficient_balance.format(current=f"{current:.2f}", required=f"{required:.2f}"))
