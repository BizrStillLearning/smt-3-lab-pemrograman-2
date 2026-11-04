#pragma once
#include <cstddef>
#include <utility>

namespace pinjamlab {

    template <typename T>
    class LinkedList {
    private:
        struct Node {
            T value;
            Node* next{nullptr};
            explicit Node(T v) : value(std::move(v)) {}
        };

        Node* head_{nullptr};
        std::size_t size_{0};

    public:
        LinkedList() = default;

        // Rule of Five: Hapus fitur copy agar tidak terjadi double-free
        LinkedList(const LinkedList&) = delete;
        LinkedList& operator=(const LinkedList&) = delete;

        // Destruktor ini WAJIB ada untuk mencegah O(n) memory leak
        ~LinkedList() {
            while (head_) {
                Node* next = head_->next;
                delete head_;
                head_ = next;
            }
        }

        void pushFront(T value) { // Kompleksitas: O(1)
            Node* node = new Node(std::move(value));
            node->next = head_;
            head_ = node;
            ++size_;
        }

        [[nodiscard]] bool contains(const T& value) const { // Kompleksitas: O(n)
            for (Node* cur = head_; cur; cur = cur->next) {
                if (cur->value == value) return true;
            }
            return false;
        }

        bool remove(const T& value) { // Kompleksitas: O(n) scan, O(1) pemutusan
            Node* prev = nullptr;
            for (Node* cur = head_; cur; prev = cur, cur = cur->next) {
                if (!(cur->value == value)) continue;

                // 1. Sambung ulang melewati node yang akan dihapus
                if (prev) prev->next = cur->next;
                else head_ = cur->next;

                // 2. BARU hapus memori (mencegah use-after-free)
                delete cur;
                --size_;
                return true;
            }
            return false;
        }

        [[nodiscard]] std::size_t size() const noexcept { return size_; }
    };

} // namespace pinjamlab