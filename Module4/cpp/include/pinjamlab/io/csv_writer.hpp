#ifndef PINJAMLAB_IO_CSV_WRITER_HPP
#define PINJAMLAB_IO_CSV_WRITER_HPP

// The exact inverse of csv_parser.hpp -- or the round-trip is not lossless.
// From-scratch, no library.

#include <string>
#include <vector>

namespace pinjamlab::io {

// A field needs quoting if it contains a comma, a quote, or a newline
// (either style). Doubling every embedded quote is what makes the result
// parseable again by parseCsvRecord above.
inline std::string writeCsvField(const std::string& f) {
    const bool needsQuotes = f.find_first_of(",\"\n\r") != std::string::npos;
    if (!needsQuotes) return f;

    std::string out = "\"";
    for (char c : f) {
        if (c == '"') out.push_back('"');  // double every quote
        out.push_back(c);
    }
    out.push_back('"');
    return out;
}

inline std::string writeCsvRecord(const std::vector<std::string>& fields) {
    std::string line;
    for (std::size_t i = 0; i < fields.size(); ++i) {
        if (i > 0) line.push_back(',');
        line += writeCsvField(fields[i]);
    }
    line += "\r\n";  // CRLF: the record terminator this parser also accepts
    return line;
}

inline std::string writeCsv(const std::vector<std::vector<std::string>>& records) {
    std::string out;
    for (const auto& r : records) out += writeCsvRecord(r);
    return out;
}

}  // namespace pinjamlab::io

#endif  // PINJAMLAB_IO_CSV_WRITER_HPP
