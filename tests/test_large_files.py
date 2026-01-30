import os
import requests
import math
from concurrent.futures import ThreadPoolExecutor

CHUNK_SIZE = 5 * 1024 * 1024  # 5MB (AWS S3 Minimum)
MAX_WORKERS = 4               # How many parallel uploads at once

def upload_large_file(file_path):
    file_size = os.path.getsize(file_path)
    total_parts = math.ceil(file_size / CHUNK_SIZE)
    file_name = os.path.basename(file_path)

    # 1. Initiate with our "Thin S3" API
    res = requests.post("http://localhost:8000/api/upload/initiate", 
                        json={"file_name": file_name, "content_type": "application/octet-stream"})
    init_data = res.json()
    file_id, upload_id = init_data["file_id"], init_data["upload_id"]

    # 2. Get Pre-signed URLs for ALL parts at once
    part_numbers = list(range(1, total_parts + 1))
    res = requests.get("http://localhost:8000/api/upload/presign-parts", 
                        json={"file_id": file_id, "upload_id": upload_id, "part_numbers": part_numbers})
    url_mapping = {p["part_number"]: p["url"] for p in res.json()["parts"]}
    # print(url_mapping)

    completed_parts = []

    # 3. The Worker Function for Parallelism
    def upload_chunk(part_number):
        offset = (part_number - 1) * CHUNK_SIZE
        with open(file_path, "rb") as f:
            f.seek(offset)
            chunk_data = f.read(CHUNK_SIZE)
            
        print(f"🚀 Uploading Part {part_number}/{total_parts}...")
        put_res = requests.put(url_mapping[part_number], data=chunk_data)
        return {"ETag": put_res.headers.get("ETag"), "PartNumber": part_number}

    # 4. Execute Parallel Uploads
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        completed_parts = list(executor.map(upload_chunk, part_numbers))

    # 5. Finalize
    print("🔗 All parts uploaded. Stitching...")
    requests.post("http://localhost:8000/api/upload/complete", 
                  json={"file_id": file_id, "upload_id": upload_id, "parts": completed_parts})
    print("✅ Large file upload complete!")

if __name__ == "__main__":
    # Create a dummy file for testing
    with open("large_test.bin", "wb") as f:
        f.write(os.urandom(100 * 1024 * 1024))
    
    upload_large_file("large_test.bin")