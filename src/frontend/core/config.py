from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from src.shared import DEFAULT_API_KEY, DEFAULT_BACKEND_PORT, ENV_PATH

load_dotenv(ENV_PATH)


class Config(BaseSettings):
    api_key: str = DEFAULT_API_KEY
    api_port: int = DEFAULT_BACKEND_PORT
    api_address: str = "http://localhost"
    mock_nfc: bool = False
    dev_mode: bool = False
    native_mode: bool = False
    full_screen: bool = False
    language: str = "en"
    default_balance: float = 10.0
    nfc_timeout: float = 10.0

    @property
    def api_url(self) -> str:
        return f"{self.api_address}:{self.api_port}/api"


config = Config()  # type: ignore[assignment]
