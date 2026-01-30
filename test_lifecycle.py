import requests
import time

BASE_URL = "http://localhost:8000/api"

def test_thin_s3_flow():
    print("🎬 Starting Thin S3 Lifecycle Test...")

    # 1. Initiate Upload (Set a short TTL of 10 seconds for testing)
    print("\n1️⃣ Initiating upload...")
    init_res = requests.post(
        f"{BASE_URL}/upload/initiate",
        json={"file_name": "test_video.mp4", "content_type": "video/mp4"}
    )
    init_data = init_res.json()
    file_id = init_data["file_id"]
    print(f"✅ Received File ID: {file_id}")

    # 2. Get Pre-signed URL for Part 1
    print("\n2️⃣ Requesting pre-signed URL for Part 1...")
    part_res = requests.post(
        f"{BASE_URL}/upload/presign-parts",
        json={
            "file_id": file_id,
            "upload_id": init_data["upload_id"],
            "part_numbers": [1]
        }
    )
    presigned_url = part_res.json()["parts"][0]["url"]
    print(f"✅ Received Pre-signed URL: {presigned_url[:60]}...")

    # 3. Simulate the Upload (PUT to S3/LocalStack)
    print("\n3️⃣ Uploading 'data' directly to S3...")
    dummy_data = b"This is a simulated video chunk"
    s3_res = requests.put(presigned_url, data=dummy_data)
    etag = s3_res.headers.get("ETag")
    print(f"✅ Upload successful. ETag: {etag}")

    # 4. Complete the Upload
    print("\n4️⃣ Finalizing upload (stitching)...")
    requests.post(
        f"{BASE_URL}/upload/complete",
        json={
            "file_id": file_id,
            "upload_id": init_data["upload_id"],
            "parts": [{"ETag": etag, "PartNumber": 1}]
        }
    )
    print("✅ Upload marked as COMPLETE in S3.")

    # 5. Verify the Lease and Wait for Janitor
    print(f"\n⌛ Waiting 15 seconds for the lease to expire (TTL was set in step 1)...")
    print("👀 Keep an eye on your Docker logs for the 'worker' container!")
    
    for i in range(15, 0, -1):
        print(f"Time remaining: {i}s", end="\r")
        time.sleep(1)

    # 6. Final Check
    print("\n\n5️⃣ Checking if file still exists...")
    final_res = requests.get(f"{BASE_URL}/storage/{file_id}/download")
    if final_res.status_code == 404:
        print("🎊 SUCCESS: The file has been automatically deleted by the Janitor!")
    else:
        print("❌ FAILURE: The file still exists in S3.")

if __name__ == "__main__":
    test_thin_s3_flow()