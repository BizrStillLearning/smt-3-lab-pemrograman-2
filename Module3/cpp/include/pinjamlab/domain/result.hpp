#pragma once

#include <string>
#include <utility>
#include <stdexcept>

namespace pinjamlab::domain {

    // Gunakan [[nodiscard]] agar compiler memberi warning jika return value diabaikan pemanggil
    template <typename T>
    class [[nodiscard]] Result {
        bool ok_;
        T value_{};
        std::string error_;

        // Konstruktor privat, hanya bisa dibuat melalui factory method 'success' atau 'failure'
        Result(bool ok, T v, std::string e)
                : ok_(ok), value_(std::move(v)), error_(std::move(e)) {}

        public:
        // Factory Method untuk keberhasilan
        static Result success(T v) {
            return Result(true, std::move(v), "");
        }

        // Factory Method untuk kegagalan
        static Result failure(std::string e) {
            return Result(false, T{}, std::move(e));
        }

        // Akses status
        [[nodiscard]] bool ok() const noexcept { return ok_; }
        [[nodiscard]] const std::string& error() const noexcept { return error_; }

        // Akses nilai dengan pengamanan ketat
        [[nodiscard]] const T& value() const {
            if (!ok_) {
                throw std::logic_error("Attempted to access value() on a failed Result: " + error_);
            }
            return value_;
        }
    };

} // namespace pinjamlab::domain