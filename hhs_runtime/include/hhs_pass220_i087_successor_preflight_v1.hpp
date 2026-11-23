#ifndef HHS_PASS220_I087_SUCCESSOR_PREFLIGHT_V1_HPP
#define HHS_PASS220_I087_SUCCESSOR_PREFLIGHT_V1_HPP

#include "hhs_pass220_i087_ordered_reconciliation_v1.hpp"
#include <cstdint>
#include <vector>

namespace hhs::pass220::i087 {

// These are opaque native-issued proof references, NOT user assertions.
// Verification must be supplied by the existing trusted native membrane.
struct SuccessorReferences {
    std::uint64_t predecessor_identity = 0;
    std::uint64_t inherited_dependency_identity = 0;
    std::uint64_t successor_relation_identity = 0;
    std::uint64_t global_closure_identity = 0;
};

enum class Obligation : std::uint32_t {
    predecessor = 1, dependencies = 2, successor = 3, closure = 4
};
using NativeProofVerifier = bool (*)(
    Obligation, std::uint64_t proof_reference, void* trusted_context);

struct SuccessorCandidate {
    CandidateTrace reconciliation{};
    bool proof_frontier_verified = false;
    bool global_successor_candidate = false;
    bool canonical_admission = false;
    Obligation first_unverified = Obligation::predecessor;
};

inline SuccessorCandidate prepare_successor_candidate(
    const std::vector<OrderedWitness>& witnesses,
    const SuccessorReferences& refs,
    NativeProofVerifier verifier,
    void* trusted_context) {
    SuccessorCandidate out;
    // No independent proof-reuse authority: an unavailable verifier is HALT.
    if (!verifier) return out;
    const struct Check { Obligation kind; std::uint64_t reference; } checks[] = {
        {Obligation::predecessor, refs.predecessor_identity},
        {Obligation::dependencies, refs.inherited_dependency_identity},
        {Obligation::successor, refs.successor_relation_identity},
        {Obligation::closure, refs.global_closure_identity}
    };
    for (const auto& check : checks) {
        out.first_unverified = check.kind;
        if (!check.reference || !verifier(check.kind, check.reference, trusted_context))
            return out;
    }
    out.proof_frontier_verified = true;
    // The inherited C wall remains the sole global constraint resolver.
    out.reconciliation = reconcile_ordered(witnesses);
    out.global_successor_candidate =
        out.reconciliation.candidate_preflight_verified &&
        !out.reconciliation.canonical_admission;
    // Only the existing VM81 signed admission path can set canonical status.
    return out;
}

} // namespace hhs::pass220::i087
#endif
