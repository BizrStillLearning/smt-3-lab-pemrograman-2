#ifndef PINJAMLAB_APP_RUNNER_HPP
#define PINJAMLAB_APP_RUNNER_HPP

// app layer: the top-level handler. This is the ONE place in the codebase
// allowed to catch `const LoanError&` and turn it into a message a human
// reads, and the ONE place that decides the process exit code. It contains
// no business rules of its own.

#include "pinjamlab/domain/loan_error.hpp"
#include "pinjamlab/io/csv_reader.hpp"
#include "pinjamlab/io/report_writer.hpp"
#include "pinjamlab/io/validator.hpp"
#include "pinjamlab/service/loan_service.hpp"

#include <string>
#include <vector>

namespace pinjamlab {

struct RunResult {
    std::vector<std::string> rejectedLines;  // exactly what expected-output.txt holds
    int total = 0;
    int created = 0;
    int rejected = 0;
    [[nodiscard]] int exitCode() const noexcept { return rejected == 0 ? 0 : 1; }
};

// Pure of console I/O on purpose: returns the lines instead of printing them,
// so both the CLI (main.cpp) and the tests (test_app.cpp) can drive the same
// code path -- one prints to stderr, the other diffs against a golden file.
[[nodiscard]] inline RunResult runCatalogue(LoanService& svc, const std::string& csvPath) {
    CsvReader reader;
    Validator validator;
    RunResult result;

    const auto rows = reader.read(csvPath);
    result.total = static_cast<int>(rows.size());

    for (std::size_t i = 0; i < rows.size(); ++i) {
        const auto& row = rows[i];

        const auto validated = validator.validate(row);

        if (!validated.ok()) {
            ++result.rejected;
            result.rejectedLines.push_back("row " + std::to_string(i + 1) + ": " + validated.error());
            continue;
        }

        const auto& req = validated.value();
        try {
            svc.borrow(req.tag, req.memberId, req.days);
            ++result.created;
        } catch (const pinjamlab::domain::LoanError& e) {
            ++result.rejected;
            result.rejectedLines.push_back("row " + std::to_string(i + 1) + ": " + e.what());
        }
    }
    return result;
}

}  // namespace pinjamlab

#endif  // PINJAMLAB_APP_RUNNER_HPP