# secure_upload.py
# Combines two things you've already built and tested separately:
#   1. Chunked AES-GCM encryption (from chunked_encrypt.py)
#   2. Uploading to MinIO via boto3 (from test_storage.py)
# The file is encrypted entirely on your machine BEFORE it ever touches
# the network — MinIO only ever receives ciphertext.

import os
import struct
import boto3
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---- Your MinIO details ----
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
BUCKET_NAME = "test-bucket"
ENDPOINT_URL = "http://127.0.0.1:9000"
# -----------------------------

CHUNK_SIZE = 1024 * 1024
LOCAL_FILE = "secret.txt"          # the real file you want to upload
TEMP_ENCRYPTED_FILE = "temp_upload.enc"   # scratch file, deleted after upload
REMOTE_KEY = "secret.enc"          # the name it will have inside the bucket

password = input("Enter a password to encrypt with: ")

# ---- Step 1: encrypt the file locally (same logic as chunked_encrypt.py) ----
salt = os.urandom(16)
nonce_prefix = os.urandom(8)

kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
key = kdf.derive(password.encode("utf-8"))
aesgcm = AESGCM(key)

with open(LOCAL_FILE, "rb") as infile, open(TEMP_ENCRYPTED_FILE, "wb") as outfile:
    outfile.write(salt)
    outfile.write(nonce_prefix)

    chunk_index = 0
    while True:
        chunk = infile.read(CHUNK_SIZE)
        if not chunk:
            break
        nonce = nonce_prefix + struct.pack(">I", chunk_index)
        aad = struct.pack(">I", chunk_index)
        ciphertext = aesgcm.encrypt(nonce, chunk, aad)
        outfile.write(ciphertext)
        chunk_index += 1

print(f"Encrypted {LOCAL_FILE} -> {TEMP_ENCRYPTED_FILE} ({chunk_index} chunk(s))")

# ---- Step 2: upload the encrypted file to MinIO (same logic as test_storage.py) ----
client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

with open(TEMP_ENCRYPTED_FILE, "rb") as f:
    client.upload_fileobj(f, BUCKET_NAME, REMOTE_KEY)

print(f"Uploaded encrypted file to bucket as '{REMOTE_KEY}'")

# ---- Step 3: clean up the local temp file ----
os.remove(TEMP_ENCRYPTED_FILE)
print("Removed local temp file — only the encrypted version now exists in the cloud.")

print("\nDone. MinIO stores only ciphertext — it never saw your password or plaintext.")