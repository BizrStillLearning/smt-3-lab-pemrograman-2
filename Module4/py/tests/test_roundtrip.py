"""write -> read -> compare, for both CSV and JSON. Also the Lab 3.1
round-trip-fidelity claims from Figure "Round-Trips": CSV loses every
non-string type; JSON keeps int/bool/None but not the date."""
from pathlib import Path

from pinjamlab.domain.loan import Loan
from pinjamlab.io.csv_store import LOAN_FIELDS, load_loans, save_loans
from pinjamlab.io.json_store import from_json, load_loans_json, save_loans_json, to_json

SAMPLE = [
    Loan("L-001", "LP-001", "M-101", 7, 50000),
    Loan("L-002", "PR-014", "M-102", 3, 35000),
]


def test_csv_round_trip_preserves_every_loan_field_value(tmp_path: Path):
    path = tmp_path / "loans.csv"
    save_loans(path, SAMPLE)
    back = load_loans(path)
    assert back == SAMPLE


def test_json_round_trip_preserves_every_loan_field_value(tmp_path: Path):
    path = tmp_path / "loans.json"
    save_loans_json(path, SAMPLE)
    back = load_loans_json(path)
    assert back == SAMPLE


def test_csv_loses_the_int_type_at_the_raw_field_level():
    # This is the concrete claim Figure "Round-Trips" makes for CSV: the
    # FORMAT has exactly one type. csv.DictReader hands back strings; only
    # Loan's own __init__ (int(row["days"])) restores the type. Prove the
    # raw field really is a string before that conversion happens.
    import csv
    import io

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=LOAN_FIELDS)
    writer.writeheader()
    writer.writerow({"loanId": "L-001", "tag": "LP-001", "member": "M-101",
                      "days": 7, "rate": 50000})
    buf.seek(0)
    row = next(csv.DictReader(buf))
    assert row["days"] == "7"        # string, not int -- the format's limit
    assert isinstance(row["days"], str)


def test_json_preserves_int_and_would_preserve_bool_and_null_too():
    # JSON keeps more types than CSV, which the module states explicitly:
    # "JSON: four types survive. String, number, boolean and null."
    text = to_json(SAMPLE)
    import json
    data = json.loads(text)
    assert isinstance(data[0]["days"], int)     # not "7" -- a real int

    # A boolean and a null survive JSON round-trip too, generically:
    assert json.loads(json.dumps(True)) is True
    assert json.loads(json.dumps(None)) is None
    # ...but neither survives CSV, where everything becomes a string:
    import csv
    import io
    buf = io.StringIO()
    csv.writer(buf).writerow([True, None])
    buf.seek(0)
    row = next(csv.reader(buf))
    assert row == ["True", ""]  # both became strings (or vanished)


def test_neither_format_has_a_native_date_type():
    # "JSON has no date type either -- so `issued` still returns as a
    # string." Documented here as an executable fact about json itself.
    import json
    from datetime import date
    try:
        json.dumps(date(2026, 3, 1))
        raised = False
    except TypeError:
        raised = True
    assert raised  # json cannot even SERIALISE a date without a converter
