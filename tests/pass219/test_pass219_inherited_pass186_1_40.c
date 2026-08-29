#include "hhs_pass219_inherited_pass186_1_40.h"

#include <assert.h>
#include <string.h>

static HHSExactPass186CumulativeAuthorityWitnessV1 witness(void) {
    HHSExactPass186CumulativeAuthorityWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass186_version();
    w.contract_preserved = 1U;
    w.implementation_commit_preserved = 1U;
    w.exact_q144_verified = 1U;
    w.factorial7_boundary_verified = 1U;
    w.vm81_crosswalk_verified = 1U;
    w.hydrated_roundtrip_states = HHS186_HYDRATED_STATES;
    w.ordered_noncommutative_identity_verified = 1U;
    w.x86_64_register_probe_verified = 1U;
    w.no_float_disassembly_verified = 1U;
    w.pass187_successor_preserved = 1U;

    strcpy(w.pass186_implementation_commit, "fd42056c22071d290945b02efe3a5752aaa3d737");
    strcpy(w.frozen_i139_commit, "e5ce3529fcdd7c214aeda8b09f3b7b2bff08b8c4");
    strcpy(w.contract_blob, "41e2e92393ad0bb08b876cf4ca09992a0baf8779");
    strcpy(w.receipt_blob, "0f8f4b9a92d3c3267361d530e91ccfe661aef4e4");
    strcpy(w.makefile_blob, "da4153d6468a46da13989195c57da6cc26fb684f");
    strcpy(w.abi_header_blob, "37ce8eafaa1beb4614e6ab41e2cd5b0904bb0376");
    strcpy(w.abi_source_blob, "a4e7099b266569c6b9db8e68b03b741f58d32a5f");
    strcpy(w.register_probe_blob, "7ee997d3f6126d04d48988498b83f7e488ead20c");
    strcpy(w.smoke_test_blob, "d53860ad314000cda7c75462f7c8122a1d492cb1");
    strcpy(w.frozen_pass187_header_blob, "e59603ac523dd32e845b21492fc3d2336a562dcf");
    return w;
}

int main(void) {
    HHSExactPass186CumulativeAuthorityWitnessV1 w = witness();
    HHSExactPass219InheritedPass186BindingV1 b;
    HHS186Quantization q;
    HHS186MappingResult xy;
    HHS186MappingResult yx;
    HHS186RegisterImage registers;

    assert(hhs_exact_pass219_bind_pass186_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 186U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.historical_abi_bound == 1U);
    assert(b.exact_q144_bound == 1U);
    assert(b.factorial7_boundary_bound == 1U);
    assert(b.vm81_crosswalk_bound == 1U);
    assert(b.hydrated_projection_bound == 1U);
    assert(b.hydrated_roundtrip_states == HHS186_HYDRATED_STATES);
    assert(b.ordered_noncommutative_identity_bound == 1U);
    assert(b.x86_64_register_mapping_bound == 1U);
    assert(b.no_float_canonical_bound == 1U);
    assert(b.pass187_successor_bound == 1U);
    assert(b.no_new_authority_bound == 1U);

    memset(&q, 0, sizeof(q));
    q.struct_size = (uint32_t)sizeof(q);
    q.abi_version = HHS186_ABI_VERSION;
    q.root_col12 = 4U;
    assert(hhs186_x64_vm81_q144_map(2, 3, 5, 7, &q, &xy) == HHS186_STATUS_OK);
    q.root_col12 = 5U;
    assert(hhs186_x64_vm81_q144_map(2, 3, 5, 7, &q, &yx) == HHS186_STATUS_OK);
    assert(xy.ordered_tag == UINT16_C(0x5859));
    assert(yx.ordered_tag == UINT16_C(0x5958));
    assert(xy.ordered_product_witness == yx.ordered_product_witness);
    assert(xy.ordered_tag != yx.ordered_tag);

    memset(&registers, 0, sizeof(registers));
    hhs186_x64_capture_xyzw_registers(11, 13, 17, 19, &registers);
    assert(registers.canonical_r8_x == 11);
    assert(registers.canonical_r9_y == 13);
    assert(registers.canonical_r10_z == 17);
    assert(registers.canonical_r11_w == 19);

    w = witness();
    w.independent_opcode_authority = 1U;
    assert(hhs_exact_pass219_bind_pass186_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.float_canonical_authority = 1U;
    assert(hhs_exact_pass219_bind_pass186_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    strcpy(w.abi_source_blob, "0000000000000000000000000000000000000000");
    assert(hhs_exact_pass219_bind_pass186_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
