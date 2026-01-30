import asyncio
import redis.asyncio as redis
from app.services.s3_service import s3_service
from app.core.config import settings

async def janitor_worker():
    """Listens for Redis expiration events and cleans up S3."""
    # Connect to Redis
    r = redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub()
    
    # Subscribe to expiration events on DB 0
    # Note: Ensure notify-keyspace-events is set to 'Ex' in Redis config
    await pubsub.subscribe("__keyevent@0__:expired")
    
    print("🧹 Janitor Worker started. Listening for expired leases...")

    async for message in pubsub.listen():
        if message["type"] == "message":
            expired_key = message["data"]
            
            # Check if this is one of our "Shadow Keys"
            if expired_key.startswith("lease:"):
                file_id = expired_key.split(":")[1]
                data_key = f"upload:{file_id}"
                
                # 1. Fetch the metadata before we delete the data key
                metadata = await r.hgetall(data_key)
                
                if metadata and "key" in metadata:
                    s3_path = metadata["key"]
                    print(f"🗑️ Lease expired for {file_id}. Deleting {s3_path} from S3...")
                    
                    try:
                        # 2. Delete from S3
                        s3_service.client.delete_object(
                            Bucket=settings.s3_bucket,
                            Key=s3_path
                        )
                        # 3. Cleanup the Data Key
                        await r.delete(data_key)
                        print(f"✅ Successfully cleaned up {file_id}")
                    except Exception as e:
                        print(f"❌ Failed to delete {s3_path}: {e}")

if __name__ == "__main__":
    asyncio.run(janitor_worker())