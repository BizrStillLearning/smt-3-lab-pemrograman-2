#ifndef PINJAMLAB_IO_PATHS_HPP
#define PINJAMLAB_IO_PATHS_HPP

#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>

namespace pinjamlab::io {

// Reads an entire file as bytes (not text): this module's whole point is
// that a file is bytes until an encoding says otherwise, so this helper
// makes no assumption about what is inside.
inline std::string readFileBytes(const std::filesystem::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("cannot open: " + path.string());
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

inline void writeFileBytes(const std::filesystem::path& path, const std::string& bytes) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot open for writing: " + path.string());
    out.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
}

inline bool fileExists(const std::filesystem::path& path) {
    return std::filesystem::exists(path);
}

}  // namespace pinjamlab::io

#endif  // PINJAMLAB_IO_PATHS_HPP
