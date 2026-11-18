"""io layer: the JSON twin of csv_store's loan persistence -- Lab 3.1's
round-trip comparison is between these two."""
from __future__ import annotations

import json
from pathlib import Path

from ..domain.loan import Loan


def to_json(loans: list[Loan]) -> str:
    return json.dumps([{
        "loanId": l.loan_id, "tag": l.tag, "member": l.member_id,
        "days": l.days, "rate": l.rate,
    } for l in loans], indent=2)


def from_json(text: str) -> list[Loan]:
    data = json.loads(text)
    return [Loan(loan_id=d["loanId"], tag=d["tag"], member_id=d["member"],
                 days=d["days"], rate=d["rate"]) for d in data]


def save_loans_json(path: str | Path, loans: list[Loan]) -> None:
    Path(path).write_text(to_json(loans), encoding="utf-8")


def load_loans_json(path: str | Path) -> list[Loan]:
    if not Path(path).exists():
        return []
    return from_json(Path(path).read_text(encoding="utf-8"))
