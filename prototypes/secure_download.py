# secure_download.py
# Reverses secure_upload.py: downloads the encrypted object from MinIO,
# then decrypts it locally, chunk by chunk, rejecting anything tampered
# with or protected by the wrong password.

import struct
import boto3
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# ---- Your MinIO details ----
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
BUCKET_NAME = "test-bucket"
ENDPOINT_URL = "http://127.0.0.1:9000"
# -----------------------------

CHUNK_SIZE = 1024 * 1024
TAG_SIZE = 16
REMOTE_KEY = "secret.enc"                    # must match what you uploaded as
TEMP_ENCRYPTED_FILE = "temp_download.enc"    # scratch file, deleted after
OUTPUT_FILE = "secret_from_cloud.txt"        # the final decrypted result

password = input("Enter the password to decrypt with: ")

# ---- Step 1: download the encrypted object from MinIO ----
client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

client.download_file(BUCKET_NAME, REMOTE_KEY, TEMP_ENCRYPTED_FILE)
print(f"Downloaded '{REMOTE_KEY}' from bucket -> {TEMP_ENCRYPTED_FILE}")

# ---- Step 2: decrypt it locally (same logic as chunked_decrypt.py) ----
with open(TEMP_ENCRYPTED_FILE, "rb") as f:
    salt = f.read(16)
    nonce_prefix = f.read(8)

    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
    key = kdf.derive(password.encode("utf-8"))
    aesgcm = AESGCM(key)

    chunk_index = 0
    output_bytes = b""

    while True:
        encrypted_chunk = f.read(CHUNK_SIZE + TAG_SIZE)
        if not encrypted_chunk:
            break

        nonce = nonce_prefix + struct.pack(">I", chunk_index)
        aad = struct.pack(">I", chunk_index)

        try:
            plaintext_chunk = aesgcm.decrypt(nonce, encrypted_chunk, aad)
        except InvalidTag:
            print(f"Decryption failed at chunk {chunk_index} — wrong password "
                  f"or the data was tampered with.")
            exit(1)

        output_bytes += plaintext_chunk
        chunk_index += 1

with open(OUTPUT_FILE, "wb") as f:
    f.write(output_bytes)

print(f"Decrypted successfully -> {OUTPUT_FILE} ({chunk_index} chunk(s))")
print("Contents:")
print(output_bytes.decode("utf-8"))

# ---- Step 3: clean up temp file ----
import os
os.remove(TEMP_ENCRYPTED_FILE)