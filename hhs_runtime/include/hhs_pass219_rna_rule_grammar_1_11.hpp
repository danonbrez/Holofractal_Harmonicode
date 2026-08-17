#ifndef HHS_PASS219_RNA_RULE_GRAMMAR_1_11_HPP
#define HHS_PASS219_RNA_RULE_GRAMMAR_1_11_HPP

#include "hhs_pass219_rna_rule_grammar_1_11.h"

#include <cstdint>
#include <type_traits>

namespace hhs::rna {

class Domain final {
public:
    Domain(std::uint32_t id,
           std::uint32_t complement_id,
           HHSExactPhaseBasis basis,
           std::uint8_t orientation,
           std::uint32_t role_flags = 0U) noexcept {
        status_ = hhs_exact_pass219_rna_domain_init(
            id, complement_id, static_cast<std::uint8_t>(basis),
            orientation, role_flags, &record_);
    }
    HHSExactStatus status() const noexcept { return status_; }
    const HHSExactPass219RNADomainV1& record() const noexcept { return record_; }
private:
    HHSExactPass219RNADomainV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

class Strand final {
public:
    explicit Strand(std::uint32_t id) noexcept {
        status_ = hhs_exact_pass219_rna_strand_init(id, &record_);
    }
    HHSExactStatus add(const Domain& domain) noexcept {
        if (status_ != HHS_EXACT_STATUS_OK || domain.status() != HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        status_ = hhs_exact_pass219_rna_strand_add_domain(&record_, &domain.record());
        return status_;
    }
    HHSExactStatus status() const noexcept { return status_; }
    const HHSExactPass219RNAStrandV1& record() const noexcept { return record_; }
private:
    HHSExactPass219RNAStrandV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

class RuleBase {
public:
    HHSExactStatus status() const noexcept { return status_; }
    const HHSExactPass219RNARuleV1& record() const noexcept { return record_; }
protected:
    RuleBase(std::uint32_t id, std::uint32_t kind,
             std::uint32_t source, std::uint32_t target) noexcept {
        status_ = hhs_exact_pass219_rna_rule_init(id, kind, source, target, &record_);
    }
private:
    HHSExactPass219RNARuleV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

class Complement final : public RuleBase {
public: Complement(std::uint32_t id, std::uint32_t source, std::uint32_t target) noexcept
    : RuleBase(id, HHS_EXACT_PASS219_RNA_RULE_COMPLEMENT, source, target) {}
};
class Binding final : public RuleBase {
public: Binding(std::uint32_t id, std::uint32_t source, std::uint32_t target) noexcept
    : RuleBase(id, HHS_EXACT_PASS219_RNA_RULE_BINDING, source, target) {}
};
class ToeholdGate final : public RuleBase {
public: ToeholdGate(std::uint32_t id, std::uint32_t source, std::uint32_t target) noexcept
    : RuleBase(id, HHS_EXACT_PASS219_RNA_RULE_TOEHOLD, source, target) {}
};
class HairpinGate final : public RuleBase {
public: HairpinGate(std::uint32_t id, std::uint32_t source, std::uint32_t target) noexcept
    : RuleBase(id, HHS_EXACT_PASS219_RNA_RULE_HAIRPIN, source, target) {}
};
class ActivationGate final : public RuleBase {
public: ActivationGate(std::uint32_t id, std::uint32_t source, std::uint32_t target) noexcept
    : RuleBase(id, HHS_EXACT_PASS219_RNA_RULE_ACTIVATION, source, target) {}
};
class InhibitionGate final : public RuleBase {
public: InhibitionGate(std::uint32_t id, std::uint32_t source, std::uint32_t target) noexcept
    : RuleBase(id, HHS_EXACT_PASS219_RNA_RULE_INHIBITION, source, target) {}
};
class Cleavage final : public RuleBase {
public: Cleavage(std::uint32_t id, std::uint32_t source, std::uint32_t target) noexcept
    : RuleBase(id, HHS_EXACT_PASS219_RNA_RULE_CLEAVAGE, source, target) {}
};
class Release final : public RuleBase {
public: Release(std::uint32_t id, std::uint32_t source, std::uint32_t target) noexcept
    : RuleBase(id, HHS_EXACT_PASS219_RNA_RULE_RELEASE, source, target) {}
};

class TranscriptionProgram final {
public:
    explicit TranscriptionProgram(std::uint32_t id) noexcept {
        status_ = hhs_exact_pass219_rna_program_init(id, &record_);
    }
    template <class Rule>
    HHSExactStatus add(const Rule& rule) noexcept {
        if (status_ != HHS_EXACT_STATUS_OK || rule.status() != HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        status_ = hhs_exact_pass219_rna_program_add_rule(&record_, &rule.record());
        return status_;
    }
    HHSExactStatus status() const noexcept { return status_; }
    const HHSExactPass219RNAProgramV1& record() const noexcept { return record_; }
private:
    HHSExactPass219RNAProgramV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

class TranscriptionWitness final {
public:
    TranscriptionWitness(const Strand& strand,
                         const TranscriptionProgram& program,
                         const HHSExactPass219RNALineageV1& lineage) noexcept {
        status_ = hhs_exact_pass219_rna_program_execute(
            &strand.record(), &program.record(), &lineage, &record_);
    }
    HHSExactStatus status() const noexcept { return status_; }
    const HHSExactPass219TranscriptionWitnessV1& record() const noexcept { return record_; }
private:
    HHSExactPass219TranscriptionWitnessV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass219RNADomainV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219RNAStrandV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219RNARuleV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219RNAProgramV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219RNALineageV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219TranscriptionWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219TranscriptionWitnessV1>);

}  // namespace hhs::rna

#endif
