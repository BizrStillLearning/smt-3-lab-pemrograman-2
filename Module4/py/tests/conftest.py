"""One shared Tk root for the whole test session.

Constructing and destroying tk.Tk() once per test is fragile on this
toolchain: after the fourth or fifth Tk() in a single process, Tcl started
failing to find its own init.tcl -- a real, reproducible defect, not a
flaky test. LoanDeskView is a Frame precisely so tests can share ONE root
(created here, destroyed once at session end) instead of each test building
and tearing down an interpreter.
"""
import tkinter as tk

import pytest


@pytest.fixture(scope="session")
def tk_root():
    root = tk.Tk()
    root.withdraw()  # never actually shown during tests
    yield root
    root.destroy()


@pytest.fixture()
def view_container(tk_root):
    """A fresh child Frame per test, destroyed after -- so widgets from one
    test never leak state into the next, without paying for a new Tk()."""
    container = tk.Frame(tk_root)
    yield container
    container.destroy()
