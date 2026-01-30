from fastapi import APIRouter, HTTPException
from app.services.s3_service import s3_service
from app.services.redis_cache import redis_cache
from app.core.config import settings

api_router = APIRouter(prefix="/storage", tags=["storage"])

@api_router.get("/{file_id}/download")
async def get_download_url(file_id: str):
    # 1. Look up the metadata in Redis
    metadata = await redis_cache.get_metadata(f"upload:{file_id}")
    
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found or lease expired")

    # 2. Generate the presigned GET URL
    url = s3_service.client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.s3_bucket, 'Key': metadata['key']},
        ExpiresIn=3600
    )
    
    return {"download_url": url}

@api_router.get("/{file_id}/progress")
async def get_upload_progress(file_id: str, upload_id: str):
    """Get real-time progress of multipart upload by checking S3 for uploaded parts."""
    # 1. Verify the upload session exists in Redis
    metadata = await redis_cache.get_metadata(f"upload:{file_id}")
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    # 2. Verify the upload_id matches
    if metadata.get("upload_id") != upload_id:
        raise HTTPException(status_code=400, detail="Upload ID mismatch")
    
    try:
        # 3. Query S3 for uploaded parts
        progress = s3_service.list_uploaded_parts(key=metadata["key"], upload_id=upload_id)
        
        return {
            "file_id": file_id,
            "parts_uploaded": progress["part_count"],
            "parts": progress["parts"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get upload progress: {str(e)}")


@api_router.patch("/{file_id}/lease")
async def update_lease(file_id: str, ttl_seconds: int):
    # We update the shadow key, NOT the metadata key
    lease_key = f"lease:{file_id}"
    
    # Check if metadata still exists first
    exists = await redis_cache.client.exists(f"upload:{file_id}")
    if not exists:
        raise HTTPException(status_code=404, detail="File already deleted or expired")

    # Reset the countdown
    await redis_cache.client.set(lease_key, "active", ex=ttl_seconds)
    
    return {"status": "success", "new_lease": f"{ttl_seconds} seconds"}



@api_router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Manually deletes the file from both S3 and Redis"""
    redis_key = f"upload:{file_id}"
    metadata = await redis_cache.get_metadata(redis_key)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="File metadata not found")

    try:
        # 1. Remove from S3 sandbox
        s3_service.client.delete_object(
            Bucket=settings.s3_bucket,
            Key=metadata["key"]
        )
        
        # 2. Remove from Redis
        await redis_cache.client.delete(redis_key)
        
        return {"status": "success", "message": f"File {file_id} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")