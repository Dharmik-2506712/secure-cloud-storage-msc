# chunked_encrypt.py
# Encrypts a file in fixed-size chunks instead of all at once.
# Each chunk gets its own nonce (prefix + chunk index) and the chunk
# index is baked into the authentication itself (as "associated data"),
# so an attacker can't reorder, duplicate, or drop chunks without the
# decryption step noticing.

import os
import struct
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

INPUT_FILE = "secret.txt"          # try this on a bigger file later too
OUTPUT_FILE = "secret.txt.enc2"
CHUNK_SIZE = 1024 * 1024           # 1 MB per chunk

password = input("Enter a password to encrypt with: ")

salt = os.urandom(16)
nonce_prefix = os.urandom(8)       # 8 random bytes, fixed for this whole file

kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
key = kdf.derive(password.encode("utf-8"))
aesgcm = AESGCM(key)

with open(INPUT_FILE, "rb") as infile, open(OUTPUT_FILE, "wb") as outfile:
    # Header: salt, then the nonce prefix. Needed again to decrypt.
    outfile.write(salt)
    outfile.write(nonce_prefix)

    chunk_index = 0
    while True:
        chunk = infile.read(CHUNK_SIZE)
        if not chunk:
            break

        # Nonce = 8-byte prefix + 4-byte chunk counter = 12 bytes, unique per chunk
        nonce = nonce_prefix + struct.pack(">I", chunk_index)

        # "Associated data" — not encrypted, but authenticated. Binding the
        # chunk index here means: if an attacker swaps chunk 3 and chunk 5,
        # decryption will fail, because chunk 5's data was authenticated
        # against index 5, not index 3.
        aad = struct.pack(">I", chunk_index)

        ciphertext = aesgcm.encrypt(nonce, chunk, aad)
        outfile.write(ciphertext)

        print(f"Encrypted chunk {chunk_index} ({len(chunk)} bytes)")
        chunk_index += 1

print(f"\nDone. {chunk_index} chunk(s) written to {OUTPUT_FILE}")