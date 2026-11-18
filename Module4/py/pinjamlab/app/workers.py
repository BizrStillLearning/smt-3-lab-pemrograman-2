"""app layer: the ONLY code that touches a background thread. A worker
touches no widget, ever -- it only ever calls q.put(...). Module 4's whole
threading lesson lives in this one file's discipline.
"""
from __future__ import annotations

import queue
import threading
from pathlib import Path

from ..io.csv_store import load_loans


class ImportWorker:
    """Runs load_loans() off the UI thread and posts the result to a queue.

    daemon=True: the worker must not keep the process alive after the window
    closes. No lock anywhere: queue.Queue is already thread-safe, and the two
    threads share nothing else -- the safest concurrent design is the one
    with no shared mutable state to protect.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = path
        self.queue: queue.Queue = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        """Runs OFF the UI thread. Touches no widget, ever."""
        try:
            rows = load_loans(self.path)
            self.queue.put(("done", rows))
        except Exception as e:  # never let a worker die silently
            self.queue.put(("error", str(e)))
