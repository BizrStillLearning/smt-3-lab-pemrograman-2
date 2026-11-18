"""io layer: load the catalogue, and persist loans as CSV.

`newline=""` is required in EVERY open() call in this file. Omitting it is
the single most common bug when people first use `csv` on Windows: the
module's own universal-newline translation and csv's "\r\n" writer double
up, producing a blank line between every record.
"""
from __future__ import annotations

import csv
from pathlib import Path

from ..domain.equipment import Equipment
from ..domain.loan import Loan

LOAN_FIELDS = ["loanId", "tag", "member", "days", "rate"]


def load_catalog(path: str | Path) -> list[Equipment]:
    items: list[Equipment] = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            items.append(Equipment(
                tag=row["tag"], model=row["model"], category=row["category"],
                daily_fine=int(row["daily_fine"]),
            ))
    return items


def load_loans(path: str | Path) -> list[Loan]:
    if not Path(path).exists():
        return []
    loans: list[Loan] = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            loans.append(Loan(
                loan_id=row["loanId"], tag=row["tag"], member_id=row["member"],
                days=int(row["days"]), rate=int(row["rate"]),
            ))
    return loans


def save_loans(path: str | Path, loans: list[Loan]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=LOAN_FIELDS)
        writer.writeheader()
        for loan in loans:
            writer.writerow({
                "loanId": loan.loan_id, "tag": loan.tag, "member": loan.member_id,
                "days": loan.days, "rate": loan.rate,
            })
