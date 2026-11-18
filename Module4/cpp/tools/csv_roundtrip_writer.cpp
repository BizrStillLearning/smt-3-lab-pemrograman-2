// Writes the SAME four pathological rows the Python side generates, using
// ONLY the from-scratch writer -- proves writeCsvField is the exact inverse
// of parseCsvRecord from the C++ side as well as the Python side.
//
// Build & run (from code/Module4):
//   g++ -std=c++20 -Wall -Wextra -Icpp/include cpp/tools/csv_roundtrip_writer.cpp -o bin/csv_write
//   ./bin/csv_write > out.csv

#include "pinjamlab/io/csv_writer.hpp"

#include <cstdio>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <fcntl.h>
#include <io.h>
#endif

int main() {
#if defined(_WIN32)
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    using pinjamlab::io::writeCsvRecord;
    const std::vector<std::vector<std::string>> rows = {
        {"loanId", "tag", "member", "note"},
        {"L-001", "LP-001", "M-101", "Budi, Santoso"},
        {"L-002", "PR-014", "M-102", "Ali \"Bob\" Chan"},
        {"L-003", "OS-003", "M-103", "line one\nline two"},
        {"L-004", "MC-007", "M-104", "M\xC3\xBCller"},
    };
    for (const auto& row : rows) {
        const std::string line = writeCsvRecord(row);
        std::fwrite(line.data(), 1, line.size(), stdout);
    }
    return 0;
}
