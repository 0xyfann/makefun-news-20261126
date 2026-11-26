#!/usr/bin/env python3
"""Copy the built entry.png into the make.fun output directory.

Uses only the Python standard library. The destination is taken from the
MAKEFUN_OUTPUT_DIR environment variable, falling back to /output when the
variable is unset.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")

    if not os.path.isfile(src):
        sys.stderr.write("entry.png not found next to main.py; run draw_news.py first\n")
        return 2

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)

    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print(dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
