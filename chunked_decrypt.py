# chunked_decrypt.py
# Reads a chunked-encrypted file, decrypts each chunk in order, and
# writes the original plaintext back out. Rejects the file if any chunk
# fails authentication (wrong password, tampering, or reordered chunks).

import struct
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

INPUT_FILE = "secret.txt.enc2"
OUTPUT_FILE = "secret_decrypted2.txt"
CHUNK_SIZE = 1024 * 1024
TAG_SIZE = 16   # AES-GCM appends a 16-byte authentication tag per chunk

password = input("Enter the password to decrypt with: ")

with open(INPUT_FILE, "rb") as f:
    salt = f.read(16)
    nonce_prefix = f.read(8)

    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
    key = kdf.derive(password.encode("utf-8"))
    aesgcm = AESGCM(key)

    chunk_index = 0
    output_bytes = b""

    while True:
        # Ciphertext chunks are up to CHUNK_SIZE plaintext + 16-byte tag
        encrypted_chunk = f.read(CHUNK_SIZE + TAG_SIZE)
        if not encrypted_chunk:
            break

        nonce = nonce_prefix + struct.pack(">I", chunk_index)
        aad = struct.pack(">I", chunk_index)

        try:
            plaintext_chunk = aesgcm.decrypt(nonce, encrypted_chunk, aad)
        except InvalidTag:
            print(f"Decryption failed at chunk {chunk_index} — wrong password, "
                  f"tampering, or chunks were reordered.")
            exit(1)

        output_bytes += plaintext_chunk
        print(f"Decrypted chunk {chunk_index} ({len(plaintext_chunk)} bytes)")
        chunk_index += 1

with open(OUTPUT_FILE, "wb") as f:
    f.write(output_bytes)

print(f"\nDone. Wrote {len(output_bytes)} bytes to {OUTPUT_FILE}")