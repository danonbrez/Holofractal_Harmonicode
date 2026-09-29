#ifndef HHS_PASS220_I061_UNIFIED_SCIENTIFIC_PHYSICS_SYNTHESIS_1_0_HPP
#define HHS_PASS220_I061_UNIFIED_SCIENTIFIC_PHYSICS_SYNTHESIS_1_0_HPP

#include "hhs_pass220_native_3d_engine_cell_wall_1_0.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace hhs::game::physics {

inline constexpr std::uint32_t kI061Version = UINT32_C(0x00010000);
inline constexpr std::uint32_t kI061Namespace = UINT32_C(0x00022061);
inline constexpr char kI061ParentMain[] =
    "ad697affec1eb87d413f25ddb9aa4ece403506ff";
inline constexpr char kHash72Alphabet[] =
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

enum class EmpiricalClaimKind : std::uint8_t {
    FormalOnly = 0U,
    MeasuredPhysicalBehavior = 1U,
};

struct LeanProofIdentityBinding final {
    std::array<char, HHS_HASH72_LEN + 1U> theorem_identity_hash72{};
    std::array<char, HHS_HASH72_LEN + 1U> dependency_identity_hash72{};
    std::uint8_t theorem_identity_validated{};
    std::uint8_t dependency_identity_validated{};
    std::uint8_t kernel_build_validated{};
    std::uint8_t leanchecker_validated{};
    std::uint8_t axiom_audit_validated{};
    std::uint8_t bound_before_physics_candidate_construction{};
    std::uint8_t post_hoc_attachment{};
    std::uint8_t lean_has_vm81_mutation_authority{};
    std::uint8_t lean_has_hash72_commit_authority{};
    std::uint8_t lean_has_hash216_persistence_authority{};
};

struct FormalValidityAxis final {
    LeanProofIdentityBinding lean{};
    std::uint8_t verbatim_hhs_source_identity_verified{};
    std::uint8_t whitepaper_proof_identity_verified{};
    std::uint8_t wolfram_source_identity_verified{};
    std::uint8_t wolfram_formalization_verified{};
    std::uint8_t formal_valid{};
    std::uint8_t formal_substitutes_for_empirical{};
    std::array<char, HHS_HASH72_LEN + 1U> formal_axis_hash72{};
};

struct EmpiricalCorrespondenceAxis final {
    EmpiricalClaimKind claim_kind{EmpiricalClaimKind::FormalOnly};
    std::uint32_t evidence_count{};
    HHSExactRational64 residual{0, 1U};
    HHSExactRational64 error_bound{0, 1U};
    std::uint8_t declared_domain_present{};
    std::uint8_t units_dimensions_verified{};
    std::uint8_t calibration_or_experiment_verified{};
    std::uint8_t replay_evidence_verified{};
    std::uint8_t residual_bound_verified{};
    std::uint8_t empirical_valid{};
    std::uint8_t empirical_substitutes_for_formal{};
    std::array<char, HHS_HASH72_LEN + 1U> empirical_axis_hash72{};
};

struct Lane5PhysicsKnowledgeBinding final {
    std::uint16_t linear5184{};
    std::array<char, HHS_HASH72_LEN + 1U> formal_axis_hash72{};
    std::array<char, HHS_HASH72_LEN + 1U> empirical_axis_hash72{};
    std::array<char, HHS_HASH72_LEN + 1U> physics_candidate_hash72{};
    std::array<char, HHS_HASH216_LEN + 1U> candidate_hash216{};
    std::array<char, HHS_HASH216_LEN + 1U> parent_hash216{};
    std::uint8_t relation_instance_of{1U};
    std::uint8_t knowledge_graph_projection_only{1U};
    std::uint8_t execution_authority{};
    std::uint8_t mutation_authority{};
    std::uint8_t canonical_hash72_commit_authority{};
    std::uint8_t canonical_hash216_persistence_authority{};
    std::uint8_t floating_point_authority{};
};

struct UnifiedScientificPhysicsCandidate final {
    FormalValidityAxis formal{};
    EmpiricalCorrespondenceAxis empirical{};
    hhs::game::PhysicsCandidate physics{};
    Lane5PhysicsKnowledgeBinding knowledge{};
    std::array<char, HHS_HASH72_LEN + 1U> intrinsic_proof_binding_hash72{};
    std::array<char, HHS_HASH72_LEN + 1U> candidate_receipt_hash72{};
    std::uint8_t proof_identity_bound_before_construction{};
    std::uint8_t post_hoc_proof_attachment{};
    std::uint8_t candidate_only{1U};
};

struct UnifiedScientificPhysicsReceipt final {
    std::uint32_t version{kI061Version};
    std::uint32_t namespace_id{kI061Namespace};
    std::uint8_t accepted{};
    std::uint8_t formal_valid{};
    std::uint8_t empirical_required{};
    std::uint8_t empirical_valid{};
    std::uint8_t intrinsic_lean_binding{};
    std::uint8_t lane5_5184_hash216_binding_valid{};
    std::uint8_t inherited_i059_physics_cell_accepted{};
    std::uint8_t candidate_only{1U};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_authority{};
    std::uint8_t canonical_hash216_authority{};
    std::uint8_t canonical_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
    hhs::game::EngineCellReceipt inherited_physics_receipt{};
};

class I061Validation final {
public:
    static bool hash72_valid(
        const std::array<char, HHS_HASH72_LEN + 1U>& value
    ) noexcept {
        if (value[HHS_HASH72_LEN] != '\0')
            return false;
        for (std::size_t i = 0U; i < HHS_HASH72_LEN; ++i) {
            if (value[i] == '\0' || std::strchr(kHash72Alphabet, value[i]) == nullptr)
                return false;
        }
        return true;
    }

    static bool hash216_valid(
        const std::array<char, HHS_HASH216_LEN + 1U>& value
    ) noexcept {
        if (value[HHS_HASH216_LEN] != '\0')
            return false;
        for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i) {
            if (value[i] == '\0' || std::strchr(kHash72Alphabet, value[i]) == nullptr)
                return false;
        }
        return true;
    }

    static bool hash216_is_ordered_axes(
        const Lane5PhysicsKnowledgeBinding& knowledge
    ) noexcept {
        if (!hash72_valid(knowledge.formal_axis_hash72) ||
            !hash72_valid(knowledge.empirical_axis_hash72) ||
            !hash72_valid(knowledge.physics_candidate_hash72) ||
            !hash216_valid(knowledge.candidate_hash216))
            return false;
        return std::memcmp(
                   knowledge.candidate_hash216.data(),
                   knowledge.formal_axis_hash72.data(),
                   HHS_HASH72_LEN) == 0 &&
               std::memcmp(
                   knowledge.candidate_hash216.data() + HHS_HASH72_LEN,
                   knowledge.empirical_axis_hash72.data(),
                   HHS_HASH72_LEN) == 0 &&
               std::memcmp(
                   knowledge.candidate_hash216.data() + 2U * HHS_HASH72_LEN,
                   knowledge.physics_candidate_hash72.data(),
                   HHS_HASH72_LEN) == 0;
    }

    static bool formal_axis_valid(const FormalValidityAxis& formal) noexcept {
        const auto& lean = formal.lean;
        return hash72_valid(lean.theorem_identity_hash72) &&
               hash72_valid(lean.dependency_identity_hash72) &&
               lean.theorem_identity_validated == 1U &&
               lean.dependency_identity_validated == 1U &&
               lean.kernel_build_validated == 1U &&
               lean.leanchecker_validated == 1U &&
               lean.axiom_audit_validated == 1U &&
               lean.bound_before_physics_candidate_construction == 1U &&
               lean.post_hoc_attachment == 0U &&
               lean.lean_has_vm81_mutation_authority == 0U &&
               lean.lean_has_hash72_commit_authority == 0U &&
               lean.lean_has_hash216_persistence_authority == 0U &&
               formal.verbatim_hhs_source_identity_verified == 1U &&
               formal.whitepaper_proof_identity_verified == 1U &&
               formal.wolfram_source_identity_verified == 1U &&
               formal.wolfram_formalization_verified == 1U &&
               formal.formal_valid == 1U &&
               formal.formal_substitutes_for_empirical == 0U &&
               hash72_valid(formal.formal_axis_hash72);
    }

    static bool empirical_axis_valid(
        const EmpiricalCorrespondenceAxis& empirical
    ) noexcept {
        if (!hhs::game::EngineFoundationValidation::valid_rational(
                empirical.residual) ||
            !hhs::game::EngineFoundationValidation::valid_rational(
                empirical.error_bound) ||
            empirical.error_bound.numerator < 0 ||
            empirical.empirical_substitutes_for_formal != 0U ||
            !hash72_valid(empirical.empirical_axis_hash72))
            return false;

        if (empirical.claim_kind == EmpiricalClaimKind::FormalOnly)
            return empirical.empirical_valid == 1U;

        if (empirical.claim_kind != EmpiricalClaimKind::MeasuredPhysicalBehavior)
            return false;

        return empirical.evidence_count > 0U &&
               empirical.declared_domain_present == 1U &&
               empirical.units_dimensions_verified == 1U &&
               empirical.calibration_or_experiment_verified == 1U &&
               empirical.replay_evidence_verified == 1U &&
               empirical.residual_bound_verified == 1U &&
               empirical.empirical_valid == 1U;
    }

    static bool knowledge_binding_valid(
        const Lane5PhysicsKnowledgeBinding& knowledge,
        const FormalValidityAxis& formal,
        const EmpiricalCorrespondenceAxis& empirical
    ) noexcept {
        return knowledge.linear5184 < HHS_EXACT_HASH72_COORDS &&
               knowledge.relation_instance_of == 1U &&
               knowledge.knowledge_graph_projection_only == 1U &&
               knowledge.execution_authority == 0U &&
               knowledge.mutation_authority == 0U &&
               knowledge.canonical_hash72_commit_authority == 0U &&
               knowledge.canonical_hash216_persistence_authority == 0U &&
               knowledge.floating_point_authority == 0U &&
               hash216_valid(knowledge.parent_hash216) &&
               hash216_is_ordered_axes(knowledge) &&
               std::memcmp(
                   knowledge.formal_axis_hash72.data(),
                   formal.formal_axis_hash72.data(),
                   HHS_HASH72_LEN + 1U) == 0 &&
               std::memcmp(
                   knowledge.empirical_axis_hash72.data(),
                   empirical.empirical_axis_hash72.data(),
                   HHS_HASH72_LEN + 1U) == 0;
    }
};

class UnifiedScientificPhysicsCellWall final {
public:
    HHSExactStatus evaluate(
        const hhs::game::WorldCandidate& world,
        const UnifiedScientificPhysicsCandidate& candidate,
        UnifiedScientificPhysicsReceipt& out
    ) const noexcept {
        out = UnifiedScientificPhysicsReceipt{};

        if (candidate.proof_identity_bound_before_construction != 1U ||
            candidate.post_hoc_proof_attachment != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (!I061Validation::formal_axis_valid(candidate.formal))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        const bool empirical_required =
            candidate.empirical.claim_kind ==
            EmpiricalClaimKind::MeasuredPhysicalBehavior;
        if (!I061Validation::empirical_axis_valid(candidate.empirical))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (!I061Validation::hash72_valid(
                candidate.intrinsic_proof_binding_hash72) ||
            !I061Validation::hash72_valid(candidate.candidate_receipt_hash72))
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;

        if (!I061Validation::knowledge_binding_valid(
                candidate.knowledge,
                candidate.formal,
                candidate.empirical))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (std::memcmp(
                candidate.formal.lean.theorem_identity_hash72.data(),
                candidate.formal.formal_axis_hash72.data(),
                HHS_HASH72_LEN) == 0 ||
            std::memcmp(
                candidate.formal.lean.dependency_identity_hash72.data(),
                candidate.formal.formal_axis_hash72.data(),
                HHS_HASH72_LEN) == 0) {
            /*
             * The axis identity is a composite identity, not an alias of either
             * Lean identity.  Reject accidental identity collapse.
             */
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        hhs::game::EngineCellReceipt inherited{};
        const HHSExactStatus status =
            inherited_physics_.evaluate(world, candidate.physics, inherited);
        if (status != HHS_EXACT_STATUS_OK)
            return status;

        out.accepted = 1U;
        out.formal_valid = 1U;
        out.empirical_required = empirical_required ? 1U : 0U;
        out.empirical_valid = 1U;
        out.intrinsic_lean_binding = 1U;
        out.lane5_5184_hash216_binding_valid = 1U;
        out.inherited_i059_physics_cell_accepted = 1U;
        out.candidate_only = 1U;
        out.canonical_vm81_mutation_authority = 0U;
        out.canonical_hash72_authority = 0U;
        out.canonical_hash216_authority = 0U;
        out.canonical_persistence_authority = 0U;
        out.floating_point_canonical_authority = 0U;
        out.inherited_physics_receipt = inherited;
        return HHS_EXACT_STATUS_OK;
    }

private:
    hhs::game::PhysicsCellWall inherited_physics_{};
};

static_assert(HHS_EXACT_HASH72_COORDS == 5184U,
              "I061 physics knowledge graph requires the 5184 coordinate fabric");
static_assert(HHS_HASH216_LEN == 3U * HHS_HASH72_LEN,
              "I061 candidate Hash216 is ordered formal+empirical+physics Hash72");

}  // namespace hhs::game::physics

#endif
