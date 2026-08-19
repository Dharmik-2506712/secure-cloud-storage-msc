# crypto_basics.py
# The smallest possible example of: password -> key -> encrypt -> decrypt

import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---- Step 1: turn a password into a 256-bit (32-byte) key ----
# We NEVER use the password itself as the key. Instead we run it through
# "scrypt" — a slow, memory-hungry function designed to make password
# guessing attacks expensive. "salt" is random data that makes sure two
# people with the same password still get different keys.

password = "correct horse battery staple"
salt = os.urandom(16)  # 16 random bytes, different every time

kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
key = kdf.derive(password.encode("utf-8"))

print("Derived key (hex):", key.hex())

# ---- Step 2: encrypt a message using that key ----
# AES-GCM is an "authenticated" cipher: it doesn't just hide the message,
# it also detects if the ciphertext was tampered with afterwards.

message = b"This is my secret file content."
nonce = os.urandom(12)  # a number used once — must never repeat for the same key

aesgcm = AESGCM(key)
ciphertext = aesgcm.encrypt(nonce, message, None)

print("Ciphertext (hex):", ciphertext.hex())

# ---- Step 3: decrypt it back ----
decrypted = aesgcm.decrypt(nonce, ciphertext, None)
print("Decrypted message:", decrypted.decode("utf-8"))

# ---- Step 4: prove tampering gets detected ----
tampered = bytearray(ciphertext)
tampered[0] ^= 0xFF  # flip some bits, simulating an attacker changing the data

try:
    aesgcm.decrypt(nonce, bytes(tampered), None)
    print("Uh oh — tampered data was accepted! (this should not happen)")
except Exception as e:
    print("Tampering correctly detected:", type(e).__name__)