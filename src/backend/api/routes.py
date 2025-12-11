from fastapi import APIRouter, Depends

from src.backend.api import balance, users
from src.backend.core.middleware import api_key_protected_dependency

api_router = APIRouter(prefix="/api", dependencies=[Depends(api_key_protected_dependency)])

api_router.include_router(users.router)
api_router.include_router(balance.router)
