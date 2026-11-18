"""A GUI is hard to test. The logic behind it is not -- if they are separate.

Every test here calls a handler DIRECTLY, without clicking anything and
without running mainloop(). That is only possible because a handler is an
ordinary method that takes no event object and does no layout -- Module 4's
whole "testability is a consequence of the split" argument, made executable.

All tests share ONE Tk root (see conftest.py's tk_root fixture) and get a
fresh child Frame each -- see that file for why.
"""
from pathlib import Path

from pinjamlab.domain.equipment import Equipment
from pinjamlab.domain.member import Member, Role
from pinjamlab.io.csv_store import save_loans
from pinjamlab.service.catalog_service import CatalogService
from pinjamlab.app.view import STATE_DONE, STATE_ERROR, LoanDeskView


def sample_service() -> CatalogService:
    svc = CatalogService()
    svc.add_equipment(Equipment("LP-001", "ThinkPad T14", "Computing", 50000))
    svc.add_equipment(Equipment("LP-002", "Latitude 5440", "Computing", 50000))
    svc.add_equipment(Equipment("LP-003", "ProBook 450", "Computing", 50000))
    svc.add_member(Member("M-101", "Ayu Lestari", Role.STUDENT))
    return svc


def test_service_borrow_rejects_over_quota_member():
    # The pure-logic half of the module's own worked example, Step 3. Two
    # DIFFERENT items bring M-101 (a Student, quota 2) to its limit; a third
    # different item is the one that must be refused for QUOTA, not for
    # availability.
    service = sample_service()
    assert service.borrow("LP-001", "M-101", 7).ok
    assert service.borrow("LP-002", "M-101", 7).ok
    result = service.borrow("LP-003", "M-101", 7)  # third loan: over quota
    assert not result.ok
    assert "quota" in result.error.lower()


def test_view_on_borrow_updates_status_and_table_on_success(view_container):
    view = LoanDeskView(view_container, sample_service())
    view._tag.set("LP-001")
    view._member.set("M-101")
    view._days.set("7")
    view._on_borrow()  # call the handler directly -- no click, no loop
    assert "Loan L-001 recorded" in view._status.cget("text")
    assert len(view._table.get_children()) == 1
    assert view.state == STATE_DONE


def test_view_shows_service_error_verbatim(view_container):
    view = LoanDeskView(view_container, sample_service())
    view._tag.set("LP-999")  # unknown tag
    view._member.set("M-101")
    view._days.set("7")
    view._on_borrow()
    assert view._status.cget("text") == "Unknown asset tag: LP-999"
    assert view.state == STATE_ERROR


def test_view_rejects_non_numeric_days_without_calling_the_service(view_container):
    view = LoanDeskView(view_container, sample_service())
    view._tag.set("LP-001")
    view._member.set("M-101")
    view._days.set("not-a-number")
    view._on_borrow()
    assert view._status.cget("text") == "Days must be a whole number"
    assert len(view._table.get_children()) == 0  # service was never called


def test_view_filter_renders_search_results_with_no_business_rule(view_container):
    view = LoanDeskView(view_container, sample_service())
    view._filter.set("Latitude")
    assert view._catalog_box.size() == 1
    assert "LP-002" in view._catalog_box.get(0)


def test_import_worker_populates_the_table_through_the_queue(view_container, tmp_path: Path):
    # Exercises the queue hand-off end to end WITHOUT a real background
    # thread or a file dialog: _poll_import only cares that the queue has
    # something in it, which is exactly what makes it testable.
    loans_path = tmp_path / "loans.csv"
    from pinjamlab.domain.loan import Loan
    save_loans(loans_path, [Loan("L-100", "LP-001", "M-101", 7, 50000)])

    view = LoanDeskView(view_container, sample_service())
    from pinjamlab.app.workers import ImportWorker
    worker = ImportWorker(loans_path)
    worker.start()
    worker._thread.join(timeout=2)  # deterministic for the test only
    view._import_worker = worker
    view._poll_import()
    assert len(view._table.get_children()) == 1
    assert "Imported 1 rows" in view._status.cget("text")
