#ifndef PINJAMLAB_IO_CSV_PARSER_HPP
#define PINJAMLAB_IO_CSV_PARSER_HPP

// From-scratch primitive, no library: the state machine of Module 4's
// Figure "The CSV Parsing State Machine" -- four states (FIELD START,
// IN PLAIN, IN QUOTED, QUOTE SEEN), five transitions. Reads CHARACTERS, not
// lines, because a quoted field may legally contain a newline.

#include <cstddef>
#include <string>
#include <vector>

namespace pinjamlab::io {

// Parses ONE record starting at text[pos] and advances pos past it
// (including the terminating newline, if any). A record may span more than
// one PHYSICAL line if a field is quoted and contains an embedded newline.
inline std::vector<std::string> parseCsvRecord(const std::string& text, std::size_t& pos) {
    std::vector<std::string> fields;
    std::string field;
    bool inQuoted = false;

    while (pos < text.size()) {
        const char c = text[pos];

        if (inQuoted) {
            if (c == '"') {
                if (pos + 1 < text.size() && text[pos + 1] == '"') {
                    field.push_back('"');  // "" inside quotes -> one literal quote
                    pos += 2;
                    continue;
                }
                inQuoted = false;  // closing quote (QUOTE SEEN -> IN PLAIN, implicitly)
                ++pos;
                continue;
            }
            field.push_back(c);  // comma / newline: ORDINARY characters here
            ++pos;
            continue;
        }

        if (c == '"') { inQuoted = true; ++pos; continue; }         // FIELD START -> IN QUOTED
        if (c == ',') { fields.push_back(field); field.clear(); ++pos; continue; }
        if (c == '\r') { ++pos; continue; }                          // tolerate CRLF
        if (c == '\n') { ++pos; break; }                             // end of record
        field.push_back(c);                                          // -> IN PLAIN
        ++pos;
    }
    fields.push_back(field);
    return fields;
}

// Parses every record in a complete CSV text (already read into memory).
inline std::vector<std::vector<std::string>> parseCsv(const std::string& text) {
    std::vector<std::vector<std::string>> records;
    std::size_t pos = 0;
    while (pos < text.size()) {
        records.push_back(parseCsvRecord(text, pos));
    }
    return records;
}

}  // namespace pinjamlab::io

#endif  // PINJAMLAB_IO_CSV_PARSER_HPP
