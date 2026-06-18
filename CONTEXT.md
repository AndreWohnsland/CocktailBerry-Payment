# CocktailBerry-Payment — domain language

Ubiquitous language for the payment service. Keep terms here when they name a
real concept in the code or a seam worth protecting.

## Domain nouns

- **NFC account** (`User`) — a card identified by its `nfc_id`, holding a
  `balance` and an `is_adult` flag. The `nfc_id` is the identity.
- **Balance** — money on an account, stored and computed as an exact `Decimal`
  (the `Money` type), serialized to a JSON number on the wire.
- **Top-up** — adding (or subtracting) money from a balance.
- **Booking** — charging a balance for a cocktail; age-checked when alcoholic.
- **Payment Log** — the append-only ledger of balance-changing events
  (created / updated / deleted / top-up / booking). One entry per change.
- **Master key** — a privileged staff card; bookings on it are logged but not
  charged, and it bypasses age checks.
- **Non-negative balance** — a balance may not go below zero. A domain fact, not
  a tunable: both the booking charge and admin adjustment enforce the same `>= 0`
  floor (surfaced as `InsufficientBalance` / `BalanceBelowMinimum` respectively).

## Seams

### GUI ↔ backend client seam

`PaymentApi` (`frontend/core/payment_api.py`) is the GUI's only door to the
backend: typed methods that each return a `Result` (`Success | Err`), with
`run_catching` turning any error (incl. an httpx `{"detail": ...}` body) into a
localized `Err`. Its `httpx` client is **injected**, so it's tested through an
`httpx.MockTransport` with no server — the interface is the test surface.
`NFCService` is a thin facade over it that also holds the NFC scanner and the
UI change-listeners (fired after a successful mutation); tabs talk to the facade.

### Service ↔ HTTP error seam

`UserService` is the domain module and speaks only the domain language: it
raises **domain errors**, never HTTP. The translation to HTTP lives at one
adapter.

- **`DomainError`** — base of the error taxonomy in `core/errors.py`. Carries
  domain data, never an HTTP status. Its `__str__` is the user-facing detail
  message.
  - `UserNotFound`, `DuplicateNfc`, `BalanceBelowMinimum`, `UnderageBooking`,
    `InsufficientBalance`.
- **The mapping** — a single dict in `core/exception_handlers.py` maps each
  `DomainError` subclass to a status code; one handler (registered on the base)
  renders `{"detail": str(exc)}`. This is the *only* place domain meaning
  becomes HTTP. Adding a domain error means adding one mapping entry.
- **Error messages are localized.** The backend has its own `LANGUAGE` env and a
  small translator (`i18n/translator.py` + per-language YAML), mirroring the
  frontend. Each `DomainError` renders its message through the `translations`
  singleton in `str()`, so the API `detail` and the logs both follow `LANGUAGE`
  (one configured language per backend instance). Adding a domain error means
  adding a key to each locale file.
- Exceptions to the rule (already at the adapter, intentionally inline): the
  API-key `401` in `core/middleware.py` and the "no logs" `404` in the history
  route.

Regression boundary: the GUI branches on `status_code == 404` and reads
`body["detail"]`, so the mapping must preserve exact 404s and the `{"detail"}`
shape.
