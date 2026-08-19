# decrypt_file.py
# Reads an encrypted file, asks for the password, and writes the
# original plaintext back out to a new file.

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

INPUT_FILE = "secret.txt.enc"
OUTPUT_FILE = "secret_decrypted.txt"

password = input("Enter the password to decrypt with: ")

with open(INPUT_FILE, "rb") as f:
    data = f.read()

# Undo the layout we wrote in encrypt_file.py:
# [16 bytes salt][12 bytes nonce][rest = ciphertext]
salt = data[0:16]
nonce = data[16:28]
ciphertext = data[28:]

kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
key = kdf.derive(password.encode("utf-8"))

aesgcm = AESGCM(key)

try:
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
except InvalidTag:
    print("Decryption failed — wrong password, or the file was tampered with.")
    exit(1)

with open(OUTPUT_FILE, "wb") as f:
    f.write(plaintext)

print(f"Decrypted {INPUT_FILE} -> {OUTPUT_FILE}")
print("Contents:")
print(plaintext.decode("utf-8"))