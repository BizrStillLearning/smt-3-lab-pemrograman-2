"""Pure domain module: the record produced by a successful borrow().

`rate` is new since Module 3 -- the view's status line
("fine rate Rp 50,000/day") reads it directly, so the service copies the
equipment's daily fine onto the Loan at the moment of borrowing rather than
making the view look the equipment back up.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Loan:
    loan_id: str
    tag: str
    member_id: str
    days: int
    rate: int
