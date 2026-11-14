"""app layer: the top-level handler. This is the ONE place allowed to catch
`LoanError` and turn it into a message a human reads, and the ONE place that
decides the process exit code.
"""
from __future__ import annotations
from dataclasses import dataclass, field

from ..domain.loan_error import LoanError
from ..io.csv_reader import CsvReader
from ..io.report_writer import ReportWriter
from ..io.validator import Validator
from ..service.loan_service import LoanService

@dataclass
class RunResult:
    rejected_lines: list[str] = field(default_factory=list)
    total: int = 0
    created: int = 0
    rejected: int = 0

    @property
    def exit_code(self) -> int:
        return 0 if self.rejected == 0 else 1

def run_catalogue(svc: LoanService, csv_path: str) -> RunResult:
    reader = CsvReader()
    validator = Validator()
    result = RunResult()

    rows = reader.read(csv_path)
    result.total = len(rows)

    for i, row in enumerate(rows, start=1):
        validated = validator.validate(row)
        if not validated.ok:
            result.rejected += 1
            result.rejected_lines.append(f"row {i}: {validated.error}")
            continue

        req = validated.value

        try:
            svc.borrow(req.tag, req.member_id, req.days)
            result.created += 1
        except LoanError as e:
            result.rejected += 1
            result.rejected_lines.append(f"row {i}: {e}")


    return result