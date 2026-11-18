"""Lab 2.4: prove tkinter has not leaked out of app/. This is the same check
run_tests.sh runs as a build gate; this test exists so `pytest` alone (e.g.
in an editor) also catches the regression, not only the shell script."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_tkinter_appears_only_in_app():
    hits = []
    for pkg in ("domain", "service", "io"):
        pkg_dir = ROOT / "py" / "pinjamlab" / pkg
        for path in pkg_dir.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if "tkinter" in line:
                    hits.append(f"{path}:{lineno}: {line}")
    assert not hits, "tkinter leaked outside app/: " + "; ".join(hits)
