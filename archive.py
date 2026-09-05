#!/usr/bin/env python3
"""Verify every archived file and optionally restore the oversized review scene."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parent


def project_path(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Archive path escapes the project: " + relative)
    return path


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def check_file(entry):
    path = project_path(entry["path"])
    if not path.is_file():
        raise ValueError("Missing file: " + entry["path"])
    if path.stat().st_size != entry["bytes"] or digest(path) != entry["sha256"]:
        raise ValueError("Checksum mismatch: " + entry["path"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore", action="store_true", help="Restore the older review scene")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "archive_manifest.json").read_text())
    for entry in manifest["files"]:
        check_file(entry)
    print("PASS: {} archived files match SHA-256.".format(len(manifest["files"])))
    archive = json.loads((ROOT / "large_file_archive.json").read_text())
    for entry in archive["files"]:
        target = project_path(entry["path"])
        combined = hashlib.sha256()
        total = 0
        for part in entry["parts"]:
            check_file(part)
            with project_path(part["path"]).open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    combined.update(block)
                    total += len(block)
        if total != entry["bytes"] or combined.hexdigest() != entry["sha256"]:
            raise ValueError("Combined archive checksum mismatch: " + entry["path"])
        if target.exists():
            check_file(entry)
            print("PASS: existing original matches: " + entry["path"])
        elif args.restore:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".restore-", delete=False) as output:
                    temporary = Path(output.name)
                    for part in entry["parts"]:
                        with project_path(part["path"]).open("rb") as stream:
                            for block in iter(lambda: stream.read(1024 * 1024), b""):
                                output.write(block)
                if temporary.stat().st_size != entry["bytes"] or digest(temporary) != entry["sha256"]:
                    raise ValueError("Restored file checksum mismatch: " + entry["path"])
                # Hard-link creation fails if a file appeared meanwhile; never overwrite it.
                os.link(temporary, target)
                print("RESTORED: " + entry["path"])
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        else:
            print("PASS: archive parts preserve original bytes: " + entry["path"])


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as exc:
        raise SystemExit("FAIL: " + str(exc))
