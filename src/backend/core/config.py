from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    api_key: str = "change-this-key"


config = Config()  # type: ignore[assignment]
