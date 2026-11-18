"""app layer: the ONLY module that imports tkinter. The view holds the
service and contains no business rule -- its entire job is converting widget
state into a service call and the answer back into pixels.

LoanDeskView is a ttk.Frame, deliberately NOT a tk.Tk subclass. Making the
window itself a Frame that is PLACED INTO a root (main.py creates the root;
tests share one root fixture across the whole session) means the tests never
construct more than one Tcl interpreter. Constructing and destroying tk.Tk()
repeatedly in one process is fragile on this toolchain -- it was the ORIGINAL
design here, and it failed intermittently after the fourth or fifth Tk() in a
single pytest run with a Tcl "couldn't read init.tcl" error. That failure is
itself worth knowing: it is what "only the thread that created the widgets"
generalises to at the process level -- a GUI toolkit's root object is not
meant to be thrown away and rebuilt on a whim.
"""
from __future__ import annotations

import queue
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..service.catalog_service import CatalogService
from .workers import ImportWorker

STATE_IDLE = "IDLE"
STATE_WORKING = "WORKING"
STATE_ERROR = "ERROR"
STATE_DONE = "DONE"


class LoanDeskView(ttk.Frame):
    def __init__(self, master: tk.Misc, service: CatalogService) -> None:
        super().__init__(master, padding=0)
        self._service = service
        self._state = STATE_IDLE
        self._import_worker = None
        self.tick_log: list[float] = []

        self.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        form = ttk.Frame(self, padding=8)
        form.grid(row=0, column=0, sticky="ew")

        self._member = tk.StringVar()
        self._tag = tk.StringVar()
        self._days = tk.StringVar(value="7")

        rows = [("Member ID", self._member), ("Asset tag", self._tag), ("Days", self._days)]
        for r, pair in enumerate(rows):
            label, var = pair
            ttk.Label(form, text=label).grid(row=r, column=0, sticky="w", pady=2)
            ttk.Entry(form, textvariable=var).grid(row=r, column=1, pady=2)

        ttk.Button(form, text="Borrow", command=self._on_borrow) \
            .grid(row=0, column=2, rowspan=3, padx=8, sticky="ns")
        ttk.Button(form, text="Import", command=self._on_import) \
            .grid(row=3, column=0, columnspan=2, pady=(6, 0), sticky="w")

        filter_row = ttk.Frame(self, padding=(8, 0))
        filter_row.grid(row=1, column=0, sticky="ew")
        ttk.Label(filter_row, text="Filter").grid(row=0, column=0, sticky="w")
        self._filter = tk.StringVar()
        self._filter.trace_add("write", self._on_filter_trace)
        ttk.Entry(filter_row, textvariable=self._filter).grid(row=0, column=1, sticky="ew")
        filter_row.columnconfigure(1, weight=1)

        self._status = ttk.Label(self, text="", padding=6)
        self._status.grid(row=2, column=0, sticky="ew")

        self._table = ttk.Treeview(self, columns=("tag", "member", "days"),
                                    show="headings", height=8)
        for col, label in (("tag", "Tag"), ("member", "Member"), ("days", "Days")):
            self._table.heading(col, text=label)
        self._table.grid(row=3, column=0, sticky="nsew")
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)

        self._catalog_box = tk.Listbox(self, height=6)
        self._catalog_box.grid(row=4, column=0, sticky="nsew")
        self.rowconfigure(4, weight=1)
        self._refresh_catalog_list()

    @property
    def state(self) -> str:
        return self._state

    def _set_state(self, state: str) -> None:
        self._state = state

    def _on_borrow(self) -> None:
        try:
            days = int(self._days.get())
        except ValueError:
            self._show_error("Days must be a whole number")
            return

        result = self._service.borrow(self._tag.get(), self._member.get(), days)

        if result.ok:
            loan = result.value
            self._table.insert("", "end", values=(loan.tag, loan.member_id, loan.days))
            self._show_ok("Loan " + loan.loan_id + " recorded - fine rate Rp "
                           + format(loan.rate, ",") + "/day")
        else:
            self._show_error(result.error)

    def _on_filter_trace(self, *_args) -> None:
        self._on_filter_changed()

    def _on_filter_changed(self) -> None:
        self._refresh_catalog_list()

    def _refresh_catalog_list(self) -> None:
        query = self._filter.get()
        if query:
            items = self._service.search(query)
        else:
            items = list(self._service._catalog.values())
        self._catalog_box.delete(0, tk.END)
        for item in items:
            self._catalog_box.insert(tk.END, item.tag + "  " + item.model)

    def _on_import(self) -> None:
        path = self._ask_import_path()
        if not path:
            return
        self._set_state(STATE_WORKING)
        self._import_worker = ImportWorker(path)
        self._import_worker.start()
        self.after(100, self._poll_import)

    def _ask_import_path(self):
        from tkinter import filedialog
        return filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])

    def _poll_import(self) -> None:
        assert self._import_worker is not None
        try:
            kind, payload = self._import_worker.queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_import)
            return

        if kind == "done":
            for loan in payload:
                self._table.insert("", "end", values=(loan.tag, loan.member_id, loan.days))
            self._show_ok("Imported " + str(len(payload)) + " rows")
        else:
            self._show_error(payload)
        self._set_state(STATE_IDLE)

    def _show_ok(self, msg: str) -> None:
        self._set_state(STATE_DONE)
        self._status.configure(text=msg, foreground="green")

    def _show_error(self, msg: str) -> None:
        self._set_state(STATE_ERROR)
        self._status.configure(text=msg, foreground="red")

    def start_tick_log(self, interval_ms=50) -> None:
        import time
        self.tick_log.append(time.perf_counter())
        self.after(interval_ms, lambda: self.start_tick_log(interval_ms))
