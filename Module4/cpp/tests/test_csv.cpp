// From-scratch CSV parser: quoting, doubled quotes, embedded commas, embedded
// newlines, CRLF, and UTF-8 -- the exact edge cases pathological.csv exists
// to exercise, tested here at the unit level before the round-trip proof.

#include "mini_catch.hpp"
#include "pinjamlab/io/csv_parser.hpp"
#include "pinjamlab/io/csv_writer.hpp"

using namespace pinjamlab::io;

TEST_CASE("Plain fields, no quoting needed") {
    std::size_t pos = 0;
    auto fields = parseCsvRecord("LP-001,M-101,7\n", pos);
    REQUIRE(fields.size() == 3);
    REQUIRE(fields[0] == "LP-001");
    REQUIRE(fields[1] == "M-101");
    REQUIRE(fields[2] == "7");
}

TEST_CASE("A quoted field may contain a comma") {
    std::size_t pos = 0;
    auto fields = parseCsvRecord("L-001,LP-001,M-101,\"Budi, Santoso\"\n", pos);
    REQUIRE(fields.size() == 4);
    REQUIRE(fields[3] == "Budi, Santoso");
}

TEST_CASE("A doubled quote inside a quoted field is one literal quote") {
    std::size_t pos = 0;
    auto fields = parseCsvRecord("L-002,PR-014,M-102,\"Ali \"\"Bob\"\" Chan\"\n", pos);
    REQUIRE(fields.size() == 4);
    REQUIRE(fields[3] == "Ali \"Bob\" Chan");
}

TEST_CASE("A quoted field may contain an embedded newline") {
    std::size_t pos = 0;
    auto fields = parseCsvRecord("L-003,OS-003,M-103,\"line one\nline two\"\n", pos);
    REQUIRE(fields.size() == 4);
    REQUIRE(fields[3] == "line one\nline two");
}

TEST_CASE("CRLF line endings are tolerated, not treated as data") {
    std::size_t pos = 0;
    auto fields = parseCsvRecord("LP-001,M-101,7\r\n", pos);
    REQUIRE(fields.size() == 3);
    REQUIRE(fields[2] == "7");  // no trailing \r leaked into the field
}

TEST_CASE("Multi-byte UTF-8 characters pass through as opaque bytes") {
    std::size_t pos = 0;
    // "Müller" in UTF-8: M, C3 BC (u-umlaut), l, l, e, r -- 7 bytes, 6 chars.
    const std::string record = "L-004,MC-007,M-104,M\xC3\xBCller\n";
    auto fields = parseCsvRecord(record, pos);
    REQUIRE(fields[3] == "M\xC3\xBCller");
    REQUIRE(fields[3].size() == 7);  // bytes, not characters -- the module's point
}

TEST_CASE("A naive split(',') would be wrong on every one of the above") {
    // Documents WHY the state machine exists, as an executable claim: a
    // plain comma-split breaks on the very first pathological row.
    const std::string raw = "\"Budi, Santoso\"";
    std::size_t commaPos = raw.find(',');
    REQUIRE(commaPos != std::string::npos);  // split(",") WOULD cut here...
    std::size_t pos = 0;
    auto fields = parseCsvRecord(raw + "\n", pos);
    REQUIRE(fields.size() == 1);             // ...but the real parser does not
    REQUIRE(fields[0] == "Budi, Santoso");
}

TEST_CASE("writeCsvField is the exact inverse of parsing: round-trips") {
    const std::vector<std::string> tricky = {
        "plain", "has,comma", "has\"quote", "has\nnewline", "M\xC3\xBCller",
    };
    for (const auto& original : tricky) {
        const std::string written = writeCsvField(original);
        std::string record = written + "\n";
        std::size_t pos = 0;
        auto fields = parseCsvRecord(record, pos);
        REQUIRE(fields.size() == 1);
        REQUIRE(fields[0] == original);
    }
}

TEST_CASE("parseCsv splits a full pathological-style file into four records") {
    const std::string text =
        "loanId,tag,member,note\r\n"
        "L-001,LP-001,M-101,\"Budi, Santoso\"\r\n"
        "L-002,PR-014,M-102,\"Ali \"\"Bob\"\" Chan\"\r\n"
        "L-003,OS-003,M-103,\"line one\nline two\"\r\n"
        "L-004,MC-007,M-104,M\xC3\xBCller\r\n";
    auto records = parseCsv(text);
    REQUIRE(records.size() == 5);  // header + 4 data rows
    REQUIRE(records[1][3] == "Budi, Santoso");
    REQUIRE(records[2][3] == "Ali \"Bob\" Chan");
    REQUIRE(records[3][3] == "line one\nline two");
    REQUIRE(records[4][3] == "M\xC3\xBCller");
}

int main() { return test_runner::runAll(); }
