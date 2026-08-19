# test_crypto_utils.py
# Automated tests for crypto_utils.py — proves the core encryption
# engine behaves correctly, not just "it worked when I tried it once."
#
# Run with: pytest -v

import os
import struct
import pytest
import crypto_utils


def test_roundtrip_small_file(tmp_path):
    """Encrypting then decrypting a small file should return the exact
    original content, given the correct password."""
    original = tmp_path / "original.txt"
    encrypted = tmp_path / "original.enc"
    decrypted = tmp_path / "original_decrypted.txt"

    original.write_bytes(b"Hello, this is a test file.")

    crypto_utils.encrypt_file(str(original), str(encrypted), "correct-password")
    success = crypto_utils.decrypt_file(str(encrypted), str(decrypted), "correct-password")

    assert success is True
    assert decrypted.read_bytes() == original.read_bytes()


def test_roundtrip_multi_chunk_file(tmp_path):
    """A file bigger than one chunk should still decrypt correctly —
    this proves the chunking logic itself, not just the trivial case."""
    original = tmp_path / "big.bin"
    encrypted = tmp_path / "big.enc"
    decrypted = tmp_path / "big_decrypted.bin"

    # Slightly more than 2 chunks' worth of random data
    data = os.urandom(int(crypto_utils.CHUNK_SIZE * 2.3))
    original.write_bytes(data)

    crypto_utils.encrypt_file(str(original), str(encrypted), "correct-password")
    success = crypto_utils.decrypt_file(str(encrypted), str(decrypted), "correct-password")

    assert success is True
    assert decrypted.read_bytes() == data


def test_empty_file(tmp_path):
    """An empty file is an edge case worth checking explicitly."""
    original = tmp_path / "empty.txt"
    encrypted = tmp_path / "empty.enc"
    decrypted = tmp_path / "empty_decrypted.txt"

    original.write_bytes(b"")

    crypto_utils.encrypt_file(str(original), str(encrypted), "correct-password")
    success = crypto_utils.decrypt_file(str(encrypted), str(decrypted), "correct-password")

    assert success is True
    assert decrypted.read_bytes() == b""


def test_wrong_password_is_rejected(tmp_path):
    """Decrypting with the wrong password must fail cleanly, not
    silently return garbage."""
    original = tmp_path / "secret.txt"
    encrypted = tmp_path / "secret.enc"
    decrypted = tmp_path / "secret_decrypted.txt"

    original.write_bytes(b"top secret content")

    crypto_utils.encrypt_file(str(original), str(encrypted), "right-password")
    success = crypto_utils.decrypt_file(str(encrypted), str(decrypted), "WRONG-password")

    assert success is False
    assert not decrypted.exists()  # nothing should be written on failure


def test_tampered_ciphertext_is_rejected(tmp_path):
    """If someone modifies the encrypted file after the fact (simulating
    an attacker with access to the storage), decryption must fail."""
    original = tmp_path / "secret.txt"
    encrypted = tmp_path / "secret.enc"
    decrypted = tmp_path / "secret_decrypted.txt"

    original.write_bytes(b"top secret content")
    crypto_utils.encrypt_file(str(original), str(encrypted), "a-password")

    # Flip a byte near the end of the encrypted file to simulate tampering
    data = bytearray(encrypted.read_bytes())
    data[-1] ^= 0xFF
    encrypted.write_bytes(bytes(data))

    success = crypto_utils.decrypt_file(str(encrypted), str(decrypted), "a-password")

    assert success is False


def test_truncated_file_is_rejected(tmp_path):
    """If the encrypted file is cut short (e.g. an interrupted upload),
    decryption must fail rather than silently return partial/wrong data."""
    original = tmp_path / "secret.txt"
    encrypted = tmp_path / "secret.enc"
    decrypted = tmp_path / "secret_decrypted.txt"

    original.write_bytes(os.urandom(500))
    crypto_utils.encrypt_file(str(original), str(encrypted), "a-password")

    # Chop off the last 5 bytes to simulate a truncated/incomplete file
    data = encrypted.read_bytes()
    encrypted.write_bytes(data[:-5])

    success = crypto_utils.decrypt_file(str(encrypted), str(decrypted), "a-password")

    assert success is False