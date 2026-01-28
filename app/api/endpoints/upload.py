"""Multipart upload & presigned URL logic"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional

api_router = APIRouter(prefix="/upload", tags=["upload"])


@api_router.post("/presigned")
async def get_presigned_url(
    bucket: str,
    key: str,
    expires_in: int = 3600
) -> dict:
    """Generate a presigned URL for direct S3 upload"""
    # TODO: Implement presigned URL generation
    pass


@api_router.post("/multipart")
async def upload_file(
    file: UploadFile = File(...),
    bucket: str = None,
    key: str = None
) -> dict:
    # TODO: Implement multipart file upload
    """Handle multipart file upload to S3"""
    pass
