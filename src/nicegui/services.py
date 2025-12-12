# services.py

import asyncio
import random
from typing import Any


async def mock_nfc_scan() -> str:
    """Simulate a 5-second NFC scan and return a random card ID."""
    await asyncio.sleep(5)
    return "".join(random.choices("0123456789ABCDEF", k=8))


async def mock_post_to_backend(user_data: dict[str, Any]) -> None:
    """Simulate a remote backend POST (0.5s delay)."""
    await asyncio.sleep(0.5)
    print(f"[mock_post_to_backend] {user_data}")
