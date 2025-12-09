from threading import Lock
from typing import Callable, ClassVar

# Try to import RFIDReader, but provide a mock if hardware is not available
try:
    from src.backend.core.nfc import RFIDReader
    HAS_NFC_HARDWARE = True
except (ImportError, RuntimeError):
    HAS_NFC_HARDWARE = False

    class RFIDReader:  # type: ignore
        """Mock RFID reader for testing without hardware."""

        def read_card(self) -> str | None:
            """Mock read card method."""
            return None


class NFCManager:
    _instance: ClassVar["NFCManager | None"] = None
    _lock: ClassVar[Lock] = Lock()
    _initialized: ClassVar[bool] = False

    def __init__(self) -> None:
        """Initialize NFC manager instance variables."""
        if not NFCManager._initialized:
            self._latest_nfc_id: str | None = None
            self._callbacks: list[Callable[[str], None]] = []
            self._reader = RFIDReader()  # Works with both real and mock
            NFCManager._initialized = True

    def __new__(cls) -> "NFCManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def start(self) -> None:
        if HAS_NFC_HARDWARE:
            self._reader.read_rfid(self._on_nfc_read, read_delay_s=0.5)

    def _on_nfc_read(self, nfc_id: str) -> None:
        with self._lock:
            self._latest_nfc_id = nfc_id
        for callback in self._callbacks:
            callback(nfc_id)

    def get_latest_nfc_id(self) -> str | None:
        with self._lock:
            nfc_id = self._latest_nfc_id
            self._latest_nfc_id = None  # Clear after reading
            return nfc_id

    def add_callback(self, callback: Callable[[str], None]) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[str], None]) -> None:
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def stop(self) -> None:
        if HAS_NFC_HARDWARE:
            self._reader.cancel_reading()


nfc_manager = NFCManager()
