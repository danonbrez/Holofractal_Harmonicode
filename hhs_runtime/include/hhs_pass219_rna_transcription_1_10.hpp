#ifndef HHS_PASS219_RNA_TRANSCRIPTION_1_10_HPP
#define HHS_PASS219_RNA_TRANSCRIPTION_1_10_HPP

#include "hhs_pass219_rna_transcription_1_10.h"

#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace hhs::pass219 {

class PhaseOperator final {
public:
    explicit constexpr PhaseOperator(HHSExactPhaseBasis basis) noexcept : basis_(basis) {}
    constexpr HHSExactPhaseBasis basis() const noexcept { return basis_; }
private:
    HHSExactPhaseBasis basis_;
};

class OrderedPhaseProduct final {
public:
    OrderedPhaseProduct(PhaseOperator left, PhaseOperator right) noexcept {
        status_ = hhs_exact_pass219_native_phase_witness(
            static_cast<std::uint8_t>(left.basis()),
            static_cast<std::uint8_t>(right.basis()),
            &record_);
    }
    HHSExactStatus status() const noexcept { return status_; }
    const HHSExactPass219NativePhaseWitnessV1& record() const noexcept { return record_; }
private:
    HHSExactPass219NativePhaseWitnessV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

class TrinaryPhaseGate final {
public:
    explicit TrinaryPhaseGate(std::uint8_t trit) noexcept {
        status_ = hhs_exact_pass219_trinary_phase_gate(trit, &record_);
    }
    HHSExactStatus status() const noexcept { return status_; }
    std::uint8_t trit() const noexcept { return record_.trit; }
    HHSExactPass219TrinaryIdentity identity() const noexcept {
        return static_cast<HHSExactPass219TrinaryIdentity>(record_.identity);
    }
    const HHSExactPass219TrinaryPhaseGateV1& record() const noexcept { return record_; }
private:
    HHSExactPass219TrinaryPhaseGateV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

class Hash72TokenView final {
public:
    explicit constexpr Hash72TokenView(
        const HHSExactPass219Hash72TokenOccurrenceV1* record = nullptr) noexcept
        : record_(record) {}
    constexpr bool valid() const noexcept { return record_ != nullptr; }
    constexpr std::uint16_t absolute_position() const noexcept {
        return record_ != nullptr ? record_->absolute_position216 : 0U;
    }
    constexpr std::uint8_t lane_position() const noexcept {
        return record_ != nullptr ? record_->lane_position72 : 0U;
    }
    constexpr std::uint8_t glyph() const noexcept {
        return record_ != nullptr ? record_->glyph : 0U;
    }
    constexpr bool index_present() const noexcept {
        return record_ != nullptr && record_->sha256_index_present == 1U;
    }
private:
    const HHSExactPass219Hash72TokenOccurrenceV1* record_;
};

class Hash216TransitionView final {
public:
    explicit constexpr Hash216TransitionView(
        const HHSExactPass219Hash216TransitionViewV1* record = nullptr) noexcept
        : record_(record) {}
    constexpr bool valid() const noexcept { return record_ != nullptr; }
    constexpr std::size_t size() const noexcept {
        return record_ != nullptr ? HHS_EXACT_PASS219_HASH216_OCCURRENCES : 0U;
    }
    constexpr Hash72TokenView token(std::size_t index) const noexcept {
        return (record_ != nullptr && index < HHS_EXACT_PASS219_HASH216_OCCURRENCES)
            ? Hash72TokenView(&record_->occurrences[index])
            : Hash72TokenView();
    }
    constexpr const char* transition_word() const noexcept {
        return record_ != nullptr ? record_->transition_word216 : nullptr;
    }
private:
    const HHSExactPass219Hash216TransitionViewV1* record_;
};

class Hydration5184View final {
public:
    Hydration5184View(
        std::uint8_t cell81,
        std::int8_t lo_shu_group,
        std::uint8_t operation64,
        std::uint16_t g243) noexcept {
        status_ = hhs_exact_pass219_coordinate_from_pass189(
            cell81, lo_shu_group, operation64, g243, &record_);
    }
    HHSExactStatus status() const noexcept { return status_; }
    std::uint8_t trit() const noexcept { return record_.trit; }
    std::uint16_t slot() const noexcept { return record_.slot5184; }
    const HHSExactPass219HydrationCoordinateV1& record() const noexcept { return record_; }
private:
    HHSExactPass219HydrationCoordinateV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

class RNAAdmissionView final {
public:
    explicit constexpr RNAAdmissionView(
        const HHSExactPass219RNAAdmissionV1* record = nullptr) noexcept
        : record_(record) {}
    constexpr bool valid() const noexcept { return record_ != nullptr; }
    constexpr Hash216TransitionView transition() const noexcept {
        return record_ != nullptr ? Hash216TransitionView(&record_->transition)
                                  : Hash216TransitionView();
    }
    constexpr const HHSExactPass219RNAAdmissionV1* get() const noexcept { return record_; }
private:
    const HHSExactPass219RNAAdmissionV1* record_;
};

static_assert(std::is_standard_layout_v<HHSExactPass219NativePhaseWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219TrinaryPhaseGateV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219Hash72TokenOccurrenceV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219Hash216TransitionViewV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219HydrationCoordinateV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219RNAAdmissionV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAAdmissionV1>);

}  // namespace hhs::pass219

#endif
