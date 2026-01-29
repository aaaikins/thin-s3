"""Main API api_router"""
from fastapi import APIRouter
from app.api.endpoints import upload, storage

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(upload.api_router)
api_router.include_router(storage.api_router)
