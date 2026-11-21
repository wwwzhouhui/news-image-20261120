#!/usr/bin/env python3
"""Entrypoint: copy the pre-rendered front page to the harness output dir.

Standard library only, no network, deterministic: the bytes written are
exactly the bytes of assets/entry.png, so repeated runs are identical.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    if not os.path.isfile(SRC):
        print(f"missing source image: {SRC}", file=sys.stderr)
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    dst = os.path.join(OUT_DIR, "entry.png")
    shutil.copyfile(SRC, dst)
    print(f"wrote {dst} ({os.path.getsize(dst)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
