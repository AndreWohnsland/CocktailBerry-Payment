import time
from threading import Thread
from typing import Callable, ClassVar, Self

from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from smartcard.PassThruCardService import PassThruCardService
from smartcard.pcsc.PCSCReader import PCSCReader
from smartcard.System import readers
from smartcard.util import toHexString


class RFIDReader:
    _instance = None

    def __new__(cls) -> Self:
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
            cls.is_active = False
            cls.rfid = USBReader()
        return cls._instance

    def read_rfid(self, side_effect: Callable[[str], None], read_delay_s: float = 0.5) -> None:
        """Start the rfid reader, calls an side effect with the read value and id."""
        if self.is_active:
            return
        rfid_thread = Thread(target=self._read_thread, args=(side_effect, read_delay_s), daemon=True)
        rfid_thread.start()

    def _read_thread(self, side_effect: Callable[[str], None], read_delay_s: float = 0.5) -> None:
        """Execute the reading until reads a value or got canceled."""
        if self.is_active:
            return
        self.is_active = True
        while self.is_active:
            _id = self.rfid.read_card()
            if _id is not None:
                side_effect(_id)
            time.sleep(read_delay_s)
        self.is_active = False

    def cancel_reading(self) -> None:
        """Cancel the reading loop."""
        self.is_active = False


class USBReader:
    """Reader for USB connected RFID readers."""

    GET_UID: ClassVar[list[int]] = [0xFF, 0xCA, 0x00, 0x00, 0x00]

    def __init__(self) -> None:
        available: list[PCSCReader] = readers()
        if not available:
            raise RuntimeError("No PC/SC reader found")
        self.reader_name = available[0]

    def read_card(self) -> str | None:
        card_request = CardRequest(cardType=AnyCardType(), timeout=5)
        try:
            service = card_request.waitforcard()
            if not isinstance(service, PassThruCardService):
                return None
            conn = service.connection  # type: ignore
            conn.connect()
            response, sw1, sw2 = conn.transmit(self.GET_UID)
        except Exception:
            # Timeout or other error — no card detected in given interval
            return None
        if (sw1, sw2) == (0x90, 0x00):
            return toHexString(response).replace(" ", "")
        return None
