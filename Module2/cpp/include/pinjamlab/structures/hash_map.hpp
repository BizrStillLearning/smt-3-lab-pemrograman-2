#pragma once
#include <vector>
#include <list>
#include <utility>
#include <optional>
#include <functional>
#include <cstddef>

namespace pinjamlab::structures {

template <typename K, typename V, typename Hash = std::hash<K>>
class HashMap {
private:
    using Entry = std::pair<K, V>;
    using Bucket = std::list<Entry>;

    std::vector<Bucket> buckets_;
    std::size_t size_{0};
    double maxLoad_{1.0};
    Hash hasher_{};

    [[nodiscard]] std::size_t indexFor(const K& key, std::size_t m) const {
        return hasher_(key) % m;
    }

    void rehash(std::size_t newCount) {
        std::vector<Bucket> grown(newCount);
        for (Bucket& b : buckets_) {
            for (Entry& e : b) {
                grown[indexFor(e.first, newCount)].push_back(std::move(e));
            }
        }
        buckets_.swap(grown);
    }

public:
    explicit HashMap(std::size_t initialBuckets = 8)
        : buckets_(initialBuckets == 0 ? 1 : initialBuckets) {}

    void insert(K key, V value) {
        Bucket& b = buckets_[indexFor(key, buckets_.size())];

        for (Entry& e : b) {
            if (e.first == key) {
                e.second = std::move(value);
                return;
            }
        }

        b.emplace_back(std::move(key), std::move(value));
        ++size_;

        if (loadFactor() > maxLoad_) {
            rehash(buckets_.size() * 2);
        }
    }

    [[nodiscard]] std::optional<V> get(const K& key) const {
        const Bucket& b = buckets_[indexFor(key, buckets_.size())];
        for (const Entry& e : b) {
            if (e.first == key) return e.second; // Hanya memindai SATU rantai
        }
        return std::nullopt;
    }

    bool erase(const K& key) {
        Bucket& b = buckets_[indexFor(key, buckets_.size())];
        for (auto it = b.begin(); it != b.end(); ++it) {
            if (it->first == key) {
                b.erase(it);
                --size_;
                return true;
            }
        }
        return false;
    }

    [[nodiscard]] double loadFactor() const {
        return static_cast<double>(size_) / static_cast<double>(buckets_.size());
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t bucketCount() const noexcept { return buckets_.size(); }
};

} // namespace pinjamlab::structures