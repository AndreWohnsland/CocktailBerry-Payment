from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from src.shared import DEFAULT_API_KEY, DEFAULT_BACKEND_PORT, ENV_PATH

load_dotenv(ENV_PATH)


class Config(BaseSettings):
    api_key: str = DEFAULT_API_KEY
    api_port: int = DEFAULT_BACKEND_PORT


config = Config()  # type: ignore[assignment]
