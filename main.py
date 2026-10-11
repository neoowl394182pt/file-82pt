"""Simple file deduplication utility."""
import os, sys, hashlib, argparse

def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description='Find duplicate files.')
    parser.add_argument('directory', help='Directory to scan')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='Delete duplicates, keep one copy')
    args = parser.parse_args()

    seen = {}
    for root, _, files in os.walk(args.directory):
        for name in files:
            path = os.path.join(root, name)
            h = hash_file(path)
            if h:
                seen.setdefault(h, []).append(path)

    duplicates = [paths for paths in seen.values() if len(paths) > 1]
    if not duplicates:
        print('No duplicates found.')
        return

    for group in duplicates:
        print('Duplicate group:')
        for p in group:
            print(f'  {p}')
        print()
    if args.delete:
        for group in duplicates:
            for dup in group[1:]:
                try:
                    os.remove(dup)
                    print(f'Deleted {dup}')
                except OSError as e:
                    print(f'Error deleting {dup}: {e}', file=sys.stderr)