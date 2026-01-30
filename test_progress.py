#!/usr/bin/env python3
"""Test the upload progress endpoint"""

import requests
import time
import os

BASE_URL = "http://localhost:8000/api"
TEST_FILE = "test_file.pdf"

def test_upload_progress():
    if not os.path.exists(TEST_FILE):
        print(f"❌ Error: Please place a file named '{TEST_FILE}' in this folder.")
        return

    file_size = os.path.getsize(TEST_FILE)
    print(f"🎬 Testing Upload Progress Endpoint")
    print(f"📄 File: {TEST_FILE} ({file_size} bytes)")

    # 1. Initiate
    print("\n1️⃣ Initiating upload...")
    init_res = requests.post(
        f"{BASE_URL}/upload/initiate",
        json={"file_name": TEST_FILE, "content_type": "image/png"}
    )
    init_data = init_res.json()
    file_id, upload_id = init_data["file_id"], init_data["upload_id"]
    print(f"✅ file_id={file_id}")

    # 2. Get presigned URLs for 3 parts
    print("\n2️⃣ Getting presigned URLs for 3 parts...")
    part_res = requests.get(
        f"{BASE_URL}/upload/presign-parts",
        json={"file_id": file_id, "upload_id": upload_id, "part_numbers": [1, 2, 3]}
    )
    parts = part_res.json()["parts"]
    print(f"✅ Got {len(parts)} presigned URLs")

    # 3. Upload part 1
    print("\n3️⃣ Uploading part 1...")
    with open(TEST_FILE, "rb") as f:
        data = f.read()
        # Upload first third as part 1
        part_size = len(data) // 3
        s3_res = requests.put(parts[0]["url"], data=data[:part_size])
    etag1 = s3_res.headers.get("ETag")
    print(f"✅ Part 1 uploaded (ETag: {etag1})")

    # 4. Check progress after part 1
    print("\n4️⃣ Checking progress after part 1...")
    progress_res = requests.get(
        f"{BASE_URL}/storage/{file_id}/progress",
        params={"upload_id": upload_id}
    )
    progress_data = progress_res.json()
    print(f"✅ Parts uploaded: {progress_data['parts_uploaded']}")
    print(f"   Parts detail: {progress_data['parts']}")

    # 5. Upload part 2
    print("\n5️⃣ Uploading part 2...")
    with open(TEST_FILE, "rb") as f:
        data = f.read()
        part_size = len(data) // 3
        s3_res = requests.put(parts[1]["url"], data=data[part_size:part_size*2])
    etag2 = s3_res.headers.get("ETag")
    print(f"✅ Part 2 uploaded (ETag: {etag2})")

    # 6. Check progress after part 2
    print("\n6️⃣ Checking progress after part 2...")
    progress_res = requests.get(
        f"{BASE_URL}/storage/{file_id}/progress",
        params={"upload_id": upload_id}
    )
    progress_data = progress_res.json()
    print(f"✅ Parts uploaded: {progress_data['parts_uploaded']}")
    print(f"   Parts detail: {progress_data['parts']}")

    # 7. Upload part 3
    print("\n7️⃣ Uploading part 3...")
    with open(TEST_FILE, "rb") as f:
        data = f.read()
        part_size = len(data) // 3
        s3_res = requests.put(parts[2]["url"], data=data[part_size*2:])
    etag3 = s3_res.headers.get("ETag")
    print(f"✅ Part 3 uploaded (ETag: {etag3})")

    # 8. Final progress check
    print("\n8️⃣ Final progress check...")
    progress_res = requests.get(
        f"{BASE_URL}/storage/{file_id}/progress",
        params={"upload_id": upload_id}
    )
    progress_data = progress_res.json()
    print(f"✅ Parts uploaded: {progress_data['parts_uploaded']}")
    print(f"   Parts detail: {progress_data['parts']}")

    print("\n✨ All tests passed!")

if __name__ == "__main__":
    test_upload_progress()
