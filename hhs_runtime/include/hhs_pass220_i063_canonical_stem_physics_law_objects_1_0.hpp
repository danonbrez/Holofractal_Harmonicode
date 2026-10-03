#ifndef HHS_PASS220_I063_CANONICAL_STEM_PHYSICS_LAW_OBJECTS_1_0_HPP
#define HHS_PASS220_I063_CANONICAL_STEM_PHYSICS_LAW_OBJECTS_1_0_HPP

#include "hhs_pass220_i061_unified_scientific_physics_synthesis_1_0.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace hhs::game::physics::law {

inline constexpr std::uint32_t kI063Version = UINT32_C(0x00010000);
inline constexpr std::uint32_t kI063Namespace = UINT32_C(0x00022063);
inline constexpr std::uint32_t kMaxLawVariables = 16U;
inline constexpr std::uint32_t kMaxDimensionEqualities = 8U;
inline constexpr std::uint32_t kMaxProductsPerEquality = 4U;
inline constexpr std::uint32_t kMaxFactorsPerProduct = 8U;

enum class LawClass : std::uint8_t {
    StandardPhysicsEquation = 1U,
    HHSAdmissibilityConstraint = 2U,
    HHSPhysicalHypothesis = 3U,
    ProjectionOnlyRelation = 4U,
};

struct DimensionSignature final {
    std::int16_t M{};
    std::int16_t L{};
    std::int16_t T{};
    std::int16_t I{};
    std::int16_t Theta{};
    std::int16_t N{};
    std::int16_t J{};
};

struct LawVariableSpec final {
    std::array<char, 16U> symbol{};
    std::array<char, 24U> unit_symbol{};
    DimensionSignature dimension{};
};

struct DimensionFactor final {
    std::uint8_t variable_index{};
    std::int8_t power{};
};

struct DimensionProduct final {
    std::uint8_t factor_count{};
    std::array<DimensionFactor, kMaxFactorsPerProduct> factors{};
};

struct DimensionalEquality final {
    std::uint8_t product_count{};
    std::array<DimensionProduct, kMaxProductsPerEquality> products{};
};

struct CanonicalPhysicsLawCandidate final {
    LawClass classification{LawClass::ProjectionOnlyRelation};
    std::uint16_t knowledge_coordinate5184{};
    std::uint8_t variable_count{};
    std::uint8_t dimensional_equality_count{};
    std::array<LawVariableSpec, kMaxLawVariables> variables{};
    std::array<DimensionalEquality, kMaxDimensionEqualities>
        dimensional_equalities{};

    std::array<char, 41U> source_git_blob_sha{};
    std::array<char, HHS_HASH72_LEN + 1U> theorem_identity_hash72{};
    std::array<char, HHS_HASH72_LEN + 1U> dependency_identity_hash72{};
    std::array<char, HHS_HASH72_LEN + 1U> law_formal_identity_hash72{};
    std::array<char, HHS_HASH72_LEN + 1U> law_object_hash72{};

    std::uint8_t measured_behavior_permitted{};
    std::uint8_t calibration_required_when_measured{};
    std::uint8_t bound_before_solver_state_construction{1U};
    std::uint8_t post_hoc_law_attachment{};
    std::uint8_t candidate_only{1U};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_commit_authority{};
    std::uint8_t canonical_hash216_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
};

struct CanonicalPhysicsLawReceipt final {
    std::uint32_t version{kI063Version};
    std::uint32_t namespace_id{kI063Namespace};
    std::uint8_t accepted{};
    std::uint8_t source_identity_shape_valid{};
    std::uint8_t proof_identity_valid{};
    std::uint8_t dimensions_valid{};
    std::uint8_t empirical_policy_valid{};
    std::uint8_t i061_scientific_admission_valid{};
    std::uint8_t shared_5184_coordinate_valid{};
    std::uint8_t pre_solver_binding_valid{};
    std::uint8_t candidate_only{1U};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_authority{};
    std::uint8_t canonical_hash216_authority{};
    std::uint8_t canonical_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
    UnifiedScientificPhysicsReceipt i061_receipt{};
};

class I063LawValidation final {
public:
    static bool cstring_nonempty(const char* value, std::size_t width) noexcept {
        if (value == nullptr || width == 0U || value[0] == '\0')
            return false;
        return std::memchr(value, '\0', width) != nullptr;
    }

    static bool git_blob_sha_valid(
        const std::array<char, 41U>& value
    ) noexcept {
        if (value[40U] != '\0')
            return false;
        for (std::size_t i = 0U; i < 40U; ++i) {
            const char c = value[i];
            if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')))
                return false;
        }
        return true;
    }

    static bool hash72_valid(
        const std::array<char, HHS_HASH72_LEN + 1U>& value
    ) noexcept {
        return I061Validation::hash72_valid(value);
    }

    static bool same_dimension(
        const DimensionSignature& a,
        const DimensionSignature& b
    ) noexcept {
        return a.M == b.M &&
               a.L == b.L &&
               a.T == b.T &&
               a.I == b.I &&
               a.Theta == b.Theta &&
               a.N == b.N &&
               a.J == b.J;
    }

    static bool add_scaled(
        DimensionSignature& out,
        const DimensionSignature& value,
        std::int8_t power
    ) noexcept {
        const auto add = [power](std::int16_t current, std::int16_t component)
            -> std::int32_t {
            return static_cast<std::int32_t>(current) +
                   static_cast<std::int32_t>(component) *
                       static_cast<std::int32_t>(power);
        };

        const std::int32_t M = add(out.M, value.M);
        const std::int32_t L = add(out.L, value.L);
        const std::int32_t T = add(out.T, value.T);
        const std::int32_t I = add(out.I, value.I);
        const std::int32_t Theta = add(out.Theta, value.Theta);
        const std::int32_t N = add(out.N, value.N);
        const std::int32_t J = add(out.J, value.J);

        const auto bounded = [](std::int32_t x) noexcept {
            return x >= INT16_MIN && x <= INT16_MAX;
        };
        if (!bounded(M) || !bounded(L) || !bounded(T) || !bounded(I) ||
            !bounded(Theta) || !bounded(N) || !bounded(J))
            return false;

        out.M = static_cast<std::int16_t>(M);
        out.L = static_cast<std::int16_t>(L);
        out.T = static_cast<std::int16_t>(T);
        out.I = static_cast<std::int16_t>(I);
        out.Theta = static_cast<std::int16_t>(Theta);
        out.N = static_cast<std::int16_t>(N);
        out.J = static_cast<std::int16_t>(J);
        return true;
    }

    static bool product_dimension(
        const CanonicalPhysicsLawCandidate& law,
        const DimensionProduct& product,
        DimensionSignature& out
    ) noexcept {
        out = DimensionSignature{};
        if (product.factor_count > kMaxFactorsPerProduct)
            return false;
        for (std::size_t i = 0U; i < product.factor_count; ++i) {
            const auto& factor = product.factors[i];
            if (factor.variable_index >= law.variable_count)
                return false;
            if (!add_scaled(
                    out,
                    law.variables[factor.variable_index].dimension,
                    factor.power))
                return false;
        }
        return true;
    }

    static bool dimensions_valid(
        const CanonicalPhysicsLawCandidate& law
    ) noexcept {
        if (law.variable_count == 0U ||
            law.variable_count > kMaxLawVariables ||
            law.dimensional_equality_count == 0U ||
            law.dimensional_equality_count > kMaxDimensionEqualities)
            return false;

        for (std::size_t v = 0U; v < law.variable_count; ++v) {
            if (!cstring_nonempty(
                    law.variables[v].symbol.data(),
                    law.variables[v].symbol.size()) ||
                !cstring_nonempty(
                    law.variables[v].unit_symbol.data(),
                    law.variables[v].unit_symbol.size()))
                return false;
        }

        for (std::size_t i = 0U; i < law.dimensional_equality_count; ++i) {
            const auto& eq = law.dimensional_equalities[i];
            if (eq.product_count < 2U ||
                eq.product_count > kMaxProductsPerEquality)
                return false;

            DimensionSignature reference{};
            if (!product_dimension(law, eq.products[0], reference))
                return false;

            for (std::size_t p = 1U; p < eq.product_count; ++p) {
                DimensionSignature current{};
                if (!product_dimension(law, eq.products[p], current) ||
                    !same_dimension(reference, current))
                    return false;
            }
        }
        return true;
    }

    static bool empirical_policy_valid(
        const CanonicalPhysicsLawCandidate& law,
        EmpiricalClaimKind claim_kind
    ) noexcept {
        if (law.classification == LawClass::HHSAdmissibilityConstraint ||
            law.classification == LawClass::ProjectionOnlyRelation) {
            if (law.measured_behavior_permitted != 0U)
                return false;
        }

        if ((law.classification == LawClass::StandardPhysicsEquation ||
             law.classification == LawClass::HHSPhysicalHypothesis) &&
            law.measured_behavior_permitted == 1U &&
            law.calibration_required_when_measured != 1U)
            return false;

        if (claim_kind == EmpiricalClaimKind::MeasuredPhysicalBehavior &&
            law.measured_behavior_permitted != 1U)
            return false;

        return true;
    }

    static bool proof_identity_valid(
        const CanonicalPhysicsLawCandidate& law,
        const UnifiedScientificPhysicsCandidate& scientific
    ) noexcept {
        return hash72_valid(law.theorem_identity_hash72) &&
               hash72_valid(law.dependency_identity_hash72) &&
               hash72_valid(law.law_formal_identity_hash72) &&
               hash72_valid(law.law_object_hash72) &&
               std::memcmp(
                   law.theorem_identity_hash72.data(),
                   kI060TheoremIdentityHash72,
                   HHS_HASH72_LEN + 1U) == 0 &&
               std::memcmp(
                   law.dependency_identity_hash72.data(),
                   kI060DependencyIdentityHash72,
                   HHS_HASH72_LEN + 1U) == 0 &&
               std::memcmp(
                   law.theorem_identity_hash72.data(),
                   scientific.formal.lean.theorem_identity_hash72.data(),
                   HHS_HASH72_LEN + 1U) == 0 &&
               std::memcmp(
                   law.dependency_identity_hash72.data(),
                   scientific.formal.lean.dependency_identity_hash72.data(),
                   HHS_HASH72_LEN + 1U) == 0;
    }
};

class CanonicalPhysicsLawCellWall final {
public:
    HHSExactStatus evaluate(
        const hhs::game::WorldCandidate& world,
        const UnifiedScientificPhysicsCandidate& scientific,
        const CanonicalPhysicsLawCandidate& law,
        CanonicalPhysicsLawReceipt& out
    ) const noexcept {
        out = CanonicalPhysicsLawReceipt{};

        if (!I063LawValidation::git_blob_sha_valid(law.source_git_blob_sha))
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        out.source_identity_shape_valid = 1U;

        if (law.knowledge_coordinate5184 >= HHS_EXACT_HASH72_COORDS ||
            law.knowledge_coordinate5184 != scientific.knowledge.linear5184)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out.shared_5184_coordinate_valid = 1U;

        if (!I063LawValidation::proof_identity_valid(law, scientific))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out.proof_identity_valid = 1U;

        if (!I063LawValidation::dimensions_valid(law))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out.dimensions_valid = 1U;

        if (!I063LawValidation::empirical_policy_valid(
                law, scientific.empirical.claim_kind))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out.empirical_policy_valid = 1U;

        if (law.bound_before_solver_state_construction != 1U ||
            law.post_hoc_law_attachment != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out.pre_solver_binding_valid = 1U;

        if (law.candidate_only != 1U ||
            law.canonical_vm81_mutation_authority != 0U ||
            law.canonical_hash72_commit_authority != 0U ||
            law.canonical_hash216_persistence_authority != 0U ||
            law.floating_point_canonical_authority != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        UnifiedScientificPhysicsReceipt i061{};
        const HHSExactStatus status =
            i061_wall_.evaluate(world, scientific, i061);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        out.i061_scientific_admission_valid = 1U;

        out.accepted = 1U;
        out.candidate_only = 1U;
        out.canonical_vm81_mutation_authority = 0U;
        out.canonical_hash72_authority = 0U;
        out.canonical_hash216_authority = 0U;
        out.canonical_persistence_authority = 0U;
        out.floating_point_canonical_authority = 0U;
        out.i061_receipt = i061;
        return HHS_EXACT_STATUS_OK;
    }

private:
    UnifiedScientificPhysicsCellWall i061_wall_{};
};

static_assert(HHS_EXACT_HASH72_COORDS == 5184U,
              "I063 laws require the Lane 5 5,184 coordinate fabric");
static_assert(kMaxLawVariables <= UINT8_MAX,
              "I063 variable count must fit its ABI field");
static_assert(kMaxDimensionEqualities <= UINT8_MAX,
              "I063 equality count must fit its ABI field");

}  // namespace hhs::game::physics::law

#endif
