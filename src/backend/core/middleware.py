from typing import Optional

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from src.backend.core.config import config as cfg

password_header = APIKeyHeader(name="x-api-key", scheme_name="Service API Key", auto_error=False)


def api_key_protected_dependency(api_key: Optional[str] = Security(password_header)) -> None:
    if api_key is None:
        raise HTTPException(status_code=403, detail="Missing API Key")
    if api_key != cfg.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
