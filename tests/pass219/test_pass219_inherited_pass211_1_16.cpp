#include "hhs_pass219_inherited_pass211_1_16.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass211BigIntHFCWitnessV1 valid_witness() {
    HHSExactPass211BigIntHFCWitnessV1 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
    w.version = hhs_exact_pass219_inherited_pass211_version();
    w.runtime_verified = 1U;
    w.hfc_register_boolean_cells = 5184U;
    w.packed_shard_bytes = 648U;
    w.snapshot_count = 36U;
    w.snapshot_width = 288U;
    w.snapshot_stride = 144U;
    w.maximum_shards = 4096U;
    w.pass133_corpus_roundtrips = 11U;
    w.pass133_single_bit_corrections = 512U;
    w.fitting_package_count = 4U;
    w.fitting_erasure_recoveries = 144U;
    w.anchored_corruption_cell = 1000U;
    w.multiregister_source_bits = 1024U;
    w.multiregister_carrier_bytes = 811U;
    w.multiregister_shard_count = 2U;
    w.multiregister_first_shard_bytes = 648U;
    w.multiregister_final_shard_bytes = 163U;
    w.deterministic_replay_verified = 1U;
    w.strict_claim_boundary_preserved = 1U;
    w.historical_integrity_requires_minted_anchor = 1U;
    w.missing_duplicate_reorder_substitution_fail_closed = 1U;
    w.zero_negative_fail_closed = 1U;
    w.no_float_canonical_authority = 1U;
    w.required_operation_count = HHS_EXACT_PASS211_REQUIRED_OPERATION_COUNT;
    w.pass212_contract_inherits_pass211 = 1U;
    w.branch_validation_run = 31005616936ULL;
    w.main_validation_run = 31005763191ULL;
    std::strcpy(w.validated_branch_head, "5c877eeae86e1fd929e30a2c418f705f12921265");
    std::strcpy(w.main_merge_head, "b80759e60bd78357d9d650aa23c99460f3952fd3");
    std::strcpy(w.contract_git_blob, "685c6d1544cbae6966e84c0d05b6bf4b8687d903");
    std::strcpy(w.restart_git_blob, "7065102a60501c797407fe7a40cdf760ab6a11b3");
    std::strcpy(w.runtime_git_blob, "0d11f3607c81b442b76dcd455b5c47450c9ed7e9");
    std::strcpy(w.api_git_blob, "a3df09c2593fc0c3d1c331b103b86826cb1a7084");
    std::strcpy(w.evidence_git_blob, "fa8807d66a28a5e38c0294cdac34e214dc39a8b6");
    std::strcpy(w.validation_script_git_blob, "4ae19dab0dd9d0b70398b6b433f92e799a6baf38");
    std::strcpy(w.pass212_contract_git_blob, "12f2c577e02f4436ee776366a1994ece5a765fca");
    std::strcpy(w.deterministic_package_root216, "2a87ecd5755a5bd22801b0b4f528b5edfbd442c8616f1bfde2a204d652ecdee2");
    std::strcpy(w.multiregister_package_root216, "b5b1e92df89a9422a7367b166c32c9362848573a065be3d2192981a4da4d1234");
    std::strcpy(w.deterministic_package_receipt_hash72, "m8h4vJSUoQ38FH8Ogr0B7xot1TwI9BA2KiCjwyyEzTz1ZfEUeQQwRLgswPeHvc>Fvk8zOYO-");
    return w;
}

int main() {
    auto witness = valid_witness();
    hhs::rna::InheritedPass211BigIntHFCCarrier membrane(witness);
    assert(membrane.status() == HHS_EXACT_STATUS_OK);
    assert(membrane.wired());
    const auto& record = membrane.record();
    assert(record.pass_number == 211U);
    assert(record.pass219_new_canonical_mutation_authority == 0U);
    assert(record.cxx_mutation_authority == 0U);
    assert(record.vm81_mutation_authority == 0U);
    return 0;
}
