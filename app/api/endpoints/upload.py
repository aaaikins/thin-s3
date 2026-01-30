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
async def initiate_upload(data: UploadInitRequest):
    file_id = str(uuid.uuid4())
    s3_key = f"uploads/{file_id}/{data.file_name}"
    
    upload_id = s3_service.initiate_multipart_upload(key=s3_key, content_type=data.content_type)
    
    # Use the new dual-key logic
    await redis_cache.set_leased_metadata(
        file_id=file_id,
        value={
            "upload_id": upload_id,
            "key": s3_key,
            "file_name": data.file_name
        },
        ttl=settings.default_ttl_seconds
    )
    
    return UploadInitResponse(file_id=file_id, upload_id=upload_id, key=s3_key)


@api_router.post("/presign-parts")
async def create_presigned_parts(data: PartUploadRequest) -> PartUploadResponse:

    """Give the client the "keys" to upload specific chunks."""

    # The metadata is stored under the `upload:{file_id}` key
    metadata = await redis_cache.get_metadata(f"upload:{data.file_id}")

    if not metadata or metadata["upload_id"] != data.upload_id:
        raise HTTPException(status_code=404, detail="Upload session not found")


    presigned_urls = []

    for part_number in data.part_numbers:
        url = s3_service.generate_presigned_part_url(
            key=metadata["key"],
            upload_id=metadata["upload_id"],
            part_number=part_number
        )

        presigned_urls.append(PartUploadURL(part_number=part_number, url=url))
    
    return PartUploadResponse(parts=presigned_urls)

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