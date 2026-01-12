from typing import Any

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from src.shared import DEFAULT_API_KEY, DEFAULT_BACKEND_PORT, DEFAULT_DATABASE_PATH, DEFAULT_MASTER_KEYS, ENV_PATH

load_dotenv(ENV_PATH)


class Config(BaseSettings):
    api_key: str = DEFAULT_API_KEY
    api_port: int = DEFAULT_BACKEND_PORT
    database_path: str = str(DEFAULT_DATABASE_PATH)
    master_keys: list[str] = []

    def model_post_init(self, _context: Any, /) -> None:
        self.master_keys.extend(DEFAULT_MASTER_KEYS)


config = Config()  # type: ignore[assignment]
