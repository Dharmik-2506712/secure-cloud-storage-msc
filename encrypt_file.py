# encrypt_file.py
# Reads a real file from disk, encrypts it, and writes an encrypted
# version to disk. This builds directly on crypto_basics.py — same
# scrypt + AES-GCM, just applied to file bytes instead of a short string.

import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

INPUT_FILE = "secret.txt"
OUTPUT_FILE = "secret.txt.enc"

password = input("Enter a password to encrypt with: ")

# Read the whole file as raw bytes (not text — this works for any file type)
with open(INPUT_FILE, "rb") as f:
    plaintext = f.read()

salt = os.urandom(16)
nonce = os.urandom(12)

kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
key = kdf.derive(password.encode("utf-8"))

aesgcm = AESGCM(key)
ciphertext = aesgcm.encrypt(nonce, plaintext, None)

# We need the salt and nonce again later to decrypt, so we store them
# alongside the ciphertext in the output file. None of this is secret —
# only the password (which never gets stored) makes decryption possible.
# Layout: [16 bytes salt][12 bytes nonce][rest = ciphertext]
with open(OUTPUT_FILE, "wb") as f:
    f.write(salt)
    f.write(nonce)
    f.write(ciphertext)

print(f"Encrypted {INPUT_FILE} ({len(plaintext)} bytes) -> {OUTPUT_FILE}")
print("Open secret.txt.enc in VS Code — it should look like unreadable noise.")