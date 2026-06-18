"""Tests for the frontend's backend client, driven through an httpx MockTransport.

No live server: a mock transport returns canned responses, so this exercises the
real call paths, the Result wrapping, and the {"detail": ...} error extraction.
Assertions key on the detail we inject, so they're independent of the GUI language.
"""

import asyncio
from collections.abc import Awaitable, Callable

import httpx

from src.frontend.core.payment_api import PaymentApi, Result, is_err, is_success


def _run[T](handler: Callable[[httpx.Request], httpx.Response], call: Callable[[PaymentApi], Awaitable[T]]) -> T:
    async def scenario() -> T:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test") as client:
            return await call(PaymentApi(client))

    return asyncio.run(scenario())


def test_get_all_nfc_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users"
        return httpx.Response(200, json=[{"nfc_id": "A", "is_adult": True, "balance": 10.0}])

    result: Result = _run(handler, lambda api: api.get_all_nfc())
    assert is_success(result)
    assert result.data[0].nfc_id == "A"
    assert result.data[0].balance == 10.0  # noqa: PLR2004


def test_get_nfc_returns_none_on_404() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "User not found"})

    result: Result = _run(handler, lambda api: api.get_nfc("MISSING"))
    assert is_success(result)
    assert result.data is None


def test_get_nfc_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"nfc_id": "B", "is_adult": False, "balance": 3.5})

    result: Result = _run(handler, lambda api: api.get_nfc("B"))
    assert is_success(result)
    assert result.data is not None
    assert result.data.is_adult is False


def test_create_nfc_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        return httpx.Response(201, json={"nfc_id": "C", "is_adult": True, "balance": 0.0})

    result: Result = _run(handler, lambda api: api.create_nfc("C", is_adult=True, balance=0.0))
    assert is_success(result)
    assert result.data.nfc_id == "C"


def test_create_nfc_duplicate_surfaces_detail() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"detail": "User with NFC ID C already exists"})

    result: Result = _run(handler, lambda api: api.create_nfc("C", is_adult=True, balance=0.0))
    assert is_err(result)
    assert "User with NFC ID C already exists" in result.error


def test_update_balance_insufficient_surfaces_detail() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(402, json={"detail": "Insufficient balance. Current: 5.00, Required: 10.00"})

    result: Result = _run(handler, lambda api: api.update_balance("D", -10.0))
    assert is_err(result)
    assert "Insufficient balance. Current: 5.00, Required: 10.00" in result.error


def test_delete_nfc_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "DELETE"
        return httpx.Response(204)

    result: Result = _run(handler, lambda api: api.delete_nfc("E"))
    assert is_success(result)


def test_delete_nfc_404_is_err() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "User not found"})

    result: Result = _run(handler, lambda api: api.delete_nfc("MISSING"))
    assert is_err(result)
