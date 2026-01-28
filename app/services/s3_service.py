import boto3
from botocore.config import Config
from app.core.config import settings

class S3Service:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
            # SigV4 is required for presigned URLs in many regions
            config=Config(signature_version="s3v4")
        )
        self.bucket = settings.s3_bucket

    def create_bucket_if_not_exists(self):
        """Ensures the sandbox environment is ready on startup."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except self.client.exceptions.ClientError:
            self.client.create_bucket(Bucket=self.bucket)

    def generate_presigned_upload_url(self, object_name: str, expiration: int = 3600):
        """Generates a URL for a simple PUT upload."""
        return self.client.generate_presigned_url(
            'put_object',
            Params={'Bucket': self.bucket, 'Key': object_name},
            ExpiresIn=expiration
        )

s3_service = S3Service()