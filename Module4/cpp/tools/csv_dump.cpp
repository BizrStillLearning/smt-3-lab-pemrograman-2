// Prints one field per line -- the match target for the cross-language
// round-trip proof (Module 4, "Step 4"). Reads bytes, parses with the
// from-scratch state machine, and writes each field on its own line so a
// plain `diff` against Python's dump is the entire comparison.

#include "pinjamlab/io/csv_parser.hpp"
#include "pinjamlab/io/paths.hpp"

#include <cstdio>
#include <string>

#if defined(_WIN32)
#include <fcntl.h>
#include <io.h>
#endif

int main(int argc, char** argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: csv_dump <path>\n");
        return 2;
    }

#if defined(_WIN32)
    // Without this, the Windows CRT's text-mode stdout silently rewrites
    // every '\n' written below into "\r\n" -- exactly the kind of hidden,
    // encoding-adjacent translation this module is built to make visible.
    // This line is the whole fix, and it is easy to never notice you need.
    _setmode(_fileno(stdout), _O_BINARY);
#endif

    const std::string bytes = pinjamlab::io::readFileBytes(argv[1]);
    const auto records = pinjamlab::io::parseCsv(bytes);

    for (const auto& record : records) {
        for (const auto& field : record) {
            std::fwrite(field.data(), 1, field.size(), stdout);
            std::fputc('\n', stdout);
        }
    }
    return 0;
}
