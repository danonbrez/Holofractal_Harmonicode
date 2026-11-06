#include "hhs_pass220_i087_successor_preflight_v1.hpp"
#include <cassert>
#include <vector>

static hhs::pass220::i087::OrderedWitness registered(unsigned rule_id) {
    HHSExactPass219HNANRuleV1 rule{};
    assert(hhs_exact_pass219_hnan_global_rule(rule_id, &rule) == HHS_EXACT_STATUS_OK);
    hhs::pass220::i087::OrderedWitness witness{};
    witness.native_address = rule_id;
    witness.previous_proof_identity = 179971;
    witness.claim.struct_size = sizeof(witness.claim);
    witness.claim.version = HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
    witness.claim.rule_id = rule.rule_id;
    witness.claim.lhs_node = rule.lhs_node;
    witness.claim.rhs_node = rule.rhs_node;
    witness.claim.relation = rule.relation;
    witness.claim.source_order_preserved = 1;
    witness.claim.typed_identity_preserved = 1;
    return witness;
}

static bool verify_proof(
    hhs::pass220::i087::Obligation obligation, std::uint64_t reference, void* ctx) {
    auto* rejected = static_cast<hhs::pass220::i087::Obligation*>(ctx);
    if (rejected && *rejected == obligation) return false;
    return reference >= 100U;
}
int main() {
    using hhs::pass220::i087::reconcile_ordered;
    auto global = reconcile_ordered({registered(1), registered(2), registered(3)});
    assert(global.candidate_preflight_verified);
    assert(global.ordered_steps.size() == 3);
    assert(global.inherited_global.verified_rule_mask == HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES);
    assert(!global.canonical_admission);
    auto reverse = reconcile_ordered({registered(2), registered(1)});
    assert(!reverse.candidate_preflight_verified);
    auto repeated = reconcile_ordered({registered(1), registered(1)});
    assert(!repeated.candidate_preflight_verified);
    auto bad = registered(4);
    bad.claim.scalar_substitution_requested = 1;
    assert(!reconcile_ordered({bad}).candidate_preflight_verified);
    bad = registered(4);
    bad.claim.rhs_node = HHS_EXACT_HNAN_NODE_NONE;
    assert(!reconcile_ordered({bad}).candidate_preflight_verified);
    bad = registered(4);
    bad.native_address = 0;
    assert(!reconcile_ordered({bad}).candidate_preflight_verified);
    assert(!reconcile_ordered({}).candidate_preflight_verified);
    using namespace hhs::pass220::i087;
    const SuccessorReferences refs{101, 102, 103, 104};
    assert(!prepare_successor_candidate({registered(1)}, refs, nullptr, nullptr)
                .global_successor_candidate);
    for (Obligation rejected : {Obligation::predecessor, Obligation::dependencies,
                                Obligation::successor, Obligation::closure}) {
        const auto blocked = prepare_successor_candidate(
            {registered(1)}, refs, verify_proof, &rejected);
        assert(!blocked.proof_frontier_verified);
        assert(!blocked.global_successor_candidate);
        assert(!blocked.canonical_admission);
        assert(blocked.first_unverified == rejected);
    }
    const auto accepted = prepare_successor_candidate(
        {registered(1), registered(2)}, refs, verify_proof, nullptr);
    assert(accepted.proof_frontier_verified);
    assert(accepted.global_successor_candidate);
    assert(!accepted.canonical_admission);
    const auto missing = prepare_successor_candidate(
        {registered(1)}, SuccessorReferences{101, 102, 0, 104},
        verify_proof, nullptr);
    assert(!missing.global_successor_candidate);
    assert(missing.first_unverified == Obligation::successor);
    // Repeating normalization of an accepted claim set is stable at the
    // candidate receipt level; this does not prove global successor closure.
    auto repeat = reconcile_ordered({registered(1), registered(2), registered(3)});
    assert(repeat.ordered_steps.size() == global.ordered_steps.size());
    for (std::size_t i = 0; i < repeat.ordered_steps.size(); ++i) {
        assert(repeat.ordered_steps[i].decision == global.ordered_steps[i].decision);
        assert(repeat.ordered_steps[i].registered_rule == global.ordered_steps[i].registered_rule);
    }
}
