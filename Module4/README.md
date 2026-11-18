# PinjamLab Module 4 — GUI / Event-Driven & File I/O

Part of **Laboratorium Pemrograman II** (`25MP7716G014`), S1 Informatika,
Universitas Muhammadiyah Surabaya. Extends the same repository as Modules 1–3.

## Unit verification table

| Unit / test file | Language | Concept verified | Outcome |
|---|---|---|---|
| `cpp/tests/test_csv.cpp` | C++20 | Quoting, doubled quotes, embedded commas/newlines, CRLF, UTF-8 pass-through, writer-is-inverse-of-parser | **9 passed** |
| `py/tests/test_view_logic.py` | Python 3.12 | Quota rejection at the service layer; handlers called directly with no window; the import-worker queue hand-off | **6 passed** |
| `py/tests/test_roundtrip.py` | Python 3.12 | CSV/JSON round-trip on `Loan`; CSV's one-type limit and JSON's four types, demonstrated, not asserted from the module text | **5 passed** |
| `py/tests/test_purity.py` | Python 3.12 | `tkinter` appears only under `app/` | **1 passed** |

**9 C++ test cases + 12 Python tests.** Plus two cross-language proofs that
are not unit tests: the round-trip dump (below) and the freeze measurement
(`figures/m4_freeze_{before,after}.txt`).

## One command

```bash
./run_tests.sh    # build, C++ tests, CSV round-trip (x2), purity check, pytest
./run_app.sh      # launches the real tkinter desktop app
```

Like Modules 2–3, `run_tests.sh` fails (non-zero exit) on any missing
toolchain or failed step.

## The cross-language CSV round-trip — the acceptance criterion for Lab 2.2

```
$ ./bin/csv_dump sample-data/pathological.csv > out_cpp.txt
$ python -m pinjamlab.tools.csv_dump sample-data/pathological.csv > out_py.txt
$ diff out_cpp.txt out_py.txt && echo "ROUND-TRIP MATCH"
ROUND-TRIP MATCH
```

`sample-data/pathological.csv` is the four rows chosen to break a naive
parser: an embedded comma, a doubled quote, an embedded newline, and a
multi-byte UTF-8 character (`Müller`). `run_tests.sh` runs this proof twice —
once against the fixed file, once against `sample-data/my-loans.csv`.

**A real bug this caught while authoring:** the first version of
`cpp/tools/csv_dump.cpp` wrote `\n` to `stdout` in Windows text mode, which
the C runtime silently rewrites to `\r\n` — so the C++ dump carried an extra
`\r` on every line that Python's dump (written through `sys.stdout.buffer`,
already binary) did not. The fix is `_setmode(_fileno(stdout), _O_BINARY)`
before writing anything, and it is the whole reason that call is in the file
with a comment. This is a textbook instance of the module's own warning: an
encoding-adjacent translation you did not ask for and will not notice until
you diff two things that should be identical.

## The frozen-window measurement — real numbers, not the module's illustrative ones

The module's own text uses "5,000 rows, 11 seconds" as an illustrative
example. Measured on this machine, `csv.DictReader` loads 5,000 rows in about
**15 ms** — too fast to freeze anything a human would notice, and not enough
to move a 50 ms tick log at all. Rather than report a freeze that did not
happen, `py/pinjamlab/tools/measure_freeze.py` uses 300,000 rows (clearly
labelled, and easy to change) so the *same* code path takes about a second on
real hardware — enough to measure honestly. The mechanism under test is
identical at any size; only the row count needed to see it on 2026 hardware
has changed.

| | longest gap between ticks |
|---|---:|
| **Before** — import on the UI thread | **1002.1 ms** |
| **After** — import on a worker thread + queue | **100.3 ms** |

Full tick logs: `figures/m4_freeze_before.txt`, `figures/m4_freeze_after.txt`.
The "after" number is not zero — it is the normal 50–65 ms scheduling jitter
of `after()` itself, which is the honest floor: threading does not make the
work free, it only stops it from blocking repaints.

## Screenshots

`figures/m4_screen_idle.png` and `figures/m4_screen_error.png` are real
screenshots of the actual running application (captured via a PowerShell
`CopyFromScreen`, not mocked up) — a successful borrow with two loans in the
table and the live filter applied, and the exact error text
`Unknown asset tag: LP-999` rendered by `_show_error`.

## A real fix made during authoring: one `tk.Tk()` per process, not per test

`LoanDeskView` is a `ttk.Frame`, **not** a `tk.Tk` subclass, and every test
shares one session-scoped Tk root (`py/tests/conftest.py`). The first version
subclassed `tk.Tk` directly; running the test suite intermittently crashed
after the fourth or fifth `tk.Tk()` constructed in one process with
`Tcl_AsyncDelete: async handler deleted by the wrong thread` / a missing
`init.tcl`. That is a real defect in repeatedly tearing down and rebuilding a
GUI toolkit's root interpreter, not a flaky test — the fix (one root, many
Frames) is now the pattern both the app and its tests use, and three
consecutive full test runs confirmed it.

## Directory structure

```
Module4/
├── run_tests.sh                 # C++, round-trip x2, tkinter purity, pytest
├── run_app.sh                   # launches the real desktop app
├── cpp/
│   ├── include/pinjamlab/io/    # csv_parser.hpp, csv_writer.hpp, paths.hpp
│   ├── tools/                   # csv_dump.cpp, csv_roundtrip_writer.cpp
│   └── tests/test_csv.cpp
├── py/pinjamlab/
│   ├── domain/, service/        # unchanged in SHAPE since Module 3, self-contained here
│   ├── io/                      # csv_store.py, json_store.py, paths.py
│   ├── app/                     # THE ONLY PLACE tkinter appears
│   │   ├── view.py              # LoanDeskView (ttk.Frame) + the Lab 2 filter feature
│   │   ├── workers.py           # ImportWorker: thread + queue, touches no widget
│   │   ├── seed.py, main.py
│   └── tools/                   # csv_dump.py, make_pathological.py, measure_freeze.py
├── py/tests/
│   └── conftest.py              # the shared Tk root fixture
├── figures/                     # real screenshots + real tick logs
└── sample-data/
    ├── sample-catalog.csv       # fixed, from Module 2
    ├── pathological.csv         # fixed: the four parser-breaking rows
    └── my-loans.csv             # bring-your-own-input, 16 rows
```

`loans.csv` (written by the app at runtime) is deliberately absent from the
committed tree — it is an output, not an input, and Module 5 makes
"nothing rebuildable is committed" an explicit rule.

## Verified

- **Environment:** Windows 11 · g++ (GCC) 15.2.0 · Python 3.12.13 · pytest 8.3.4 · Tcl/Tk 8.6.12
- **Date:** 2026-09-15
- **Result:** `./run_tests.sh` exits 0; the real app was driven programmatically
  (form filled, Borrow clicked, filter applied) and screenshotted; the freeze
  was reproduced and fixed with measured, not narrated, numbers.
