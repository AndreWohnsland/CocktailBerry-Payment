from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from src.shared import DEFAULT_API_KEY, DEFAULT_BACKEND_PORT

load_dotenv()


class Config(BaseSettings):
    api_key: str = DEFAULT_API_KEY
    api_port: int = DEFAULT_BACKEND_PORT
    api_address: str = "http://localhost"
    mock_nfc: bool = False
    language: str = "en"
    default_balance: float = 10.0
    nfc_timeout: float = 10.0

    @property
    def api_url(self) -> str:
        return f"{self.api_address}:{self.api_port}"


config = Config()  # type: ignore[assignment]
