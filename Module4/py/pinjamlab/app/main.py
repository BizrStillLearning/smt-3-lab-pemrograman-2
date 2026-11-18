"""app layer entry point -- the ONLY file that knows tkinter exists.

Read the CatalogService construction below twice: it is the class from
Module 2/3, imported and constructed with no modification whatsoever. The
dependency rule is what made this possible -- the service never knew about
CSV, so it equally never needs to know about tkinter.
"""
from __future__ import annotations

import sys
import tkinter as tk

from ..io.csv_store import load_catalog
from ..io.paths import data_file
from ..service.catalog_service import CatalogService
from .seed import seed_members
from .view import LoanDeskView


def build_service() -> CatalogService:
    service = CatalogService()
    for item in load_catalog(data_file("sample-catalog.csv")):
        service.add_equipment(item)
    seed_members(service)
    return service


def main() -> int:
    service = build_service()
    root = tk.Tk()
    root.title("PinjamLab - Loan Desk")
    LoanDeskView(root, service)
    root.mainloop()  # control passes to the loop
    return 0  # reached only when the window closes


if __name__ == "__main__":
    sys.exit(main())
