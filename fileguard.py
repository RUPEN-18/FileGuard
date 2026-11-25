"""Create and compare SHA-256 directory snapshots."""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root, excluded=None):
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("Root must be an existing directory")
    excluded = excluded.resolve() if excluded else None
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.resolve() == excluded:
            continue
        result[path.relative_to(root).as_posix()] = sha256(path)
    return result


def compare(before, after):
    return {"added": sorted(after.keys() - before.keys()),
            "removed": sorted(before.keys() - after.keys()),
            "modified": sorted(k for k in before.keys() & after.keys() if before[k] != after[k])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["snapshot", "verify"])
    parser.add_argument("directory", type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.action == "snapshot":
            if args.manifest.exists():
                raise ValueError("Manifest already exists; choose a new output path")
            files = snapshot(args.directory, args.manifest)
            with args.manifest.open("x", encoding="utf-8") as handle:
                json.dump({"version": 1, "algorithm": "sha256", "files": files}, handle, indent=2)
                handle.write("\n")
            print(f"Saved {len(files)} file hashes to {args.manifest}")
        else:
            data = json.loads(args.manifest.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("version") != 1 or data.get("algorithm") != "sha256" or not isinstance(data.get("files"), dict):
                raise ValueError("Invalid manifest format")
            before = data["files"]
            if any(not isinstance(v, str) or len(v) != 64 or any(c not in "0123456789abcdef" for c in v) for v in before.values()):
                raise ValueError("Invalid SHA-256 value in manifest")
            changes = compare(before, snapshot(args.directory, args.manifest))
            for label, paths in changes.items():
                print(f"{label.upper()}: {len(paths)}")
                for path in paths:
                    print(f"  {path}")
            if any(changes.values()):
                return 1
            print("Integrity check passed: no changes detected.")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"FileGuard: {exc}\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
