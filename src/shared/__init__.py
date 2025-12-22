from pathlib import Path

DEFAULT_BACKEND_PORT = 9876
DEFAULT_API_KEY = "CocktailBerry-Secret-Change-Me"

ROOT_PATH = Path(__file__).parent.parent.parent
ENV_PATH = ROOT_PATH / ".env"
DEFAULT_DATABASE_PATH = Path.home() / ".cocktailberry" / "payment.db"
