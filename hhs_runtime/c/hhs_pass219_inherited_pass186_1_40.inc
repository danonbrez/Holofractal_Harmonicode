#include "../include/hhs_pass219_inherited_pass186_1_40.h"

#include <stddef.h>
#include <string.h>

static const char P186_I140_IMPLEMENTATION_COMMIT[] = "fd42056c22071d290945b02efe3a5752aaa3d737";
static const char P186_I140_FROZEN_I139[] = "e5ce3529fcdd7c214aeda8b09f3b7b2bff08b8c4";
static const char P186_I140_CONTRACT_BLOB[] = "41e2e92393ad0bb08b876cf4ca09992a0baf8779";
static const char P186_I140_RECEIPT_BLOB[] = "0f8f4b9a92d3c3267361d530e91ccfe661aef4e4";
static const char P186_I140_MAKEFILE_BLOB[] = "da4153d6468a46da13989195c57da6cc26fb684f";
static const char P186_I140_ABI_HEADER_BLOB[] = "37ce8eafaa1beb4614e6ab41e2cd5b0904bb0376";
static const char P186_I140_ABI_SOURCE_BLOB[] = "a4e7099b266569c6b9db8e68b03b741f58d32a5f";
static const char P186_I140_REGISTER_BLOB[] = "7ee997d3f6126d04d48988498b83f7e488ead20c";
static const char P186_I140_SMOKE_BLOB[] = "d53860ad314000cda7c75462f7c8122a1d492cb1";
static const char P186_I140_FROZEN_PASS187_HEADER_BLOB[] = "e59603ac523dd32e845b21492fc3d2336a562dcf";

static uint32_t p186_i140_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS186_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS186_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS186_VERSION_PATCH;
}

static int p186_i140_git(
    const char value[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS186_I140_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS186_I140_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass186_version(void) {
    return p186_i140_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass186_cumulative_authority(
    const HHSExactPass186CumulativeAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass186BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != p186_i140_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->contract_preserved != 1U ||
        witness->implementation_commit_preserved != 1U ||
        witness->exact_q144_verified != 1U ||
        witness->factorial7_boundary_verified != 1U ||
        witness->vm81_crosswalk_verified != 1U ||
        witness->hydrated_roundtrip_states != HHS186_HYDRATED_STATES ||
        witness->ordered_noncommutative_identity_verified != 1U ||
        witness->x86_64_register_probe_verified != 1U ||
        witness->no_float_disassembly_verified != 1U ||
        witness->pass187_successor_preserved != 1U ||
        witness->independent_opcode_authority != 0U ||
        witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_clock != 0U ||
        witness->float_canonical_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p186_i140_git(witness->pass186_implementation_commit, P186_I140_IMPLEMENTATION_COMMIT) ||
        !p186_i140_git(witness->frozen_i139_commit, P186_I140_FROZEN_I139) ||
        !p186_i140_git(witness->contract_blob, P186_I140_CONTRACT_BLOB) ||
        !p186_i140_git(witness->receipt_blob, P186_I140_RECEIPT_BLOB) ||
        !p186_i140_git(witness->makefile_blob, P186_I140_MAKEFILE_BLOB) ||
        !p186_i140_git(witness->abi_header_blob, P186_I140_ABI_HEADER_BLOB) ||
        !p186_i140_git(witness->abi_source_blob, P186_I140_ABI_SOURCE_BLOB) ||
        !p186_i140_git(witness->register_probe_blob, P186_I140_REGISTER_BLOB) ||
        !p186_i140_git(witness->smoke_test_blob, P186_I140_SMOKE_BLOB) ||
        !p186_i140_git(witness->frozen_pass187_header_blob, P186_I140_FROZEN_PASS187_HEADER_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p186_i140_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS186_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_abi_bound = 1U;
    out_binding->exact_q144_bound = 1U;
    out_binding->factorial7_boundary_bound = 1U;
    out_binding->vm81_crosswalk_bound = 1U;
    out_binding->hydrated_projection_bound = 1U;
    out_binding->hydrated_roundtrip_states = HHS186_HYDRATED_STATES;
    out_binding->ordered_noncommutative_identity_bound = 1U;
    out_binding->x86_64_register_mapping_bound = 1U;
    out_binding->no_float_canonical_bound = 1U;
    out_binding->pass187_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    memcpy(out_binding->pass186_implementation_commit, P186_I140_IMPLEMENTATION_COMMIT,
           HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i139_commit, P186_I140_FROZEN_I139,
           HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
