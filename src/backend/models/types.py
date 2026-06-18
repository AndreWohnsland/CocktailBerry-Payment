"""Shared model field types."""

from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

# Monetary amount type.
#
# Stored and computed server-side as an exact ``Decimal`` (no float rounding
# errors when accumulating balances), but serialized to a JSON *number* so the
# public API contract stays identical to the previous float-based one. Clients
# (the GUI and cocktail machines) keep receiving e.g. ``10.1`` rather than
# ``"10.10"``.
Money = Annotated[
    Decimal,
    PlainSerializer(float, return_type=float, when_used="json"),
]

# Database column precision: up to 9_999_999_999.99.
MONEY_MAX_DIGITS = 12
MONEY_DECIMAL_PLACES = 2
