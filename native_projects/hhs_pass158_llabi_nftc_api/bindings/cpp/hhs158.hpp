#ifndef HHS_PASS158_CPP_HPP
#define HHS_PASS158_CPP_HPP

#include "hhs_pass158_api.h"

#include <cstdint>
#include <stdexcept>
#include <string>
#include <string_view>

namespace hhs158 {

class Error final : public std::runtime_error {
public:
    explicit Error(HHS158Status status)
        : std::runtime_error(std::string(hhs158_status_classification(status)) + " (" + std::to_string(status) + ")"),
          status_(status) {}
    HHS158Status status() const noexcept { return status_; }
private:
    HHS158Status status_;
};

inline void check(HHS158Status status) {
    if (status != HHS158_OK) throw Error(status);
}

inline HHS158ByteSpan span(std::string_view value) noexcept {
    return HHS158ByteSpan{reinterpret_cast<const std::uint8_t *>(value.data()), value.size()};
}

template <typename T>
inline void initialize(T &value) noexcept {
    value = T{};
    value.header.struct_size = static_cast<std::uint32_t>(sizeof(T));
    value.header.struct_version = HHS158_STRUCT_VERSION_1;
}

class Context final {
public:
    explicit Context(std::uint64_t epoch = UINT64_C(1799711799)) {
        HHS158ContextConfig config{};
        initialize(config);
        config.abi_major = HHS158_ABI_VERSION_MAJOR;
        config.abi_minor = HHS158_ABI_VERSION_MINOR;
        config.max_definitions = 64;
        config.max_instances = 128;
        config.max_receipts = 128;
        config.max_memory_bytes = UINT64_C(16777216);
        config.deterministic_epoch_seconds = epoch;
        check(hhs158_context_create(&config, &handle_));
    }
    ~Context() { if (handle_) hhs158_context_release(handle_); }
    Context(const Context &) = delete;
    Context &operator=(const Context &) = delete;
    Context(Context &&other) noexcept : handle_(other.handle_) { other.handle_ = nullptr; }
    Context &operator=(Context &&other) noexcept {
        if (this != &other) {
            if (handle_) hhs158_context_release(handle_);
            handle_ = other.handle_;
            other.handle_ = nullptr;
        }
        return *this;
    }
    HHS158Context *get() const noexcept { return handle_; }
private:
    HHS158Context *handle_ = nullptr;
};

class Receipt final {
public:
    Receipt() = default;
    explicit Receipt(HHS158Receipt *handle) : handle_(handle) {}
    HHS158Receipt *get() const noexcept { return handle_; }
    std::string serialize() const {
        HHS158MutableByteSpan output{};
        HHS158Status status = hhs158_receipt_serialize(handle_, &output);
        if (status != HHS158_BUFFER_TOO_SMALL) check(status);
        std::string value(output.size_written, '\0');
        output.data = reinterpret_cast<std::uint8_t *>(value.data());
        output.capacity = value.size();
        check(hhs158_receipt_serialize(handle_, &output));
        return value;
    }
private:
    HHS158Receipt *handle_ = nullptr;
};

}  // namespace hhs158

#endif
