#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdio.h>

int main(void) {
    HHSExactPass219H36DefaultBindingV1 b;

    assert(HHS_EXACT_PASS219_H36_FRAME_BITS == 5184U);
    assert(HHS_EXACT_PASS219_H36_WORD_COUNT * HHS_EXACT_PASS219_H36_WORD_BITS == 5184U);
    assert(HHS_EXACT_VM81_CELLS * HHS_EXACT_PASS219_H36_RULE_COUNT == 5184U);

    assert(hhs_exact_pass219_h36_default_binding(&b) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_default_binding_validate(&b) == HHS_EXACT_STATUS_OK);

    assert(b.default_state_machine_required == 1U);
    assert(b.hydration_required == 1U);
    assert(b.compression_required == 1U);
    assert(b.phase_gear_required == 1U);
    assert(b.gpu_candidate_path_required == 1U);
    assert(b.hash216_vector_cache_required == 1U);
    assert(b.knowledge_graph_required == 1U);
    assert(b.quantum_like_branch_required == 1U);
    assert(b.rna_dna_transcription_required == 1U);
    assert(b.octonion_ternary_required == 1U);
    assert(b.loshu_sudoku_qudit_required == 1U);
    assert(b.native_36bit_execution_required == 1U);
    assert(b.multimodal_generalization_required == 1U);

    assert(b.singleton_vm81_authority_preserved == 1U);
    assert(b.independent_vm81_authority == 0U);
    assert(b.independent_hash72_authority == 0U);
    assert(b.independent_hash216_authority == 0U);
    assert(b.floating_point_canonical_authority == 0U);

    b.hydration_required = 0U;
    assert(hhs_exact_pass219_h36_default_binding_validate(&b) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    puts("PASS219 Harmonic36 mandatory default binding: PASS");
    return 0;
}
