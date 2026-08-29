#include "hhs_pass219_inherited_pass186_1_40.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass186CumulativeAuthorityWitnessV1 witness() {
    HHSExactPass186CumulativeAuthorityWitnessV1 w{};
    w.struct_size = sizeof(w);
    w.version = hhs::rna::InheritedPass186X64VM81Q144Authority::version();
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

    std::strcpy(w.pass186_implementation_commit, "fd42056c22071d290945b02efe3a5752aaa3d737");
    std::strcpy(w.frozen_i139_commit, "e5ce3529fcdd7c214aeda8b09f3b7b2bff08b8c4");
    std::strcpy(w.contract_blob, "41e2e92393ad0bb08b876cf4ca09992a0baf8779");
    std::strcpy(w.receipt_blob, "0f8f4b9a92d3c3267361d530e91ccfe661aef4e4");
    std::strcpy(w.makefile_blob, "da4153d6468a46da13989195c57da6cc26fb684f");
    std::strcpy(w.abi_header_blob, "37ce8eafaa1beb4614e6ab41e2cd5b0904bb0376");
    std::strcpy(w.abi_source_blob, "a4e7099b266569c6b9db8e68b03b741f58d32a5f");
    std::strcpy(w.register_probe_blob, "7ee997d3f6126d04d48988498b83f7e488ead20c");
    std::strcpy(w.smoke_test_blob, "d53860ad314000cda7c75462f7c8122a1d492cb1");
    std::strcpy(w.frozen_pass187_header_blob, "e59603ac523dd32e845b21492fc3d2336a562dcf");
    return w;
}

int main() {
    using hhs::rna::InheritedPass186X64VM81Q144Authority;
    auto w = witness();
    HHSExactPass219InheritedPass186BindingV1 b{};
    assert(InheritedPass186X64VM81Q144Authority::bind(w, b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 186U);
    assert(b.historical_abi_bound == 1U);
    assert(b.ordered_noncommutative_identity_bound == 1U);
    assert(b.pass187_successor_bound == 1U);
    assert(b.no_new_authority_bound == 1U);

    HHS186Quantization q{};
    q.struct_size = sizeof(q);
    q.abi_version = HHS186_ABI_VERSION;
    q.opcode_lane36 = 35U;
    q.root_row12 = 11U;
    q.root_col12 = 11U;
    q.g243 = 242U;
    HHS186MappingResult r{};
    assert(hhs186_x64_vm81_q144_map(2, 3, 5, 7, &q, &r) == HHS186_STATUS_OK);
    assert(r.instruction_state5184 == 5183U);
    assert(r.projected_state5184_243 == HHS186_HYDRATED_STATES - 1U);
    assert(r.closure_q144_lane == 1U);

    static_assert(!InheritedPass186X64VM81Q144Authority::candidate_authority());
    static_assert(!InheritedPass186X64VM81Q144Authority::mutation_authority());
    static_assert(!InheritedPass186X64VM81Q144Authority::persistence_authority());
    static_assert(!InheritedPass186X64VM81Q144Authority::hash72_clock_authority());
    static_assert(!InheritedPass186X64VM81Q144Authority::vm81_mutation_authority());
    static_assert(!InheritedPass186X64VM81Q144Authority::independent_opcode_authority());
    static_assert(!InheritedPass186X64VM81Q144Authority::floating_point_canonical_authority());
    static_assert(InheritedPass186X64VM81Q144Authority::singleton_vm81_authority_remains_inherited());
    static_assert(!InheritedPass186X64VM81Q144Authority::ordered_product_witness_is_identity());
    static_assert(InheritedPass186X64VM81Q144Authority::ordered_basis_tag_is_identity());
    static_assert(InheritedPass186X64VM81Q144Authority::historical_pass186_runtime_reused());
    static_assert(InheritedPass186X64VM81Q144Authority::pass187_successor_preserved());
    return 0;
}
