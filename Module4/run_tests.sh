#!/usr/bin/env bash
# ==============================================================================
# PinjamLab Module 4: one command -- build, C++ tests, the cross-language CSV
# round-trip, Python tests (incl. the tkinter-only-in-app/ purity check).
#
# Fails (non-zero exit) on any missing toolchain or failed step, like
# Modules 2-3 and unlike Module 1's original script.
# ==============================================================================
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p bin

CXX="${CXX:-g++}"
PY="${PY:-python}"
command -v "$CXX" >/dev/null || { echo "FATAL: no C++ compiler ($CXX) on PATH."; exit 2; }
command -v "$PY"  >/dev/null || { echo "FATAL: no Python interpreter ($PY) on PATH."; exit 2; }

echo "================================================================================"
echo " [PinjamLab M4] $("$CXX" --version | head -1)"
echo " [PinjamLab M4] $("$PY" --version 2>&1)"
echo "================================================================================"

echo ""
echo ">>> [1/5] Building C++20 (-Wall -Wextra -Werror)"
"$CXX" -std=c++20 -Wall -Wextra -Werror -Icpp/include -Icpp/tests cpp/tests/test_csv.cpp -o bin/test_csv
"$CXX" -std=c++20 -Wall -Wextra -Werror -Icpp/include cpp/tools/csv_dump.cpp -o bin/csv_dump

echo ""
echo ">>> [2/5] Running C++20 test suite"
./bin/test_csv

echo ""
echo ">>> [3/5] Cross-language round-trip: pathological.csv, C++ vs Python"
./bin/csv_dump sample-data/pathological.csv > bin/out_cpp.txt
PYTHONPATH=py "$PY" -m pinjamlab.tools.csv_dump sample-data/pathological.csv > bin/out_py.txt
diff bin/out_cpp.txt bin/out_py.txt
echo "  match: cpp/tools/csv_dump and Python's csv module agree, byte for byte"

if [ -f sample-data/my-loans.csv ]; then
    echo ""
    echo ">>> [3b/5] Cross-language round-trip: my-loans.csv (bring-your-own-input)"
    ./bin/csv_dump sample-data/my-loans.csv > bin/out_cpp_my.txt
    PYTHONPATH=py "$PY" -m pinjamlab.tools.csv_dump sample-data/my-loans.csv > bin/out_py_my.txt
    diff bin/out_cpp_my.txt bin/out_py_my.txt
    echo "  match: my-loans.csv round-trips identically in both languages"
fi

echo ""
echo ">>> [4/5] tkinter-only-in-app/ purity check"
if grep -rq "tkinter" py/pinjamlab/domain/ py/pinjamlab/service/ py/pinjamlab/io/ 2>/dev/null; then
    echo "FAIL: tkinter must appear only in app/"
    exit 1
fi
echo "  clean: tkinter appears only in py/pinjamlab/app/"

echo ""
echo ">>> [5/5] Running Python 3.12 test suite (pytest)"
PYTHONPATH=py "$PY" -m pytest py/tests -q

echo ""
echo "================================================================================"
echo " [SUCCESS] C++ suite, cross-language round-trip, purity check, and pytest all passed."
echo "================================================================================"
