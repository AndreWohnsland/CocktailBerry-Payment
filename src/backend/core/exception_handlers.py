"""The service↔HTTP seam: maps domain errors to HTTP responses.

This is the only place a :class:`DomainError` becomes an HTTP status. The service
raises domain errors (see ``core.errors``); this adapter renders them as
``{"detail": ...}`` with the mapped status — the response shape the GUI depends
on. Adding a new domain error means adding one entry to ``_STATUS``.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.backend.core.errors import (
    BalanceBelowMinimum,
    DomainError,
    DuplicateNfc,
    InsufficientBalance,
    UnderageBooking,
    UserNotFound,
)

_logger = logging.getLogger(__name__)

_STATUS: dict[type[DomainError], int] = {
    UserNotFound: status.HTTP_404_NOT_FOUND,
    DuplicateNfc: status.HTTP_400_BAD_REQUEST,
    BalanceBelowMinimum: status.HTTP_400_BAD_REQUEST,
    UnderageBooking: status.HTTP_403_FORBIDDEN,
    InsufficientBalance: status.HTTP_402_PAYMENT_REQUIRED,
}


def _handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
    status_code = _STATUS.get(type(exc))
    if status_code is None:
        # An unmapped domain error is a programming error, not a client one:
        # fail safe with 500 rather than raising KeyError out of the handler.
        _logger.error("Unmapped domain error: %s", type(exc).__name__)
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


def register_exception_handlers(app: FastAPI) -> None:
    """Register the domain-error handler on the app. Catches every DomainError subclass."""
    app.add_exception_handler(DomainError, _handle_domain_error)  # type: ignore[arg-type]
