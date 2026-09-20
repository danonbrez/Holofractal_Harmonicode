#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void fill_pattern(uint8_t *buffer, size_t length) {
    size_t i;
    for (i = 0U; i < length; ++i)
        buffer[i] = (uint8_t)((i * 29U + 0x53U) & 0xffU);
}

int main(void) {
    HHSExactPass219Lane5VirtualBIOSDescriptorV1 bios;
    HHSExactPass219CoreCircuitStateV1 state;
    HHSExactPass219CoreCircuitFeaturesV1 features;
    HHSExactPass219CoreCircuitDecisionV1 decision;
    HHSExactPass219Lane5RawX86VM5184ReceiptV1 receipt;
    uint8_t input[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t output[HHS_EXACT_VM81_FRAME_BYTES];
    size_t written = 0U;

    memset(&bios, 0, sizeof(bios));
    assert(hhs_exact_pass219_lane5_virtual_bios_descriptor(&bios) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_lane5_virtual_bios_validate() ==
           HHS_EXACT_STATUS_OK);

    assert(bios.vm81_cells == 81U);
    assert(bios.local_constructor_states == 64U);
    assert(bios.vm5184_bits == 5184U);
    assert(bios.raw_frame_bytes == 648U);
    assert(bios.hydration_lanes == 4U);
    assert(bios.phase_modulus == 72U);

    assert(bios.resident_vm_bios == 1U);
    assert(bios.control_plane_only == 1U);
    assert(bios.payload_dataflow_stage == 0U);
    assert(bios.payload_format_translation == 0U);
    assert(bios.raw_x86_vm5184_kernel_bound == 1U);
    assert(bios.cpp_rna_cell_wall_bound == 1U);
    assert(bios.pqc_firewall_bound == 1U);
    assert(bios.four_lane_hydration_bound == 1U);
    assert(bios.global_latency_policy_bound == 1U);
    assert(bios.direct_witness_routing_bound == 1U);
    assert(bios.automatic_superedge_routing_bound == 1U);
    assert(bios.unbounded_workload_routing_bound == 1U);
    assert(bios.hash216_validated_jump_cache_bound == 1U);
    assert(bios.candidate_optimization_only == 1U);
    assert(bios.signed_vm81_admission_required == 1U);
    assert(bios.hash72_commit_bypass_allowed == 0U);
    assert(bios.hash216_cache_commit_bypass_allowed == 0U);
    assert(bios.canonical_mutation_authority == 0U);
    assert(bios.floating_point_authority == 0U);

    /*
     * BIOS validation is a control-plane precondition. The payload still takes
     * the exact 1.57 raw kernel path and must emerge byte-identically.
     */
    assert(hhs_exact_pass219_core_circuit_state_init(&state) ==
           HHS_EXACT_STATUS_OK);
    fill_pattern(input, sizeof(input));
    memset(output, 0, sizeof(output));
    memset(&features, 0, sizeof(features));
    memset(&decision, 0, sizeof(decision));
    memset(&receipt, 0, sizeof(receipt));

    assert(hhs_exact_pass219_lane5_raw_x86_vm5184_step(
               input, sizeof(input), 0, &state,
               output, sizeof(output), &written,
               &features, &decision, &receipt) ==
           HHS_EXACT_STATUS_OK);
    assert(written == sizeof(input));
    assert(memcmp(input, output, sizeof(input)) == 0);
    assert(receipt.exact_byte_identity == 1U);
    assert(receipt.direct_vm81_kernel_execution == 1U);

    puts("PASS lane5 virtual BIOS control plane");
    return 0;
}
