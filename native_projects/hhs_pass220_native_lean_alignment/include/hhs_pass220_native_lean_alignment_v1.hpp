#ifndef HHS_PASS220_NATIVE_LEAN_ALIGNMENT_V1_HPP
#define HHS_PASS220_NATIVE_LEAN_ALIGNMENT_V1_HPP

#include "hhs_pass220_mathlib_native_v1.hpp"

#include <cstddef>
#include <cstring>
#include <string_view>

namespace hhs::alignment {

enum class PhaseV1 { plus_i, minus_i };
enum class AuthorityV1 { auth, derived };
enum class LexicalRelationV1 {
    synonym,
    antonym,
    hypernym,
    hyponym,
    holonym,
    meronym
};
enum class LexicalGeometryV1 {
    direct_pair,
    reciprocal_ratios,
    directed_inclusion_forward,
    directed_inclusion_reverse,
    whole_contains_part,
    part_contained_by_whole
};
enum class TensorStateV1 { genesis, bottom };

inline LexicalGeometryV1 expected_geometry(LexicalRelationV1 relation) noexcept {
    switch (relation) {
        case LexicalRelationV1::synonym:
            return LexicalGeometryV1::direct_pair;
        case LexicalRelationV1::antonym:
            return LexicalGeometryV1::reciprocal_ratios;
        case LexicalRelationV1::hypernym:
            return LexicalGeometryV1::directed_inclusion_forward;
        case LexicalRelationV1::hyponym:
            return LexicalGeometryV1::directed_inclusion_reverse;
        case LexicalRelationV1::holonym:
            return LexicalGeometryV1::whole_contains_part;
        case LexicalRelationV1::meronym:
            return LexicalGeometryV1::part_contained_by_whole;
    }
    return LexicalGeometryV1::direct_pair;
}

class NativeLeanProofReceiptV1 final {
public:
    NativeLeanProofReceiptV1(
        bool kernel_checked,
        bool no_sorry,
        bool no_unapproved_axioms,
        std::string_view theorem_hash72,
        std::string_view dependency_hash72,
        std::string_view transition_hash216
    ) noexcept
        : kernel_checked_(kernel_checked),
          no_sorry_(no_sorry),
          no_unapproved_axioms_(no_unapproved_axioms),
          theorem_hash72_bound_(theorem_hash72.size() == 72U),
          dependency_hash72_bound_(dependency_hash72.size() == 72U),
          transition_hash216_bound_(transition_hash216.size() == 216U) {}

    bool admitted() const noexcept {
        return kernel_checked_
            && no_sorry_
            && no_unapproved_axioms_
            && theorem_hash72_bound_
            && dependency_hash72_bound_
            && transition_hash216_bound_;
    }

    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool hash72_commit_authority() noexcept { return false; }
    static constexpr bool hash216_persistence_authority() noexcept { return false; }

private:
    bool kernel_checked_{false};
    bool no_sorry_{false};
    bool no_unapproved_axioms_{false};
    bool theorem_hash72_bound_{false};
    bool dependency_hash72_bound_{false};
    bool transition_hash216_bound_{false};
};

class NativeAlignmentWitnessV1 final {
public:
    NativeAlignmentWitnessV1(
        PhaseV1 prompt_phase,
        AuthorityV1 prompt_authority,
        PhaseV1 response_phase,
        AuthorityV1 response_authority,
        bool response_exists,
        LexicalRelationV1 lexical_relation,
        LexicalGeometryV1 lexical_geometry,
        bool prompt_bound,
        bool response_bound,
        bool antonym_opposition,
        bool phase8_canonical,
        bool direct_ab_p4,
        bool mirror_ba_negative_p4,
        bool x4,
        bool omega12,
        std::string_view delta_e,
        std::string_view psi,
        bool hash72_lineage,
        bool hash216_lineage,
        bool commutation_allowed_without_native_proof,
        const NativeLeanProofReceiptV1& proof_receipt
    ) noexcept
        : prompt_phase_(prompt_phase),
          prompt_authority_(prompt_authority),
          response_phase_(response_phase),
          response_authority_(response_authority),
          response_exists_(response_exists),
          lexical_relation_(lexical_relation),
          lexical_geometry_(lexical_geometry),
          prompt_bound_(prompt_bound),
          response_bound_(response_bound),
          antonym_opposition_(antonym_opposition),
          phase8_canonical_(phase8_canonical),
          direct_ab_p4_(direct_ab_p4),
          mirror_ba_negative_p4_(mirror_ba_negative_p4),
          x4_(x4),
          omega12_(omega12),
          delta_e_(delta_e),
          psi_(psi),
          hash72_lineage_(hash72_lineage),
          hash216_lineage_(hash216_lineage),
          commutation_allowed_without_native_proof_(
              commutation_allowed_without_native_proof),
          proof_receipt_admitted_(proof_receipt.admitted()) {}

    bool lexical_admitted() const noexcept {
        if (lexical_geometry_ != expected_geometry(lexical_relation_))
            return false;
        if (!prompt_bound_ || !response_bound_)
            return false;
        if (lexical_relation_ == LexicalRelationV1::antonym && !antonym_opposition_)
            return false;
        return true;
    }

    bool canonical() const noexcept {
        return prompt_phase_ == PhaseV1::plus_i
            && prompt_authority_ == AuthorityV1::auth
            && response_phase_ == PhaseV1::minus_i
            && response_authority_ == AuthorityV1::derived
            && response_exists_
            && lexical_admitted()
            && phase8_canonical_
            && direct_ab_p4_
            && mirror_ba_negative_p4_
            && x4_
            && omega12_
            && exact_zero(delta_e_)
            && exact_zero(psi_)
            && hash72_lineage_
            && hash216_lineage_
            && !commutation_allowed_without_native_proof_
            && proof_receipt_admitted_;
    }

    TensorStateV1 state() const noexcept {
        return canonical() ? TensorStateV1::genesis : TensorStateV1::bottom;
    }

    static constexpr bool response_free_state_admitted() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool hash72_commit_authority() noexcept { return false; }
    static constexpr bool hash216_persistence_authority() noexcept { return false; }

private:
    static bool exact_zero(const hhs::mathlib::NativeInt& value) noexcept {
        return value.valid() && std::strcmp(value.decimal(), "0") == 0;
    }

    PhaseV1 prompt_phase_;
    AuthorityV1 prompt_authority_;
    PhaseV1 response_phase_;
    AuthorityV1 response_authority_;
    bool response_exists_;
    LexicalRelationV1 lexical_relation_;
    LexicalGeometryV1 lexical_geometry_;
    bool prompt_bound_;
    bool response_bound_;
    bool antonym_opposition_;
    bool phase8_canonical_;
    bool direct_ab_p4_;
    bool mirror_ba_negative_p4_;
    bool x4_;
    bool omega12_;
    hhs::mathlib::NativeInt delta_e_;
    hhs::mathlib::NativeInt psi_;
    bool hash72_lineage_;
    bool hash216_lineage_;
    bool commutation_allowed_without_native_proof_;
    bool proof_receipt_admitted_;
};

}  // namespace hhs::alignment

#endif
