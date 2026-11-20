# news-image-20261120 entry (Python 3.13, standard library only).
# The finished poster is entry.png beside this file; the program
# copies it to /output/entry.png. No network, no randomness:
# every run writes the same bytes.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in
# for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil
from pathlib import Path


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__).with_name("entry.png"), out_dir / "entry.png")


if __name__ == "__main__":
    main()
