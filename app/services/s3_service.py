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
    
    def initiate_multipart_upload(self, key: str, content_type: str):
        """Tells S3 we are starting a multi-part process."""
        response = self.client.create_multipart_upload(
            Bucket=self.bucket,
            Key=key,
            ContentType=content_type
        )
        return response["UploadId"]

    def generate_presigned_part_url(self, key: str, upload_id: str, part_number: int):
        """Generates a unique URL for a specific chunk of the file."""
        return self.client.generate_presigned_url(
            ClientMethod="upload_part",
            Params={
                "Bucket": self.bucket,
                "Key": key,
                "UploadId": upload_id,
                "PartNumber": part_number,
            },
            ExpiresIn=3600,
        )

    def complete_multipart_upload(self, key: str, upload_id: str, parts: list):
        """Tells S3 to stitch all the chunks together into one file."""
        return self.client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )

s3_service = S3Service()