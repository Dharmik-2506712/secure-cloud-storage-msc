import os
import struct
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

CHUNK_SIZE = 1024 * 1024
TAG_SIZE = 16


def encrypt_file(input_path: str, output_path: str, password: str, chunk_size: int = CHUNK_SIZE) -> None:
    """Encrypt input_path, writing the encrypted result to output_path."""
    salt = os.urandom(16)
    nonce_prefix = os.urandom(8)

    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
    key = kdf.derive(password.encode("utf-8"))
    aesgcm = AESGCM(key)

    with open(input_path, "rb") as infile, open(output_path, "wb") as outfile:
        outfile.write(salt)
        outfile.write(nonce_prefix)

        chunk_index = 0
        while True:
            chunk = infile.read(chunk_size)
            if not chunk:
                break
            nonce = nonce_prefix + struct.pack(">I", chunk_index)
            aad = struct.pack(">I", chunk_index)
            ciphertext = aesgcm.encrypt(nonce, chunk, aad)
            outfile.write(ciphertext)
            chunk_index += 1


def decrypt_file(input_path: str, output_path: str, password: str, chunk_size: int = CHUNK_SIZE) -> bool:
    """Decrypt input_path, writing the result to output_path.
    Returns True on success, False if the password was wrong or the
    data was tampered with (in which case output_path is not written)."""
    with open(input_path, "rb") as f:
        salt = f.read(16)
        nonce_prefix = f.read(8)

        kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
        key = kdf.derive(password.encode("utf-8"))
        aesgcm = AESGCM(key)

        chunk_index = 0
        output_bytes = b""

        while True:
            encrypted_chunk = f.read(chunk_size + TAG_SIZE)
            if not encrypted_chunk:
                break

            nonce = nonce_prefix + struct.pack(">I", chunk_index)
            aad = struct.pack(">I", chunk_index)

            try:
                plaintext_chunk = aesgcm.decrypt(nonce, encrypted_chunk, aad)
            except InvalidTag:
                return False

            output_bytes += plaintext_chunk
            chunk_index += 1

    with open(output_path, "wb") as f:
        f.write(output_bytes)
    return True