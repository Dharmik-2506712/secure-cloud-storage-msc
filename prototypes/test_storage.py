# test_storage.py
# Proves we can talk to MinIO: upload a file, list the bucket, download
# it back, and check the contents match. No encryption yet — just the
# plumbing to the "cloud" (your local MinIO server).

import boto3

# ---- Your MinIO details ----
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
BUCKET_NAME = "test-bucket"
ENDPOINT_URL = "http://127.0.0.1:9000"   # API port, NOT the 9001 console port
# -----------------------------

client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

# 1. Upload a small test file
with open("secret.txt", "rb") as f:
    client.upload_fileobj(f, BUCKET_NAME, "test-upload.txt")
print("Uploaded secret.txt as 'test-upload.txt'")

# 2. List what's in the bucket
response = client.list_objects_v2(Bucket=BUCKET_NAME)
print("\nObjects currently in bucket:")
for obj in response.get("Contents", []):
    print(f"  - {obj['Key']} ({obj['Size']} bytes)")

# 3. Download it back down
client.download_file(BUCKET_NAME, "test-upload.txt", "downloaded_copy.txt")
print("\nDownloaded back to downloaded_copy.txt")

# 4. Confirm contents match
with open("secret.txt", "rb") as f1, open("downloaded_copy.txt", "rb") as f2:
    if f1.read() == f2.read():
        print("Contents match — MinIO round trip successful!")
    else:
        print("Contents DON'T match — something's wrong.")