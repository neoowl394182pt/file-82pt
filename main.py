#!/usr/bin/env python3
"""
A tiny file deduplication utility.
Scan a directory, list files that share identical contents.
"""

import argparse, hashlib, os, sys

def file_hash(path, block=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()

def find_dups(root):
    hashes = {}
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            try:
                h = file_hash(fp)
            except (OSError, PermissionError):
                continue
            hashes.setdefault(h, []).append(fp)
    return [v for v in hashes.values() if len(v) > 1]

def main():
    parser = argparse.ArgumentParser(description="Find duplicate files.")
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("-d", "--delete", action="store_true",
                        help="Delete duplicates, keep one copy")
    args = parser.parse_args()

    dups = find_dups(args.path)
    if not dups:
        print("No duplicates found.")
        return

    print(f"Found {len(dups)} groups of duplicates:")
    for group in dups:
        print("\n".join(group))
        print("-" * 40)

    if args.delete:
        for group in dups:
            for fp in group[1:]:
                try:
                    os.remove(fp)
                    print(f"Deleted {fp}")
                except Exception as e:
                    print(f"Failed to delete {fp}: {e}")

if __name__ == "__main__":
    main()