"""Main API router"""

from fastapi import APIRouter
from app.api.endpoints import upload, storage

router = APIRouter(prefix="/api", tags=["api"])

# TODO: Include endpoint routers
router.include_router(upload.router)
router.include_router(storage.router)
