"""CatalogService: search/browse (Module 2) and borrow (Module 3), unified
behind a Result-returning API so the view (app/) never needs a try/except of
its own -- Module 4's own case study gives this class exactly this shape:
`borrow(tag, id, days) -> Result<Loan>`.

Internally still raises the typed LoanError hierarchy (so the guard order and
messages are identical to Module 3); this class is the ONE place that catches
them and converts to a Result, once, for every caller above it.
"""
from __future__ import annotations

from ..domain.equipment import Equipment
from ..domain.loan import Loan
from ..domain.loan_error import (
    EquipmentUnavailable,
    InvalidLoanDuration,
    LoanError,
    QuotaExceeded,
    UnknownAssetTag,
    UnknownMember,
)
from ..domain.member import Member
from ..domain.result import Result

MAX_LOAN_DAYS = 90


class CatalogService:
    def __init__(self) -> None:
        self._catalog: dict[str, Equipment] = {}
        self._roster: dict[str, Member] = {}
        self._loans: list[Loan] = []
        self._next_loan_seq = 1

    def add_equipment(self, equipment: Equipment) -> None:
        self._catalog[equipment.tag] = equipment

    def add_member(self, member: Member) -> None:
        self._roster[member.member_id] = member

    def find_equipment(self, tag: str) -> Equipment | None:
        return self._catalog.get(tag)

    def find_member(self, member_id: str) -> Member | None:
        return self._roster.get(member_id)

    def search(self, query: str) -> list[Equipment]:
        """Case-insensitive substring match over tag and model (Module 2)."""
        q = query.lower()
        return [e for e in self._catalog.values()
                if q in e.tag.lower() or q in e.model.lower()]

    def by_category(self, category: str) -> list[Equipment]:
        return [e for e in self._catalog.values() if getattr(e, "category", None) == category]

    def all_loans(self) -> list[Loan]:
        return list(self._loans)

    def _borrow_or_raise(self, tag: str, member_id: str, days: int) -> Loan:
        equipment = self._catalog.get(tag)
        if equipment is None:
            raise UnknownAssetTag(tag)

        member = self._roster.get(member_id)
        if member is None:
            raise UnknownMember(member_id)

        if days > MAX_LOAN_DAYS:
            raise InvalidLoanDuration(days, MAX_LOAN_DAYS)

        if not equipment.is_available():
            raise EquipmentUnavailable(tag)
        if not member.can_borrow():
            raise QuotaExceeded(member.active_loans, member.max_loans)

        member.record_loan()
        equipment.mark_loaned()

        loan = Loan(f"L-{self._next_loan_seq:03d}", tag, member_id, days, equipment.daily_fine)
        self._next_loan_seq += 1
        self._loans.append(loan)
        return loan

    def borrow(self, tag: str, member_id: str, days: int) -> Result[Loan]:
        """The one public entry point: a Result, never an exception."""
        try:
            loan = self._borrow_or_raise(tag, member_id, days)
            return Result.success(loan)
        except LoanError as e:
            return Result.failure(str(e))

    def return_item(self, tag: str, member_id: str) -> None:
        equipment = self._catalog.get(tag)
        member = self._roster.get(member_id)
        if equipment is not None:
            equipment.mark_returned()
        if member is not None:
            member.record_return()
