from pydantic import BaseModel


class Nfc(BaseModel):
    nfc_id: str
    is_adult: bool
    balance: float
