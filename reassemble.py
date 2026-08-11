#!/usr/bin/env python3
"""
Run this after cloning the GitHub repo these files were pushed to.
Reassembles the chunked ONNX model back into a single file and verifies
both files against the recorded checksums, so you know the transfer
(clone -> reassembly) didn't corrupt anything.

Usage: python3 reassemble.py
"""
import hashlib
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


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

    # Reassemble the chunked ONNX model.
    parts = sorted(glob.glob(os.path.join(HERE, "onnx-chunks", "*.part*")))
    if not parts:
        print("No chunks found in onnx-chunks/ -- did the clone finish?")
        sys.exit(1)

    out_path = os.path.join(HERE, "kokoro-v1.0.fp16.onnx")
    print(f"Reassembling {len(parts)} chunks -> {out_path}")
    with open(out_path, "wb") as out:
        for part in parts:
            with open(part, "rb") as p:
                out.write(p.read())

    # Verify both files.
    ok = True
    for name in ("kokoro-v1.0.fp16.onnx", "voices-v1.0.bin"):
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print(f"MISSING: {name}")
            ok = False
            continue
        actual = sha256(path)
        if actual == expected.get(name):
            print(f"OK: {name} checksum matches")
        else:
            print(f"MISMATCH: {name} -- expected {expected.get(name)}, got {actual}")
            ok = False

    if ok:
        print("\nAll good. kokoro-v1.0.fp16.onnx and voices-v1.0.bin are ready to use.")
    else:
        print("\nSomething didn't match -- don't use these files yet.")
        sys.exit(1)


if __name__ == "__main__":
    main()
