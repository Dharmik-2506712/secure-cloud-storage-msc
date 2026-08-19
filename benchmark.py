# benchmark.py
# Measures encryption/decryption performance at different file sizes
# and chunk sizes. Answers RQ2: what is the performance overhead of
# client-side encryption, and how does chunk size affect it?
#
# Results are saved to benchmark_results.csv so you can open it in
# Excel or plot it with matplotlib for your dissertation.

import os
import time
import csv
import crypto_utils

# File sizes to test, in bytes
FILE_SIZES = {
    "1MB": 1 * 1024 * 1024,
    "5MB": 5 * 1024 * 1024,
    "20MB": 20 * 1024 * 1024,
    "50MB": 50 * 1024 * 1024,
}

# Chunk sizes to test (only used in the chunk-size sensitivity test)
CHUNK_SIZES = {
    "1MB chunks": 1 * 1024 * 1024,
    "4MB chunks": 4 * 1024 * 1024,
    "16MB chunks": 16 * 1024 * 1024,
}

REPEATS = 3  # run each timing 3 times and average, to smooth out noise

TEMP_DIR = "benchmark_temp"
os.makedirs(TEMP_DIR, exist_ok=True)

results = []  # will hold rows to write to CSV


def make_test_file(path, size_bytes):
    with open(path, "wb") as f:
        f.write(os.urandom(size_bytes))


def time_it(func):
    start = time.perf_counter()
    func()
    return time.perf_counter() - start


print("=" * 60)
print("PART 1: Encryption/decryption time vs. file size")
print("(using the default 1MB chunk size)")
print("=" * 60)

for label, size in FILE_SIZES.items():
    original = os.path.join(TEMP_DIR, "test_input.bin")
    encrypted = os.path.join(TEMP_DIR, "test_input.enc")
    decrypted = os.path.join(TEMP_DIR, "test_output.bin")

    make_test_file(original, size)

    encrypt_times = []
    decrypt_times = []

    for _ in range(REPEATS):
        t = time_it(lambda: crypto_utils.encrypt_file(original, encrypted, "benchmark-password"))
        encrypt_times.append(t)

        t = time_it(lambda: crypto_utils.decrypt_file(encrypted, decrypted, "benchmark-password"))
        decrypt_times.append(t)

    avg_encrypt = sum(encrypt_times) / len(encrypt_times)
    avg_decrypt = sum(decrypt_times) / len(decrypt_times)
    throughput_mb_s = (size / (1024 * 1024)) / avg_encrypt

    print(f"{label:6} | encrypt: {avg_encrypt:.4f}s  decrypt: {avg_decrypt:.4f}s  "
          f"throughput: {throughput_mb_s:.1f} MB/s")

    results.append({
        "test": "file_size",
        "label": label,
        "size_bytes": size,
        "chunk_size_bytes": crypto_utils.CHUNK_SIZE,
        "avg_encrypt_seconds": round(avg_encrypt, 5),
        "avg_decrypt_seconds": round(avg_decrypt, 5),
        "throughput_mb_per_s": round(throughput_mb_s, 2),
    })

print()
print("=" * 60)
print("PART 2: Encryption time vs. chunk size")
print("(using a fixed 20MB file)")
print("=" * 60)

fixed_size = FILE_SIZES["20MB"]
original = os.path.join(TEMP_DIR, "test_input2.bin")
make_test_file(original, fixed_size)

for label, chunk_size in CHUNK_SIZES.items():
    encrypted = os.path.join(TEMP_DIR, "test_input2.enc")
    decrypted = os.path.join(TEMP_DIR, "test_output2.bin")

    encrypt_times = []
    for _ in range(REPEATS):
        t = time_it(lambda: crypto_utils.encrypt_file(
            original, encrypted, "benchmark-password", chunk_size=chunk_size))
        encrypt_times.append(t)

    avg_encrypt = sum(encrypt_times) / len(encrypt_times)
    throughput_mb_s = (fixed_size / (1024 * 1024)) / avg_encrypt

    print(f"{label:12} | encrypt: {avg_encrypt:.4f}s  throughput: {throughput_mb_s:.1f} MB/s")

    results.append({
        "test": "chunk_size",
        "label": label,
        "size_bytes": fixed_size,
        "chunk_size_bytes": chunk_size,
        "avg_encrypt_seconds": round(avg_encrypt, 5),
        "avg_decrypt_seconds": None,
        "throughput_mb_per_s": round(throughput_mb_s, 2),
    })

# Save everything to a CSV file for your dissertation graphs
csv_path = "benchmark_results.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"\nResults saved to {csv_path}")