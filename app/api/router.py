"""Main API api_router"""

from fastapi import APIRouter
from app.api.endpoints import upload, storage

api_router = APIRouter()

# api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
api_router.include_router(upload.api_router)
api_router.include_router(storage.api_router)
