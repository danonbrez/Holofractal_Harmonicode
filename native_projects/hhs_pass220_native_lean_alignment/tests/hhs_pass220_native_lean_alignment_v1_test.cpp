#include "hhs_pass220_native_lean_alignment_v1.hpp"

#include <cassert>
#include <string>

int main() {
    using namespace hhs::alignment;

    const std::string h72(72U, 'a');
    const std::string h216(216U, 'b');
    const NativeLeanProofReceiptV1 proof(true, true, true, h72, h72, h216);
    assert(proof.admitted());

    const NativeAlignmentWitnessV1 admitted(
        PhaseV1::plus_i,
        AuthorityV1::auth,
        PhaseV1::minus_i,
        AuthorityV1::derived,
        true,
        LexicalRelationV1::synonym,
        LexicalGeometryV1::direct_pair,
        true,
        true,
        false,
        true,
        true,
        true,
        true,
        true,
        "0",
        "0",
        true,
        true,
        false,
        proof);
    assert(admitted.canonical());
    assert(admitted.state() == TensorStateV1::genesis);

    const NativeAlignmentWitnessV1 bad_mirror(
        PhaseV1::plus_i,
        AuthorityV1::auth,
        PhaseV1::minus_i,
        AuthorityV1::derived,
        true,
        LexicalRelationV1::synonym,
        LexicalGeometryV1::direct_pair,
        true,
        true,
        false,
        true,
        true,
        false,
        true,
        true,
        "0",
        "0",
        true,
        true,
        false,
        proof);
    assert(!bad_mirror.canonical());
    assert(bad_mirror.state() == TensorStateV1::bottom);

    const NativeAlignmentWitnessV1 bad_delta(
        PhaseV1::plus_i,
        AuthorityV1::auth,
        PhaseV1::minus_i,
        AuthorityV1::derived,
        true,
        LexicalRelationV1::antonym,
        LexicalGeometryV1::reciprocal_ratios,
        true,
        true,
        true,
        true,
        true,
        true,
        true,
        true,
        "1",
        "0",
        true,
        true,
        false,
        proof);
    assert(!bad_delta.canonical());

    const NativeAlignmentWitnessV1 bad_geometry(
        PhaseV1::plus_i,
        AuthorityV1::auth,
        PhaseV1::minus_i,
        AuthorityV1::derived,
        true,
        LexicalRelationV1::antonym,
        LexicalGeometryV1::direct_pair,
        true,
        true,
        true,
        true,
        true,
        true,
        true,
        true,
        "0",
        "0",
        true,
        true,
        false,
        proof);
    assert(!bad_geometry.lexical_admitted());

    assert(!NativeAlignmentWitnessV1::response_free_state_admitted());
    assert(!NativeAlignmentWitnessV1::vm81_mutation_authority());
    assert(!NativeAlignmentWitnessV1::hash72_commit_authority());
    assert(!NativeAlignmentWitnessV1::hash216_persistence_authority());
    return 0;
}
