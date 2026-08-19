# main.py
# The actual program you run. Ties together crypto_utils.py and
# storage_utils.py into one simple menu-driven tool.

import os
import getpass
import crypto_utils
import storage_utils

TEMP_ENC_FILE = "_temp.enc"


def do_upload():
    local_path = input("Path to the file you want to upload: ").strip()
    if not os.path.isfile(local_path):
        print(f"No such file: {local_path}")
        return

    remote_key = input("Name to give it in the cloud (e.g. myphoto.enc): ").strip()
    password = getpass.getpass("Password to encrypt with: ")

    crypto_utils.encrypt_file(local_path, TEMP_ENC_FILE, password)
    storage_utils.upload_file(TEMP_ENC_FILE, remote_key)
    os.remove(TEMP_ENC_FILE)

    print(f"Done. '{local_path}' is now stored encrypted in the cloud as '{remote_key}'.")


def do_download():
    remote_key = input("Name of the file in the cloud to download: ").strip()
    output_path = input("Where to save the decrypted file (e.g. downloaded.txt): ").strip()
    password = getpass.getpass("Password to decrypt with: ")

    storage_utils.download_file(remote_key, TEMP_ENC_FILE)
    success = crypto_utils.decrypt_file(TEMP_ENC_FILE, output_path, password)
    os.remove(TEMP_ENC_FILE)

    if success:
        print(f"Done. Decrypted and saved to '{output_path}'.")
    else:
        print("Failed — wrong password, or the file was tampered with.")


def do_list():
    files = storage_utils.list_files()
    if not files:
        print("No files stored yet.")
        return
    print("Files currently stored (encrypted):")
    for f in files:
        print(f"  - {f}")


def main():
    while True:
        print("\n--- Secure Cloud Storage ---")
        print("1. Upload and encrypt a file")
        print("2. Download and decrypt a file")
        print("3. List stored files")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            do_upload()
        elif choice == "2":
            do_download()
        elif choice == "3":
            do_list()
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Not a valid option, try again.")


if __name__ == "__main__":
    main()