#!/usr/bin/env python3
"""
Run this after cloning/downloading the GitHub repo these files were
uploaded to. Reassembles both chunked files back into their originals
and verifies them against the recorded checksums, so you know the
transfer (upload -> download -> reassembly) didn't corrupt anything.

Usage: python3 reassemble.py
"""
import hashlib
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "kokoro-v1.0.fp16.onnx": "onnx-chunks",
    "voices-v1.0.bin": "voices-chunks",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_checksums():
    expected = {}
    with open(os.path.join(HERE, "checksums.txt")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            digest, name = line.split("  ", 1)
            expected[name] = digest
    return expected


def main():
    expected = load_checksums()
    ok = True

    for out_name, chunk_dir in FILES.items():
        parts = sorted(glob.glob(os.path.join(HERE, chunk_dir, "*.part*")))
        if not parts:
            print(f"No chunks found in {chunk_dir}/ -- did the download finish?")
            ok = False
            continue

        out_path = os.path.join(HERE, out_name)
        print(f"Reassembling {len(parts)} chunks -> {out_path}")
        with open(out_path, "wb") as out:
            for part in parts:
                with open(part, "rb") as p:
                    out.write(p.read())

        actual = sha256(out_path)
        if actual == expected.get(out_name):
            print(f"OK: {out_name} checksum matches")
        else:
            print(f"MISMATCH: {out_name} -- expected {expected.get(out_name)}, got {actual}")
            ok = False

    if ok:
        print("\nAll good. kokoro-v1.0.fp16.onnx and voices-v1.0.bin are ready to use.")
    else:
        print("\nSomething didn't match -- don't use these files yet.")
        sys.exit(1)


if __name__ == "__main__":
    main()
