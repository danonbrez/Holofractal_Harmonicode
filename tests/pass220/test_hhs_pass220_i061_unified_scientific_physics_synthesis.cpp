#include "hhs_pass220_i061_unified_scientific_physics_synthesis_1_0.hpp"

#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>

using namespace hhs::game;
using namespace hhs::game::physics;

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

void fill_raw_hash216(char (&out)[HHS_HASH216_LEN + 1], char symbol) {
    for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i)
        out[i] = symbol;
    out[HHS_HASH216_LEN] = '\0';
}

WorldCandidate world() {
    WorldCandidate w{};
    w.tick = 144U;
    w.world_epoch = 1U;
    w.entity_count = 8U;
    w.active_entity_count = 8U;
    w.deterministic_replay_required = 1U;
    w.exact_transform_authority = 1U;
    fill_raw_hash216(w.parent_hash216, '0');
    return w;
}

UnifiedScientificPhysicsCandidate candidate(
    EmpiricalClaimKind claim = EmpiricalClaimKind::FormalOnly
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

    c.physics.tick = 144U;
    c.physics.body_count = 8U;
    c.physics.collider_count = 12U;
    c.physics.constraint_count = 4U;
    c.physics.delta_time = HHSExactRational64{1, 120U};
    c.physics.exact_state_required = 1U;
    c.physics.host_float_authority_requested = 0U;
    c.physics.renderer_mutation_authority_requested = 0U;

    c.knowledge.linear5184 = 5183U;
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

void test_formal_only_accepts() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();
    const auto c = candidate();

    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_OK);
    assert(receipt.accepted == 1U);
    assert(receipt.formal_valid == 1U);
    assert(receipt.empirical_required == 0U);
    assert(receipt.empirical_valid == 1U);
    assert(receipt.intrinsic_lean_binding == 1U);
    assert(receipt.lane5_5184_hash216_binding_valid == 1U);
    assert(receipt.inherited_i059_physics_cell_accepted == 1U);
    assert(receipt.candidate_only == 1U);
    assert(receipt.canonical_vm81_mutation_authority == 0U);
    assert(receipt.canonical_hash72_authority == 0U);
    assert(receipt.canonical_hash216_authority == 0U);
    assert(receipt.canonical_persistence_authority == 0U);
    assert(receipt.floating_point_canonical_authority == 0U);
}

void test_measured_claim_requires_empirical_evidence() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();

    auto bad = candidate(EmpiricalClaimKind::MeasuredPhysicalBehavior);
    bad.empirical.evidence_count = 0U;
    assert(wall.evaluate(w, bad, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    const auto good = candidate(EmpiricalClaimKind::MeasuredPhysicalBehavior);
    receipt = UnifiedScientificPhysicsReceipt{};
    assert(wall.evaluate(w, good, receipt) == HHS_EXACT_STATUS_OK);
    assert(receipt.empirical_required == 1U);
    assert(receipt.empirical_valid == 1U);
}

void test_post_hoc_proof_attachment_fails() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();
    auto c = candidate();

    c.post_hoc_proof_attachment = 1U;
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    c = candidate();
    c.formal.lean.post_hoc_attachment = 1U;
    receipt = UnifiedScientificPhysicsReceipt{};
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_wrong_i060_hash72_identity_fails() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();

    auto c = candidate();
    fill_chars(c.formal.lean.theorem_identity_hash72, '1');
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    c = candidate();
    fill_chars(c.formal.lean.dependency_identity_hash72, '2');
    receipt = UnifiedScientificPhysicsReceipt{};
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_missing_kernel_or_axiom_validation_fails() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();

    auto c = candidate();
    c.formal.lean.kernel_build_validated = 0U;
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    c = candidate();
    c.formal.lean.axiom_audit_validated = 0U;
    receipt = UnifiedScientificPhysicsReceipt{};
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_formal_cannot_substitute_for_empirical() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();
    auto c = candidate(EmpiricalClaimKind::MeasuredPhysicalBehavior);

    c.empirical.empirical_valid = 0U;
    c.formal.formal_valid = 1U;
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_empirical_cannot_substitute_for_formal() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();
    auto c = candidate(EmpiricalClaimKind::MeasuredPhysicalBehavior);

    c.formal.formal_valid = 0U;
    c.empirical.empirical_valid = 1U;
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_hash216_order_drift_fails() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();
    auto c = candidate();

    const char tmp = c.knowledge.candidate_hash216[0];
    c.knowledge.candidate_hash216[0] =
        c.knowledge.candidate_hash216[HHS_HASH72_LEN];
    c.knowledge.candidate_hash216[HHS_HASH72_LEN] = tmp;
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_knowledge_coordinate_out_of_range_fails() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();
    auto c = candidate();

    c.knowledge.linear5184 = 5184U;
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_authority_escalation_fails() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();

    auto c = candidate();
    c.knowledge.mutation_authority = 1U;
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    c = candidate();
    c.formal.lean.lean_has_hash216_persistence_authority = 1U;
    receipt = UnifiedScientificPhysicsReceipt{};
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

void test_i059_physics_invariants_still_apply() {
    UnifiedScientificPhysicsCellWall wall{};
    UnifiedScientificPhysicsReceipt receipt{};
    const auto w = world();

    auto c = candidate();
    c.physics.tick = w.tick + 1U;
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    c = candidate();
    c.physics.host_float_authority_requested = 1U;
    receipt = UnifiedScientificPhysicsReceipt{};
    assert(wall.evaluate(w, c, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

}  // namespace

int main() {
    test_formal_only_accepts();
    test_measured_claim_requires_empirical_evidence();
    test_post_hoc_proof_attachment_fails();
    test_wrong_i060_hash72_identity_fails();
    test_missing_kernel_or_axiom_validation_fails();
    test_formal_cannot_substitute_for_empirical();
    test_empirical_cannot_substitute_for_formal();
    test_hash216_order_drift_fails();
    test_knowledge_coordinate_out_of_range_fails();
    test_authority_escalation_fails();
    test_i059_physics_invariants_still_apply();
    return 0;
}
