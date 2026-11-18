"""The Python side of the round-trip proof: prints one field per line, using
the standard library's csv module. Must byte-match cpp/tools/csv_dump.cpp on
the SAME input file.

Run:  python -m pinjamlab.tools.csv_dump <path>
"""
from __future__ import annotations

import csv
import sys


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: csv_dump <path>", file=sys.stderr)
        return 2

    # newline="": required, or the csv module's own universal-newline
    # translation fights the module's own \r\n handling -- the classic bug
    # named in the module text.
    with open(argv[1], newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        out = sys.stdout.buffer
        for record in reader:
            for field in record:
                out.write(field.encode("utf-8"))
                out.write(b"\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
