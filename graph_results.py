# graph_results.py
# Reads benchmark_results.csv and produces two graphs:
#   1. Throughput vs. file size
#   2. Throughput vs. chunk size
# Saves both as PNG files, ready to drop straight into your dissertation.

import csv
import matplotlib.pyplot as plt

rows = []
with open("benchmark_results.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# ---- Graph 1: throughput vs file size ----
size_rows = [r for r in rows if r["test"] == "file_size"]
labels = [r["label"] for r in size_rows]
throughputs = [float(r["throughput_mb_per_s"]) for r in size_rows]

plt.figure(figsize=(7, 5))
plt.bar(labels, throughputs, color="#4C72B0")
plt.xlabel("File size")
plt.ylabel("Throughput (MB/s)")
plt.title("Encryption throughput vs. file size (1MB chunk size)")
plt.tight_layout()
plt.savefig("graph_throughput_vs_filesize.png", dpi=150)
print("Saved graph_throughput_vs_filesize.png")

# ---- Graph 2: throughput vs chunk size ----
chunk_rows = [r for r in rows if r["test"] == "chunk_size"]
labels2 = [r["label"] for r in chunk_rows]
throughputs2 = [float(r["throughput_mb_per_s"]) for r in chunk_rows]

plt.figure(figsize=(7, 5))
plt.bar(labels2, throughputs2, color="#DD8452")
plt.xlabel("Chunk size")
plt.ylabel("Throughput (MB/s)")
plt.title("Encryption throughput vs. chunk size (fixed 20MB file)")
plt.tight_layout()
plt.savefig("graph_throughput_vs_chunksize.png", dpi=150)
print("Saved graph_throughput_vs_chunksize.png")

# ---- Graph 3 (bonus): encrypt vs decrypt time vs file size ----
sizes_mb = [float(r["size_bytes"]) / (1024 * 1024) for r in size_rows]
encrypt_times = [float(r["avg_encrypt_seconds"]) for r in size_rows]
decrypt_times = [float(r["avg_decrypt_seconds"]) for r in size_rows]

plt.figure(figsize=(7, 5))
plt.plot(sizes_mb, encrypt_times, marker="o", label="Encrypt")
plt.plot(sizes_mb, decrypt_times, marker="o", label="Decrypt")
plt.xlabel("File size (MB)")
plt.ylabel("Time (seconds)")
plt.title("Encrypt/decrypt time vs. file size")
plt.legend()
plt.tight_layout()
plt.savefig("graph_time_vs_filesize.png", dpi=150)
print("Saved graph_time_vs_filesize.png")

print("\nAll graphs saved. Check your project folder for the .png files.")