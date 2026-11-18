"""Pure domain module: no console output, no file streams, no GUI toolkit.

Carried forward from Module 3's hierarchy: the same five failure modes.
CatalogService (service/) catches these internally and converts them to a
Result, so the view never needs a try/except of its own.
"""


class LoanError(Exception):
    """Base for every PinjamLab loan failure."""


class UnknownAssetTag(LoanError):
    def __init__(self, tag: str) -> None:
        super().__init__(f"Unknown asset tag: {tag}")
        self.tag = tag


class UnknownMember(LoanError):
    def __init__(self, member_id: str) -> None:
        super().__init__(f"Unknown member: {member_id}")
        self.member_id = member_id


class InvalidLoanDuration(LoanError):
    def __init__(self, days: int, max_days: int) -> None:
        super().__init__(f"Loan duration exceeds maximum: {days} > {max_days}")
        self.days = days
        self.max_days = max_days


class EquipmentUnavailable(LoanError):
    def __init__(self, tag: str) -> None:
        super().__init__(f"Equipment already on loan: {tag}")
        self.tag = tag


class QuotaExceeded(LoanError):
    def __init__(self, active: int, limit: int) -> None:
        super().__init__(f"Loan quota exceeded: {active} active, limit {limit}")
        self.active = active
        self.limit = limit
