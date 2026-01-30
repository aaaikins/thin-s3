import requests
import time
import hashlib
import os

BASE_URL = "http://localhost:8000/api"
TEST_FILE = "test_file.pdf"
DOWNLOADED_FILE = "downloaded_result.pdf"

def get_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def run_full_test():
    if not os.path.exists(TEST_FILE):
        print(f"❌ Error: Please place a file named '{TEST_FILE}' in this folder.")
        return

    original_hash = get_md5(TEST_FILE)
    file_size = os.path.getsize(TEST_FILE)
    print(f"🎬 Starting Byte-Integrity Test for: {TEST_FILE} ({file_size} bytes)")
    print(f"🔑 Original MD5: {original_hash}")

    # 1. Initiate
    print("\n1️⃣ Initiating upload...")
    init_res = requests.post(
        f"{BASE_URL}/upload/initiate",
        json={"file_name": TEST_FILE, "content_type": "image/png"}
    )
    init_data = init_res.json()
    file_id, upload_id = init_data["file_id"], init_data["upload_id"]

    # 2. Get Pre-signed URL
    print("2️⃣ Requesting pre-signed URL for Part 1...")
    
    part_res = requests.get(
        f"{BASE_URL}/upload/presign-parts",
        json={"file_id": file_id, "upload_id": upload_id, "part_numbers": [1]}
    )
    # for i in range(len(part_res.json()["parts"])):
    #     print(part_res.json()["parts"][i]["url"])
    presigned_url = part_res.json()["parts"][0]["url"]


    # 3. Upload Actual Bytes
    print("3️⃣ Uploading actual file bytes to S3...")
    with open(TEST_FILE, "rb") as f:
        s3_res = requests.put(presigned_url, data=f)
    etag = s3_res.headers.get("ETag")
    print(f"✅ S3 Upload Successful. ETag: {etag}")

    # 4. Complete
    print("4️⃣ Finalizing Multipart Upload...")
    complete_res = requests.post(
        f"{BASE_URL}/upload/complete",
        json={
            "file_id": file_id,
            "upload_id": upload_id,
            "parts": [{"ETag": etag, "PartNumber": 1}]
        }
    )

    # 5. Download and Compare
    print("\n5️⃣ Testing Download...")
    dl_url_res = requests.get(f"{BASE_URL}/storage/{file_id}/download")
    download_url = dl_url_res.json()["download_url"]
    
    file_content = requests.get(download_url)
    with open(DOWNLOADED_FILE, "wb") as f:
        f.write(file_content.content)
    
    downloaded_hash = get_md5(DOWNLOADED_FILE)
    print(f"🔑 Downloaded MD5: {downloaded_hash}")

    if original_hash == downloaded_hash:
        print("✅ SUCCESS: Hashes match! Data integrity is perfect.")
    else:
        print("❌ ERROR: Hashes do not match. Data was corrupted.")

    # 6. Test the Lease/Janitor
    print("\n6️⃣ Testing Janitor (10s Lease)...")
    requests.patch(f"{BASE_URL}/storage/{file_id}/lease?ttl_seconds=10")
    print("⌛ Waiting 12s for auto-deletion...")
    time.sleep(12)
    
    final_check = requests.get(f"{BASE_URL}/storage/{file_id}/download")
    if final_check.status_code == 404:
        print("🎊 SUCCESS: Janitor cleaned up the file on schedule.")
    else:
        print("❌ FAILURE: File still exists after lease expired.")

if __name__ == "__main__":
    run_full_test()