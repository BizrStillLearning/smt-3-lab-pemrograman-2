"""Generates a large, deterministic loans CSV for the responsiveness
measurement (Lab 2.3): reproduce the freeze on a 5,000-row file.

Run:  python -m pinjamlab.tools.make_big_loans 5000 > sample-data/big-loans.csv
"""
from __future__ import annotations

import csv
import io
import sys


def main(argv: list[str]) -> int:
    n = int(argv[1]) if len(argv) > 1 else 5000
    out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")
    writer = csv.writer(out)
    writer.writerow(["loanId", "tag", "member", "days", "rate"])
    tags = ["LP-001", "LP-002", "LP-003", "PR-014", "OS-003"]
    for i in range(1, n + 1):
        writer.writerow([f"L-{i:05d}", tags[i % len(tags)], f"M-{100 + i % 50}",
                          1 + i % 30, 50000])
    out.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
