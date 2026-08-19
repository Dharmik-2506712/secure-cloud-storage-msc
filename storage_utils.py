# storage_utils.py
# Reusable MinIO/S3 functions — same logic you already tested in
# test_storage.py, packaged as functions.

import boto3

ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
BUCKET_NAME = "test-bucket"
ENDPOINT_URL = "http://127.0.0.1:9000"


def get_client():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )


def upload_file(local_path: str, remote_key: str) -> None:
    client = get_client()
    with open(local_path, "rb") as f:
        client.upload_fileobj(f, BUCKET_NAME, remote_key)


def download_file(remote_key: str, local_path: str) -> None:
    client = get_client()
    client.download_file(BUCKET_NAME, remote_key, local_path)


def list_files() -> list:
    client = get_client()
    response = client.list_objects_v2(Bucket=BUCKET_NAME)
    return [obj["Key"] for obj in response.get("Contents", [])]
