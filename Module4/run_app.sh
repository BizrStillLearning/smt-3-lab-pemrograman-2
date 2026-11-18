#!/usr/bin/env bash
# Launches the Python desktop app. Requires a display (Windows/macOS/X11).
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PY:-python}"
PYTHONPATH=py "$PY" -m pinjamlab.app.main
