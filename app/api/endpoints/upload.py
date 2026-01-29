"""Multipart upload & presigned URL logic"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.s3_service import s3_service
from app.core.config import settings
from app.services.redis_cache import redis_cache
from app.models.schemas import UploadInitRequest, UploadInitResponse, PartUploadRequest, PartUploadURL, PartUploadResponse, CompleteUploadRequest
from typing import Optional
import uuid

api_router = APIRouter(prefix="/upload", tags=["upload"])

@api_router.post("/initiate")
async def initiate_upload(data: UploadInitRequest) -> UploadInitResponse:
    # Use UUID for a guaranteed unique file key in S3
    file_id = str(uuid.uuid4())
    s3_key = f"uploads/{file_id}/{data.file_name}"
    
    upload_id = s3_service.initiate_multipart_upload(
        key=s3_key,
        content_type=data.content_type
    )
    
    # Ensure 'key' is saved so the other endpoints know WHERE the file is in S3
    await redis_cache.set_metadata(
        key=f"upload:{file_id}",
        value={
            "upload_id": upload_id,
            "key": s3_key, 
            "file_name": data.file_name
        },
        ttl=settings.default_ttl_seconds
    )
    
    return UploadInitResponse(file_id=file_id, upload_id=upload_id, key=s3_key)

@api_router.post("/complete")
async def complete_upload(data: CompleteUploadRequest):
    redis_key = f"upload:{data.file_id}"
    metadata = await redis_cache.get_metadata(redis_key)
    
    if not metadata or metadata.get("upload_id") != data.upload_id:
        raise HTTPException(status_code=404, detail="Upload session expired or not found")
    
    try:
        # Stitch it all together
        response = s3_service.complete_multipart_upload(
            key=metadata["key"],
            upload_id=metadata["upload_id"],
            parts=data.parts
        )
        
        # CLEANUP: Remove from Redis now that it's finalized
        await redis_cache.client.delete(redis_key)
        
        return {"status": "success", "location": response.get("Location")}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 Completion Error: {str(e)}")