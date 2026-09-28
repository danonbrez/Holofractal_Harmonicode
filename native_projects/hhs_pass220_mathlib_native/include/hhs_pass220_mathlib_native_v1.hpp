#ifndef HHS_PASS220_MATHLIB_NATIVE_V1_HPP
#define HHS_PASS220_MATHLIB_NATIVE_V1_HPP

#include "hhs_pass220_python_native_execution_v1.h"
#include "hhs_pass220_python_rna_class_registration_2_0.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <string_view>

namespace hhs::mathlib {

class NativeInt final {
public:
    NativeInt() noexcept { assign_literal("0"); }

    explicit NativeInt(std::string_view literal) noexcept {
        assign_literal(literal);
    }

    bool valid() const noexcept {
        return status_ == HHS_PYTHON_NATIVE_OK;
    }

    HHSPythonNativeStatusV1 status() const noexcept {
        return status_;
    }

    const char* decimal() const noexcept {
        return decimal_.data();
    }

    std::uint32_t statement_count() const noexcept {
        return statement_count_;
    }

    static NativeInt add(const NativeInt& lhs, const NativeInt& rhs) noexcept {
        return binary(lhs, rhs, '+');
    }

    static NativeInt sub(const NativeInt& lhs, const NativeInt& rhs) noexcept {
        return binary(lhs, rhs, '-');
    }

    static NativeInt mul(const NativeInt& lhs, const NativeInt& rhs) noexcept {
        return binary(lhs, rhs, '*');
    }

    static constexpr bool host_python_evaluator_used() noexcept {
        return false;
    }

private:
    struct RawTag {};

    explicit NativeInt(RawTag) noexcept = default;

    void assign_literal(std::string_view literal) noexcept {
        std::array<char, HHS_PYTHON_NATIVE_MAX_SOURCE_BYTES + 1U> source{};
        const int written = std::snprintf(
            source.data(),
            source.size(),
            "result=%.*s",
            static_cast<int>(literal.size()),
            literal.data());
        if (written < 0 || static_cast<std::size_t>(written) >= source.size()) {
            status_ = HHS_PYTHON_NATIVE_ERR_SOURCE_TOO_LARGE;
            return;
        }
        execute(source.data());
    }

    void execute(const char* source) noexcept {
        std::array<char, 512U> error{};
        std::size_t result_length = 0U;
        statement_count_ = 0U;
        status_ = hhs_python_native_execute(
            source,
            decimal_.data(),
            decimal_.size(),
            &result_length,
            error.data(),
            error.size(),
            &statement_count_);
        if (status_ != HHS_PYTHON_NATIVE_OK)
            decimal_[0] = '\0';
    }

    static NativeInt binary(
        const NativeInt& lhs,
        const NativeInt& rhs,
        char op
    ) noexcept {
        NativeInt out{RawTag{}};
        if (!lhs.valid() || !rhs.valid()) {
            out.status_ = HHS_PYTHON_NATIVE_ERR_ARGUMENT;
            return out;
        }

        constexpr std::size_t source_capacity =
            (HHS_PYTHON_NATIVE_MAX_DIGITS * 2U) + 64U;
        std::array<char, source_capacity> source{};
        const int written = std::snprintf(
            source.data(),
            source.size(),
            "result=(%s)%c(%s)",
            lhs.decimal(),
            op,
            rhs.decimal());
        if (written < 0 || static_cast<std::size_t>(written) >= source.size()) {
            out.status_ = HHS_PYTHON_NATIVE_ERR_SOURCE_TOO_LARGE;
            return out;
        }
        out.execute(source.data());
        return out;
    }

    std::array<char, HHS_PYTHON_NATIVE_MAX_DIGITS + 2U> decimal_{};
    HHSPythonNativeStatusV1 status_{HHS_PYTHON_NATIVE_ERR_ARGUMENT};
    std::uint32_t statement_count_{0U};
};

class NativeNat final {
public:
    explicit NativeNat(std::string_view literal) noexcept
        : value_(literal),
          admitted_(value_.valid() && value_.decimal()[0] != '-') {}

    bool valid() const noexcept { return admitted_; }
    const char* decimal() const noexcept { return value_.decimal(); }

    static NativeNat add(const NativeNat& lhs, const NativeNat& rhs) noexcept {
        return NativeNat(NativeInt::add(lhs.value_, rhs.value_));
    }

    static NativeNat mul(const NativeNat& lhs, const NativeNat& rhs) noexcept {
        return NativeNat(NativeInt::mul(lhs.value_, rhs.value_));
    }

private:
    explicit NativeNat(NativeInt value) noexcept
        : value_(value),
          admitted_(value_.valid() && value_.decimal()[0] != '-') {}

    NativeInt value_;
    bool admitted_{false};
};

/* C++ class identity is projected through the existing Python2 RNA cell wall.
 * Registration is proof/type metadata only and cannot commit VM81/Hash72/Hash216.
 */
class NativeClassRegistration final {
public:
    explicit NativeClassRegistration(
        const HHSExactPass220PythonRNAClassDescriptorV1& descriptor
    ) noexcept
        : registration_(descriptor) {}

    HHSExactStatus status() const noexcept {
        return registration_.status();
    }

    const HHSExactPass220PythonRNAClassRegistrationV1& record() const noexcept {
        return registration_.record();
    }

    bool registration_only() const noexcept {
        return registration_.registration_only();
    }

    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool hash72_commit_authority() noexcept { return false; }
    static constexpr bool hash216_persistence_authority() noexcept { return false; }
    static constexpr bool proof_kernel_authority() noexcept { return false; }

private:
    hhs::rna::PythonClassRegistration registration_;
};

}  // namespace hhs::mathlib

#endif
