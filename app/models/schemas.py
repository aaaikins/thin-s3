from pydantic import BaseModel, Field
from typing import List, Optional

class UploadInitRequest(BaseModel):
    file_name: str
    content_type: str = "application/octet-stream"

class UploadInitResponse(BaseModel):
    file_id: str
    upload_id: str
    key: str

class PartUploadRequest(BaseModel):
    file_id: str
    upload_id: str
    part_numbers: List[int]

class PartUploadURL(BaseModel):
    part_number: int
    url: str

class PartUploadResponse(BaseModel):
    parts: List[PartUploadURL]

class CompleteUploadRequest(BaseModel):
    file_id: str
    upload_id: str
    parts: List[dict]  # List of {"ETag": str, "PartNumber": int}