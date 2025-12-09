from typing import Callable, ClassVar

from src.backend.core.nfc import RFIDReader


class NFCManager:
    _instance: ClassVar["NFCManager | None"] = None
    _latest_nfc_id: str | None = None
    _callbacks: ClassVar[list[Callable[[str], None]]] = []

    def __new__(cls) -> "NFCManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._reader = RFIDReader()
        return cls._instance

    def start(self) -> None:
        self._reader.read_rfid(self._on_nfc_read, read_delay_s=0.5)

    def _on_nfc_read(self, nfc_id: str) -> None:
        self._latest_nfc_id = nfc_id
        for callback in self._callbacks:
            callback(nfc_id)

    def get_latest_nfc_id(self) -> str | None:
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
        self._reader.cancel_reading()


nfc_manager = NFCManager()
