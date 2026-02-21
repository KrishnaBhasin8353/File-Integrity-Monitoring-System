import os
import hashlib
import json
from datetime import datetime

HASH_DB = "hash_db.json"
LOG_FILE = "logs.txt"


def calculate_hash(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None


def scan_folder(folder_path):
    file_hashes = {}

    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_hash = calculate_hash(full_path)
            if file_hash:
                file_hashes[full_path] = file_hash

    return file_hashes


def save_hashes(hash_data):
    with open(HASH_DB, "w") as f:
        json.dump(hash_data, f, indent=4)


def load_hashes():
    if not os.path.exists(HASH_DB):
        return {}
    with open(HASH_DB, "r") as f:
        return json.load(f)


def log_event(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")


def compare_hashes(old_hashes, new_hashes):
    old_files = set(old_hashes.keys())
    new_files = set(new_hashes.keys())

    for file in old_files & new_files:
        if old_hashes[file] != new_hashes[file]:
            print(f"[MODIFIED] {file}")
            log_event(f"MODIFIED: {file}")

    for file in old_files - new_files:
        print(f"[DELETED] {file}")
        log_event(f"DELETED: {file}")

    for file in new_files - old_files:
        print(f"[NEW FILE] {file}")
        log_event(f"NEW FILE: {file}")


def main():
    folder_path = input("Enter folder path to monitor: ")

    if not os.path.exists(folder_path):
        print("Folder does not exist.")
        return

    print("Scanning folder...")
    new_hashes = scan_folder(folder_path)
    old_hashes = load_hashes()

    if not old_hashes:
        print("Creating baseline...")
        save_hashes(new_hashes)
        print("Baseline created successfully.")
    else:
        print("Comparing with previous records...")
        compare_hashes(old_hashes, new_hashes)
        save_hashes(new_hashes)
        print("Scan complete.")


if __name__ == "__main__":
    main()
