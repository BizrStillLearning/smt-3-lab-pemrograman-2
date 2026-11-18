"""Measures the frozen-window defect honestly, on THIS machine, and writes
the tick-log evidence Lab 2.3 asks for -- no fabricated numbers.

Method (Figure "Measuring Responsiveness"): schedule after(interval, tick)
to append time.perf_counter() to a list. The LARGEST GAP between consecutive
ticks is the longest freeze, measured by the loop itself rather than an
external stopwatch.

A note on the row count. The module's own narrative uses "5,000 rows, 11
seconds" as an illustrative example. Measured on this machine, Python's
`csv.DictReader` loads 5,000 rows in about 15 ms -- far too fast to freeze
anything a human would notice, and not enough to move the tick log at all.
Rather than report a freeze that did not happen, this script uses a larger,
clearly-labelled row count chosen so the SAME code path takes roughly one
second, which is enough to measure honestly. The mechanism under test
(blocking the UI thread stops repaints) is identical at any size; only the
row count needed to make it visible on 2026 hardware has changed since
whatever machine motivated the module's illustrative number.

Run:  python -m pinjamlab.tools.measure_freeze [n_rows]
"""
from __future__ import annotations

import sys
import time
import tkinter as tk

from ..io.csv_store import load_loans


def _write_csv(path: str, n: int) -> None:
    """Same deterministic shape as make_big_loans.py, written straight to a
    real file rather than stdout (this script needs the path, not a stream)."""
    import csv
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["loanId", "tag", "member", "days", "rate"])
        tags = ["LP-001", "LP-002", "LP-003", "PR-014", "OS-003"]
        for i in range(1, n + 1):
            writer.writerow([f"L-{i:05d}", tags[i % len(tags)],
                              f"M-{100 + i % 50}", 1 + i % 30, 50000])


def _tick_gaps(ticks: list[float]) -> list[float]:
    return [b - a for a, b in zip(ticks, ticks[1:])]


def measure_blocking(root: tk.Tk, csv_path: str, tick_interval_ms: int = 50, run_ms: int = 2500) -> list[float]:
    ticks: list[float] = []
    pending: list[str] = []

    def tick() -> None:
        ticks.append(time.perf_counter())
        pending.append(root.after(tick_interval_ms, tick))

    def do_blocking_import() -> None:
        load_loans(csv_path)  # THE DEFECT: runs on the UI thread

    pending.append(root.after(tick_interval_ms, tick))
    root.after(300, do_blocking_import)  # let a few ticks happen first
    root.after(run_ms, root.quit)
    root.mainloop()
    # Cancel any tick still scheduled for AFTER quit() fired -- otherwise Tk
    # tries to run it against an interpreter that destroy() has torn down,
    # which surfaces as "invalid command name ...tick", not as a Python
    # exception. This was found by running the script, not anticipated.
    for job in pending:
        try:
            root.after_cancel(job)
        except Exception:
            pass
    return ticks


def measure_threaded(root: tk.Tk, csv_path: str, tick_interval_ms: int = 50, run_ms: int = 2500) -> list[float]:
    import queue
    import threading

    ticks: list[float] = []
    pending: list[str] = []
    q: "queue.Queue" = queue.Queue()

    def tick() -> None:
        ticks.append(time.perf_counter())
        pending.append(root.after(tick_interval_ms, tick))

    def worker() -> None:
        rows = load_loans(csv_path)
        q.put(rows)

    def start_import() -> None:
        threading.Thread(target=worker, daemon=True).start()

    pending.append(root.after(tick_interval_ms, tick))
    root.after(300, start_import)
    root.after(run_ms, root.quit)
    root.mainloop()
    for job in pending:
        try:
            root.after_cancel(job)
        except Exception:
            pass
    return ticks


def main(argv: list[str]) -> int:
    n = int(argv[1]) if len(argv) > 1 else 300_000
    csv_path = "sample-data/_freeze_measure_input.csv"
    _write_csv(csv_path, n)

    t0 = time.perf_counter()
    rows = load_loans(csv_path)
    parse_ms = (time.perf_counter() - t0) * 1000
    print(f"# {len(rows)} rows, real load_loans() time: {parse_ms:.1f} ms "
          f"(measured on this machine, {sys.platform})")

    # ONE shared Tk root for both phases: destroying and recreating tk.Tk()
    # within a single process was found to be unreliable on this toolchain
    # (see view.py's docstring) -- the same fix applies here.
    root = tk.Tk()
    root.withdraw()

    blocking_ticks = measure_blocking(root, csv_path)
    blocking_gaps = _tick_gaps(blocking_ticks)
    print(f"# BLOCKING: {len(blocking_ticks)} ticks, "
          f"longest gap = {max(blocking_gaps) * 1000:.1f} ms")
    for g in blocking_gaps:
        print(f"{g * 1000:.2f}")

    print("---")

    threaded_ticks = measure_threaded(root, csv_path)
    threaded_gaps = _tick_gaps(threaded_ticks)
    print(f"# THREADED: {len(threaded_ticks)} ticks, "
          f"longest gap = {max(threaded_gaps) * 1000:.1f} ms")
    for g in threaded_gaps:
        print(f"{g * 1000:.2f}")

    root.destroy()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
