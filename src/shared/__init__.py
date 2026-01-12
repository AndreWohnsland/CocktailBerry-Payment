from pathlib import Path

DEFAULT_BACKEND_PORT = 9876
DEFAULT_API_KEY = "CocktailBerry-Secret-Change-Me"
# holy default master keys, batman! Honor them for the cocktailberry team!
DEFAULT_MASTER_KEYS = ["33DFE41D", "9A853015", "CAD3B515"]

ROOT_PATH = Path(__file__).parent.parent.parent
ENV_PATH = ROOT_PATH / ".env"
LOG_CONFIG_PATH = ROOT_PATH / "log_config.yaml"
DEFAULT_DATABASE_PATH = Path.home() / ".cocktailberry" / "payment.db"
