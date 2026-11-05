#include "hhs_pass220_i063_canonical_stem_physics_law_objects_1_0.hpp"

#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>

using namespace hhs::game;
using namespace hhs::game::physics;
using namespace hhs::game::physics::law;

namespace {

template <std::size_t N>
void fill_chars(std::array<char, N>& out, char symbol) {
    static_assert(N > 1U);
    for (std::size_t i = 0U; i + 1U < N; ++i)
        out[i] = symbol;
    out[N - 1U] = '\0';
}

template <std::size_t N, std::size_t M>
void copy_literal(std::array<char, N>& out, const char (&literal)[M]) {
    static_assert(N == M);
    std::memcpy(out.data(), literal, N);
}

template <std::size_t N>
void copy_text(std::array<char, N>& out, const char* text) {
    std::memset(out.data(), 0, N);
    const std::size_t length = std::strlen(text);
    assert(length + 1U <= N);
    std::memcpy(out.data(), text, length);
}

void fill_raw_hash216(char (&out)[HHS_HASH216_LEN + 1], char symbol) {
    for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i)
        out[i] = symbol;
    out[HHS_HASH216_LEN] = '\0';
}

WorldCandidate world() {
    WorldCandidate w{};
    w.tick = 63U;
    w.world_epoch = 1U;
    w.entity_count = 8U;
    w.active_entity_count = 8U;
    w.deterministic_replay_required = 1U;
    w.exact_transform_authority = 1U;
    fill_raw_hash216(w.parent_hash216, '0');
    return w;
}

UnifiedScientificPhysicsCandidate scientific(
    EmpiricalClaimKind claim = EmpiricalClaimKind::FormalOnly,
    std::uint16_t coordinate = 13U
) {
    UnifiedScientificPhysicsCandidate c{};

    copy_literal(
        c.formal.lean.theorem_identity_hash72,
        kI060TheoremIdentityHash72);
    copy_literal(
        c.formal.lean.dependency_identity_hash72,
        kI060DependencyIdentityHash72);
    c.formal.lean.theorem_identity_validated = 1U;
    c.formal.lean.dependency_identity_validated = 1U;
    c.formal.lean.kernel_build_validated = 1U;
    c.formal.lean.leanchecker_validated = 1U;
    c.formal.lean.axiom_audit_validated = 1U;
    c.formal.lean.bound_before_physics_candidate_construction = 1U;
    c.formal.lean.post_hoc_attachment = 0U;
    c.formal.lean.lean_has_vm81_mutation_authority = 0U;
    c.formal.lean.lean_has_hash72_commit_authority = 0U;
    c.formal.lean.lean_has_hash216_persistence_authority = 0U;
    c.formal.verbatim_hhs_source_identity_verified = 1U;
    c.formal.whitepaper_proof_identity_verified = 1U;
    c.formal.wolfram_source_identity_verified = 1U;
    c.formal.wolfram_formalization_verified = 1U;
    c.formal.formal_valid = 1U;
    c.formal.formal_substitutes_for_empirical = 0U;
    fill_chars(c.formal.formal_axis_hash72, '3');

    c.empirical.claim_kind = claim;
    c.empirical.residual = HHSExactRational64{0, 1U};
    c.empirical.error_bound = HHSExactRational64{1, 1000U};
    c.empirical.empirical_substitutes_for_formal = 0U;
    c.empirical.empirical_valid = 1U;
    fill_chars(c.empirical.empirical_axis_hash72, '4');
    if (claim == EmpiricalClaimKind::MeasuredPhysicalBehavior) {
        c.empirical.evidence_count = 1U;
        c.empirical.declared_domain_present = 1U;
        c.empirical.units_dimensions_verified = 1U;
        c.empirical.calibration_or_experiment_verified = 1U;
        c.empirical.replay_evidence_verified = 1U;
        c.empirical.residual_bound_verified = 1U;
    }

    c.physics.tick = 63U;
    c.physics.body_count = 8U;
    c.physics.collider_count = 12U;
    c.physics.constraint_count = 4U;
    c.physics.delta_time = HHSExactRational64{1, 120U};
    c.physics.exact_state_required = 1U;

    c.knowledge.linear5184 = coordinate;
    c.knowledge.formal_axis_hash72 = c.formal.formal_axis_hash72;
    c.knowledge.empirical_axis_hash72 = c.empirical.empirical_axis_hash72;
    fill_chars(c.knowledge.physics_candidate_hash72, '5');
    for (std::size_t i = 0U; i < HHS_HASH72_LEN; ++i) {
        c.knowledge.candidate_hash216[i] = c.knowledge.formal_axis_hash72[i];
        c.knowledge.candidate_hash216[i + HHS_HASH72_LEN] =
            c.knowledge.empirical_axis_hash72[i];
        c.knowledge.candidate_hash216[i + 2U * HHS_HASH72_LEN] =
            c.knowledge.physics_candidate_hash72[i];
    }
    c.knowledge.candidate_hash216[HHS_HASH216_LEN] = '\0';
    fill_chars(c.knowledge.parent_hash216, '6');
    c.knowledge.relation_instance_of = 1U;
    c.knowledge.knowledge_graph_projection_only = 1U;

    fill_chars(c.intrinsic_proof_binding_hash72, '7');
    fill_chars(c.candidate_receipt_hash72, '8');
    c.proof_identity_bound_before_construction = 1U;
    c.post_hoc_proof_attachment = 0U;
    c.candidate_only = 1U;
    return c;
}

CanonicalPhysicsLawCandidate relativistic_law() {
    CanonicalPhysicsLawCandidate law{};
    law.classification = LawClass::StandardPhysicsEquation;
    law.knowledge_coordinate5184 = 13U;
    law.variable_count = 4U;
    law.dimensional_equality_count = 1U;

    copy_text(law.variables[0].symbol, "E");
    copy_text(law.variables[0].unit_symbol, "J");
    law.variables[0].dimension = DimensionSignature{1, 2, -2, 0, 0, 0, 0};

    copy_text(law.variables[1].symbol, "p");
    copy_text(law.variables[1].unit_symbol, "kg*m/s");
    law.variables[1].dimension = DimensionSignature{1, 1, -1, 0, 0, 0, 0};

    copy_text(law.variables[2].symbol, "c");
    copy_text(law.variables[2].unit_symbol, "m/s");
    law.variables[2].dimension = DimensionSignature{0, 1, -1, 0, 0, 0, 0};

    copy_text(law.variables[3].symbol, "m");
    copy_text(law.variables[3].unit_symbol, "kg");
    law.variables[3].dimension = DimensionSignature{1, 0, 0, 0, 0, 0, 0};

    auto& eq = law.dimensional_equalities[0];
    eq.product_count = 3U;

    eq.products[0].factor_count = 1U;
    eq.products[0].factors[0] = DimensionFactor{0U, 2};

    eq.products[1].factor_count = 2U;
    eq.products[1].factors[0] = DimensionFactor{1U, 2};
    eq.products[1].factors[1] = DimensionFactor{2U, 2};

    eq.products[2].factor_count = 2U;
    eq.products[2].factors[0] = DimensionFactor{3U, 2};
    eq.products[2].factors[1] = DimensionFactor{2U, 4};

    copy_text(
        law.source_git_blob_sha,
        "56d5599011d489f3273d4280b8e4ba0e1cfd8165");
    copy_literal(law.theorem_identity_hash72, kI060TheoremIdentityHash72);
    copy_literal(law.dependency_identity_hash72, kI060DependencyIdentityHash72);
    fill_chars(law.law_formal_identity_hash72, '9');
    fill_chars(law.law_object_hash72, 'a');

    law.measured_behavior_permitted = 1U;
    law.calibration_required_when_measured = 1U;
    law.bound_before_solver_state_construction = 1U;
    law.post_hoc_law_attachment = 0U;
    law.candidate_only = 1U;
    return law;
}

CanonicalPhysicsLawCandidate hhs_admission_law() {
    CanonicalPhysicsLawCandidate law{};
    law.classification = LawClass::HHSAdmissibilityConstraint;
    law.knowledge_coordinate5184 = 10U;
    law.variable_count = 3U;
    law.dimensional_equality_count = 1U;

    copy_text(law.variables[0].symbol, "P");
    copy_text(law.variables[0].unit_symbol, "1");
    copy_text(law.variables[1].symbol, "A");
    copy_text(law.variables[1].unit_symbol, "1");
    copy_text(law.variables[2].symbol, "B");
    copy_text(law.variables[2].unit_symbol, "1");

    auto& eq = law.dimensional_equalities[0];
    eq.product_count = 2U;
    eq.products[0].factor_count = 1U;
    eq.products[0].factors[0] = DimensionFactor{0U, 4};
    eq.products[1].factor_count = 2U;
    eq.products[1].factors[0] = DimensionFactor{1U, 1};
    eq.products[1].factors[1] = DimensionFactor{2U, 1};

    copy_text(
        law.source_git_blob_sha,
        "56d5599011d489f3273d4280b8e4ba0e1cfd8165");
    copy_literal(law.theorem_identity_hash72, kI060TheoremIdentityHash72);
    copy_literal(law.dependency_identity_hash72, kI060DependencyIdentityHash72);
    fill_chars(law.law_formal_identity_hash72, 'b');
    fill_chars(law.law_object_hash72, 'c');

    law.measured_behavior_permitted = 0U;
    law.calibration_required_when_measured = 0U;
    law.bound_before_solver_state_construction = 1U;
    law.candidate_only = 1U;
    return law;
}

void test_relativistic_law_accepts_through_i061() {
    CanonicalPhysicsLawCellWall wall{};
    CanonicalPhysicsLawReceipt receipt{};
    const auto w = world();
    const auto s = scientific(EmpiricalClaimKind::FormalOnly, 13U);
    const auto law = relativistic_law();

    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_OK);
    assert(receipt.accepted == 1U);
    assert(receipt.source_identity_shape_valid == 1U);
    assert(receipt.proof_identity_valid == 1U);
    assert(receipt.dimensions_valid == 1U);
    assert(receipt.empirical_policy_valid == 1U);
    assert(receipt.i061_scientific_admission_valid == 1U);
    assert(receipt.shared_5184_coordinate_valid == 1U);
    assert(receipt.pre_solver_binding_valid == 1U);
    assert(receipt.canonical_vm81_mutation_authority == 0U);
    assert(receipt.canonical_hash72_authority == 0U);
    assert(receipt.canonical_hash216_authority == 0U);
    assert(receipt.canonical_persistence_authority == 0U);
}

void test_dimension_mismatch_fails() {
    CanonicalPhysicsLawCellWall wall{};
    CanonicalPhysicsLawReceipt receipt{};
    const auto w = world();
    const auto s = scientific(EmpiricalClaimKind::FormalOnly, 13U);
    auto law = relativistic_law();

    law.variables[0].dimension.L = 3;
    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_wrong_i060_identity_fails() {
    CanonicalPhysicsLawCellWall wall{};
    CanonicalPhysicsLawReceipt receipt{};
    const auto w = world();
    const auto s = scientific(EmpiricalClaimKind::FormalOnly, 13U);
    auto law = relativistic_law();

    fill_chars(law.theorem_identity_hash72, 'd');
    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_coordinate_drift_fails() {
    CanonicalPhysicsLawCellWall wall{};
    CanonicalPhysicsLawReceipt receipt{};
    const auto w = world();
    const auto s = scientific(EmpiricalClaimKind::FormalOnly, 14U);
    const auto law = relativistic_law();

    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_post_hoc_law_attachment_fails() {
    CanonicalPhysicsLawCellWall wall{};
    CanonicalPhysicsLawReceipt receipt{};
    const auto w = world();
    const auto s = scientific(EmpiricalClaimKind::FormalOnly, 13U);
    auto law = relativistic_law();

    law.bound_before_solver_state_construction = 0U;
    law.post_hoc_law_attachment = 1U;
    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_hhs_admission_constraint_cannot_be_measured_physics() {
    CanonicalPhysicsLawCellWall wall{};
    CanonicalPhysicsLawReceipt receipt{};
    const auto w = world();
    const auto s = scientific(EmpiricalClaimKind::MeasuredPhysicalBehavior, 10U);
    auto law = hhs_admission_law();

    law.measured_behavior_permitted = 1U;
    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    law = hhs_admission_law();
    receipt = CanonicalPhysicsLawReceipt{};
    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_standard_measured_claim_requires_calibration_policy() {
    CanonicalPhysicsLawCellWall wall{};
    CanonicalPhysicsLawReceipt receipt{};
    const auto w = world();
    const auto s = scientific(EmpiricalClaimKind::MeasuredPhysicalBehavior, 13U);
    auto law = relativistic_law();

    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_OK);

    law.calibration_required_when_measured = 0U;
    receipt = CanonicalPhysicsLawReceipt{};
    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_authority_escalation_fails() {
    CanonicalPhysicsLawCellWall wall{};
    CanonicalPhysicsLawReceipt receipt{};
    const auto w = world();
    const auto s = scientific(EmpiricalClaimKind::FormalOnly, 13U);
    auto law = relativistic_law();

    law.canonical_vm81_mutation_authority = 1U;
    assert(wall.evaluate(w, s, law, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

}  // namespace

int main() {
    test_relativistic_law_accepts_through_i061();
    test_dimension_mismatch_fails();
    test_wrong_i060_identity_fails();
    test_coordinate_drift_fails();
    test_post_hoc_law_attachment_fails();
    test_hhs_admission_constraint_cannot_be_measured_physics();
    test_standard_measured_claim_requires_calibration_policy();
    test_authority_escalation_fails();
    return 0;
}
