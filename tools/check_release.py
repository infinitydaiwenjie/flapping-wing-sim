"""Check the exact public file list and hashes without running a simulation."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "PUBLIC_MANIFEST.json"


def check():
    entries = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))["files"]
    expected = {}
    errors = []
    for entry in entries:
        name = entry["path"]
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
            errors.append("Unsafe manifest path: " + name)
            continue
        if name in expected or name == MANIFEST:
            errors.append("Duplicate or self-referencing manifest entry: " + name)
        expected[name] = entry
    actual = set()
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if relative.parts[0] == ".git":
            continue
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            errors.append("Link is not allowed: " + relative.as_posix())
        elif path.is_file():
            actual.add(relative.as_posix())
    for name in sorted(actual - set(expected) - {MANIFEST}):
        errors.append("Unexpected file: " + name)
    for name in sorted(set(expected) - actual):
        errors.append("Missing file: " + name)
    for name in sorted(set(expected) & actual):
        path = ROOT / name
        entry = expected[name]
        if not path.resolve().is_relative_to(ROOT):
            errors.append("Path escapes public root: " + name)
            continue
        if path.stat().st_size != entry["bytes"]:
            errors.append("Size mismatch: " + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            errors.append("Content mismatch: " + name)
    if errors:
        print("Public release check failed:")
        for error in errors:
            print("- " + error)
        return 1
    print("Public file manifest verified. No additional payload files found.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(check())
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print("Unable to verify public manifest: " + str(exc))
        sys.exit(1)
