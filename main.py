"""Entrypoint for news-image-20261120 v3.

Runs draw_poster.py and writes entry.png to $MAKEFUN_OUTPUT_DIR
(default /output). Deterministic: two runs produce byte-identical output.
Standard library only.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import draw_poster


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    size = draw_poster.render(out_path)
    print(f"wrote {out_path} ({size} bytes)")


if __name__ == "__main__":
    main()
