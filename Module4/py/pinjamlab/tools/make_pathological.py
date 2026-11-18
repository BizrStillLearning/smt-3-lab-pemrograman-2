"""Writes the four-row file chosen specifically to break a naive parser:
an embedded comma, a doubled quote, an embedded newline, and a multi-byte
UTF-8 character. Run once to (re)generate sample-data/pathological.csv.

Run:  python -m pinjamlab.tools.make_pathological > sample-data/pathological.csv

Written straight to sys.stdout.buffer with an explicit UTF-8 TextIOWrapper
and newline="" -- stdout in TEXT mode applies universal-newline translation
on top of csv.writer's own "\r\n", which doubles every \r, and the platform
default encoding is not guaranteed to be UTF-8 when output is redirected.
Both mistakes were made once, while authoring this file, and are exactly the
"missing newline=''" and "silent wrong encoding" bugs the module names.
"""
from __future__ import annotations

import csv
import io
import sys


def main() -> int:
    out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")
    writer = csv.writer(out, lineterminator="\r\n")
    writer.writerow(["loanId", "tag", "member", "note"])
    writer.writerow(["L-001", "LP-001", "M-101", "Budi, Santoso"])
    writer.writerow(["L-002", "PR-014", "M-102", 'Ali "Bob" Chan'])
    writer.writerow(["L-003", "OS-003", "M-103", "line one\nline two"])
    writer.writerow(["L-004", "MC-007", "M-104", "M\u00fcller"])
    out.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
