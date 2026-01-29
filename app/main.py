from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services.s3_service import s3_service
from app.services.redis_cache import redis_cache
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    Priming the environment here ensures LocalStack is ready.
    """
    # Startup Logic
    print(f"🚀 Starting {settings.api_title}...")
    
    # 1. Ensure S3 Bucket exists in LocalStack
    try:
        s3_service.create_bucket_if_not_exists()
        print(f"✅ S3 Bucket '{settings.s3_bucket}' is ready.")
    except Exception as e:
        print(f"❌ Error connecting to LocalStack/S3: {e}")

    # 2. Check Redis Connection
    try:
        await redis_cache.client.ping()
        print("✅ Redis connection established.")
    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")

    yield

    # Shutdown Logic
    print("👋 Shutting down...")
    await redis_cache.client.close()

app = FastAPI(
    title=settings.api_title,
    lifespan=lifespan,
    debug=settings.debug
)

# Set up CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our API routes
app.include_router(api_router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check to verify the API is alive."""
    return {
        "status": "online",
        "aws_region": settings.aws_region,
        "bucket": settings.s3_bucket
    }