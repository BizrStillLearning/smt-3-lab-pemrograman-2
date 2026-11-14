#pragma once

#include "pinjamlab/service/database.hpp"
#include <iostream>

namespace pinjamlab::service {

    class TxnGuard {
        Database& db_;
        bool committed_{false};

    public:
        explicit TxnGuard(Database& db) : db_(db) {
            db_.begin();
        }

        TxnGuard(const TxnGuard&) = delete;
        TxnGuard& operator=(const TxnGuard&) = delete;

        void commit() {
            db_.commit();
            committed_ = true;
        }

        ~TxnGuard() noexcept {
            if (committed_) return;

            try {
                db_.rollback();
            } catch (...) {
                std::cerr << "Rollback failed during stack unwinding!\n";
            }
        }
    };

} // namespace pinjamlab::service