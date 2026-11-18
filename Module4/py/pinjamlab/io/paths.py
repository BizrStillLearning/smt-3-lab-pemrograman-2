"""io layer: path helpers. Deliberately trivial -- the module's own point is
that most of the interesting behaviour lives in encoding and newline
handling, not path manipulation."""
from __future__ import annotations

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "sample-data"


def data_file(name: str) -> Path:
    return DATA_DIR / name
