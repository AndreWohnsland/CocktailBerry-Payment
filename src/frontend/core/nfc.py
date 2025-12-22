"""NFC reader module for the frontend.

Provides stateless NFC scanning with two modes:
- one_shot: Scans until a card is detected or timeout
- continuous: Continuously scans and calls a callback for each card
"""

import asyncio
import logging
import time
from collections.abc import Callable
from threading import Event, Thread
from typing import ClassVar

try:
    from smartcard.CardRequest import CardRequest
    from smartcard.CardType import AnyCardType
    from smartcard.PassThruCardService import PassThruCardService
    from smartcard.pcsc.PCSCReader import PCSCReader
    from smartcard.System import readers
    from smartcard.util import toHexString
except (ImportError, ModuleNotFoundError):
    print("pyscard library is required for NFC functionality. Please install the 'nfc' extra.")

from src.frontend.core.config import config as cfg

_logger = logging.getLogger(__name__)


class USBReader:
    """Low-level USB NFC reader interface."""

    GET_UID: ClassVar[list[int]] = [0xFF, 0xCA, 0x00, 0x00, 0x00]

    def __init__(self) -> None:
        available: list[PCSCReader] = readers()
        if not available:
            _logger.error("No PC/SC reader found")
            raise RuntimeError("No PC/SC reader found")
        self.reader_name = available[0]

    def read_card(self, timeout: int = 5) -> str | None:
        """Read a card UID with timeout in seconds."""
        card_request = CardRequest(cardType=AnyCardType(), timeout=timeout)
        try:
            service = card_request.waitforcard()
            if not isinstance(service, PassThruCardService):
                return None
            conn = service.connection  # type: ignore
            conn.connect()
            response, sw1, sw2 = conn.transmit(self.GET_UID)
        except Exception:
            return None
        if (sw1, sw2) == (0x90, 0x00):
            return toHexString(response).replace(" ", "")
        return None


class NFCScanner:
    """Singleton NFC scanner for frontend use.

    Provides two scanning modes:
    - one_shot: Blocking scan until card detected or timeout
    - continuous: Non-blocking continuous scanning with callback
    """

    _instance: ClassVar["NFCScanner | None"] = None
    _initialized: bool = False

    def __new__(cls) -> "NFCScanner":
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._reader: USBReader | None = None
        self._stop_event = Event()
        self._scan_thread: Thread | None = None
        self._init_reader()

    def _init_reader(self) -> None:
        """Initialize the USB reader, catching errors if no reader available."""
        try:
            self._reader = USBReader()
        except RuntimeError:
            self._reader = None

    def is_available(self) -> bool:
        """Check if NFC reader is available."""
        return self._reader is not None

    async def one_shot(self, timeout: float = cfg.nfc_timeout, poll_interval: float = 0.5) -> str | None:
        """Scan for a single NFC card (blocking) until detected or timeout reached."""
        if not self._reader:
            return None

        start_time = time.monotonic()
        while (time.monotonic() - start_time) < timeout:
            await asyncio.sleep(0.1)
            nfc_id = self._reader.read_card(timeout=max(1, int(poll_interval)))
            if nfc_id:
                return nfc_id
        return None

    def start_continuous(
        self,
        callback: Callable[[str], None],
        poll_interval: float = 0.5,
    ) -> bool:
        """Start continuous NFC scanning in background thread. Returns True if started."""
        if not self._reader:
            return False
        if self._scan_thread and self._scan_thread.is_alive():
            return False

        self._stop_event.clear()
        self._scan_thread = Thread(
            target=self._continuous_scan_loop,
            args=(callback, poll_interval),
            daemon=True,
        )
        self._scan_thread.start()
        return True

    def _continuous_scan_loop(
        self,
        callback: Callable[[str], None],
        poll_interval: float,
    ) -> None:
        """Run the continuous scanning loop."""
        if not self._reader:
            return
        while not self._stop_event.is_set():
            nfc_id = self._reader.read_card(timeout=max(1, int(poll_interval)))
            if nfc_id and not self._stop_event.is_set():
                callback(nfc_id)

    def stop_continuous(self) -> None:
        """Stop continuous scanning."""
        self._stop_event.set()
        if self._scan_thread:
            self._scan_thread.join(timeout=2.0)
            self._scan_thread = None

    def is_scanning(self) -> bool:
        """Check if continuous scanning is active."""
        return self._scan_thread is not None and self._scan_thread.is_alive()


# Module-level scanner instance
nfc_scanner = NFCScanner()
