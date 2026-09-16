#define _POSIX_C_SOURCE 200809L

#include "hhs_pass219_vm81_environmental_recovery_1_32.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HHS_PROBE_CASE_COMMIT 0U
#define HHS_PROBE_CASE_CONSTRAINT 1U
#define HHS_PROBE_CASE_BAD_PARENT 2U
#define HHS_PROBE_CASE_MISSING_INPUT 3U
#define HHS_PROBE_CASE_BAD_PASS 4U

static int fail(const char *message) {
    fprintf(stderr, "%s\n", message);
    return 1;
}

static int install_root_key(void) {
    char hex[HHS_EXACT_PASS219_VM81_PQC_KEY_HEX_CHARS + 1U];
    static const char digits[] = "0123456789abcdef";
    size_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES; ++i) {
        const uint8_t value = (uint8_t)(i + 1U);
        hex[2U * i] = digits[(value >> 4U) & 0x0FU];
        hex[2U * i + 1U] = digits[value & 0x0FU];
    }
    hex[HHS_EXACT_PASS219_VM81_PQC_KEY_HEX_CHARS] = '\0';
    return setenv(HHS_EXACT_PASS219_VM81_PQC_KEY_ENV, hex, 1) == 0;
}

static HHSExactBigUIntView view_of(const uint8_t *value) {
    HHSExactBigUIntView view;
    memset(&view, 0, sizeof(view));
    view.struct_size = (uint32_t)sizeof(view);
    view.byte_length = 1U;
    view.bytes_be = value;
    return view;
}

static int frame_is_zero(const HHSExactVM81Frame *frame) {
    HHSExactVM81Frame zero;
    if (frame == NULL)
        return 0;
    memset(&zero, 0, sizeof(zero));
    return memcmp(frame, &zero, sizeof(zero)) == 0;
}

static int read_raw_frame(const char *path, uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES]) {
    FILE *stream;
    size_t count;
    int trailing;
    if (path == NULL || raw == NULL)
        return 0;
    stream = fopen(path, "rb");
    if (stream == NULL)
        return 0;
    count = fread(raw, 1U, HHS_EXACT_VM81_FRAME_BYTES, stream);
    trailing = fgetc(stream);
    fclose(stream);
    return count == HHS_EXACT_VM81_FRAME_BYTES && trailing == EOF;
}

static int write_frame(const char *path, const HHSExactVM81Frame *frame) {
    uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES];
    size_t written = 0U;
    FILE *stream;
    if (path == NULL || frame == NULL)
        return 0;
    if (hhs_exact_vm81_frame_export_le(
            frame, raw, sizeof(raw), &written) != HHS_EXACT_STATUS_OK ||
        written != sizeof(raw))
        return 0;
    stream = fopen(path, "wb");
    if (stream == NULL)
        return 0;
    written = fwrite(raw, 1U, sizeof(raw), stream);
    if (fclose(stream) != 0)
        return 0;
    return written == sizeof(raw);
}

static int build_input(
    HHSExactUQCELInputV1 *input,
    const HHSExactPass219Hash216TransitionViewV1 *parent,
    const uint8_t *P,
    const uint8_t *p,
    const uint8_t *q,
    const uint8_t *delta,
    const uint8_t *A,
    const uint8_t *B
) {
    if (input == NULL || parent == NULL || P == NULL || p == NULL || q == NULL ||
        delta == NULL || A == NULL || B == NULL)
        return 0;
    memset(input, 0, sizeof(*input));
    input->struct_size = (uint32_t)sizeof(*input);
    input->uqcel_version = hhs_exact_uqcel_version();
    input->profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input->P = view_of(P);
    input->p = view_of(p);
    input->q = view_of(q);
    input->delta = view_of(delta);
    input->A = view_of(A);
    input->B = view_of(B);
    input->cell81 = 41U;
    input->left_basis8 = HHS_EXACT_PHASE_X;
    input->right_basis8 = HHS_EXACT_PHASE_Y;
    if (hhs_exact_uqcel_source_sha256(input->source_envelope_sha256) != HHS_EXACT_STATUS_OK)
        return 0;
    memcpy(input->previous_hash72, parent->receipt_hash72, HHS_EXACT_HASH72_STRLEN);
    return 1;
}

static uint32_t parse_mode(const char *mode) {
    if (mode == NULL)
        return UINT32_MAX;
    if (strcmp(mode, "commit") == 0)
        return HHS_PROBE_CASE_COMMIT;
    if (strcmp(mode, "constraint") == 0)
        return HHS_PROBE_CASE_CONSTRAINT;
    if (strcmp(mode, "bad-parent") == 0)
        return HHS_PROBE_CASE_BAD_PARENT;
    if (strcmp(mode, "missing-input") == 0)
        return HHS_PROBE_CASE_MISSING_INPUT;
    if (strcmp(mode, "bad-pass") == 0)
        return HHS_PROBE_CASE_BAD_PASS;
    return UINT32_MAX;
}

int main(int argc, char **argv) {
    uint32_t probe_case;
    uint32_t pass_number = 220U;
    const uint32_t algorithm = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65;
    uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES];
    HHSExactVM81Frame candidate;
    HHSExactVM81Frame committed;
    HHSExactPass219Hash216TransitionViewV1 parent;
    HHSExactUQCELInputV1 input;
    HHSExactPass219RNAAdmissionV1 admission;
    HHSExactPass219VM81PQCFirewallReceiptV1 firewall;
    HHSExactPass219VM81PQCSignatureReceiptV1 signature;
    HHSExactPass219VM81EnvironmentReceiptV1 environment;
    HHSExactStatus status;
    uint8_t P = 4U;
    uint8_t p = 3U;
    uint8_t q = 5U;
    uint8_t delta = 1U;
    uint8_t A = 16U;
    uint8_t B = 16U;
    const HHSExactUQCELInputV1 *input_ptr;
    int committed_exact;
    int transition_verified;
    int child_identity_matches;
    int canonical_receipt_minted;
    int authority_handoff_exact;
    int signature_verified;
    int environment_verified;
    int provider_available;

    if (argc != 4)
        return fail("USAGE:test_pass219_bigint_environment_admission_native_probe <mode> <raw648> <out648>");
    probe_case = parse_mode(argv[1]);
    if (probe_case == UINT32_MAX)
        return fail("UNKNOWN_MODE");
    if (!read_raw_frame(argv[2], raw))
        return fail("RAW_FRAME_MUST_BE_EXACTLY_648_BYTES");
    if (!install_root_key())
        return fail("ROOT_KEY_INSTALL_FAILED");

    provider_available =
        hhs_exact_pass219_vm81_pqc_signature_provider_available(algorithm) == 1U;
    if (!provider_available)
        return fail("ML_DSA_65_PROVIDER_REQUIRED");

    memset(&candidate, 0, sizeof(candidate));
    if (hhs_exact_vm81_frame_import_le(raw, sizeof(raw), &candidate) != HHS_EXACT_STATUS_OK)
        return fail("VM81_IMPORT_FAILED");

    memset(&parent, 0, sizeof(parent));
    if (hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&parent) != HHS_EXACT_STATUS_OK)
        return fail("GENESIS_HASH216_REFERENCE_FAILED");

    if (probe_case == HHS_PROBE_CASE_CONSTRAINT)
        delta = 2U;
    if (!build_input(&input, &parent, &P, &p, &q, &delta, &A, &B))
        return fail("UQCEL_INPUT_BUILD_FAILED");
    if (probe_case == HHS_PROBE_CASE_BAD_PARENT)
        parent.occurrences[83].sha256_index_record[9] ^= UINT8_C(0x01);
    if (probe_case == HHS_PROBE_CASE_BAD_PASS)
        pass_number = 219U;
    input_ptr = probe_case == HHS_PROBE_CASE_MISSING_INPUT ? NULL : &input;

    memset(&committed, 0, sizeof(committed));
    memset(&admission, 0, sizeof(admission));
    memset(&firewall, 0, sizeof(firewall));
    memset(&signature, 0, sizeof(signature));
    memset(&environment, 0, sizeof(environment));

    status = hhs_exact_pass219_vm81_environment_admit_signed(
        pass_number,
        algorithm,
        input_ptr,
        &candidate,
        &parent,
        0,
        0U,
        HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
        0,
        &committed,
        &admission,
        &firewall,
        &signature,
        &environment);

    if (!write_frame(argv[3], &committed))
        return fail("COMMITTED_FRAME_WRITE_FAILED");

    committed_exact = memcmp(&candidate, &committed, sizeof(candidate)) == 0;
    transition_verified =
        status == HHS_EXACT_STATUS_OK &&
        hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&admission.transition) == HHS_EXACT_STATUS_OK;
    child_identity_matches =
        status == HHS_EXACT_STATUS_OK &&
        memcmp(
            firewall.child_hash216_identity,
            admission.transition.transition_identity216,
            HHS_EXACT_UQCEL_HASH216_STRLEN) == 0;
    canonical_receipt_minted =
        firewall.canonical_receipt_owned_by_inherited_authority == 1U;
    signature_verified =
        signature.provider_available == 1U &&
        signature.key_derived_from_kernel_root == 1U &&
        signature.signature_generated_inside_kernel == 1U &&
        signature.signature_verified_before_vm81 == 1U &&
        signature.decision == HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED &&
        signature.signature_is_canonical_receipt == 0U;
    environment_verified =
        environment.state == HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING &&
        environment.decision == HHS_EXACT_PASS219_VM81_ENV_DECISION_READY &&
        environment.reason == HHS_EXACT_PASS219_VM81_ENV_REASON_NONE &&
        environment.genesis_verified == 1U &&
        environment.witness_verified == 1U &&
        environment.environment_signature_verified == 1U &&
        environment.recovery_candidate_only == 1U &&
        environment.canonical_mutation_authority == 0U &&
        environment.canonical_receipt_authority == 0U;
    authority_handoff_exact =
        firewall.firewall_is_canonical_authority == 0U &&
        environment.canonical_mutation_authority == 0U &&
        environment.canonical_receipt_authority == 0U &&
        signature.external_key_authority == 0U &&
        signature.external_signature_authority == 0U &&
        signature.signature_is_canonical_receipt == 0U;

    if (probe_case == HHS_PROBE_CASE_COMMIT) {
        if (status != HHS_EXACT_STATUS_OK || !committed_exact ||
            firewall.decision != HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED ||
            firewall.halted != 0U || firewall.parent_hash216_verified != 1U ||
            firewall.child_hash216_verified != 1U || firewall.rna_cell_wall_routed != 1U ||
            firewall.pqc_authenticated != 1U || firewall.inherited_rna_authority_invoked != 1U ||
            !canonical_receipt_minted || !transition_verified || !child_identity_matches ||
            !signature_verified || !environment_verified || !authority_handoff_exact)
            return fail("CANONICAL_COMMIT_ASSERTION_FAILED");
    } else {
        if (status == HHS_EXACT_STATUS_OK || !frame_is_zero(&committed) ||
            canonical_receipt_minted || firewall.decision == HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED)
            return fail("NEGATIVE_CASE_FAIL_CLOSED_ASSERTION_FAILED");
        if (probe_case == HHS_PROBE_CASE_CONSTRAINT &&
            (status != HHS_EXACT_STATUS_CONSTRAINT_REJECTED ||
             firewall.decision != HHS_EXACT_PASS219_VM81_PQC_DECISION_CANONICAL_REJECTED ||
             firewall.halted != 0U))
            return fail("CONSTRAINT_REJECTION_ASSERTION_FAILED");
    }

    printf(
        "case=%u status=%u provider_available=%u committed_exact=%u committed_zero=%u "
        "firewall_decision=%u firewall_halted=%u parent_hash216_verified=%u "
        "child_hash216_verified=%u inherited_rna_authority_invoked=%u "
        "canonical_receipt_minted=%u transition_verified=%u child_identity_matches=%u "
        "signature_verified=%u environment_verified=%u authority_handoff_exact=%u "
        "environment_witness_sequence=%llu signature_length=%u\n",
        (unsigned)probe_case,
        (unsigned)status,
        (unsigned)provider_available,
        (unsigned)committed_exact,
        (unsigned)frame_is_zero(&committed),
        (unsigned)firewall.decision,
        (unsigned)firewall.halted,
        (unsigned)firewall.parent_hash216_verified,
        (unsigned)firewall.child_hash216_verified,
        (unsigned)firewall.inherited_rna_authority_invoked,
        (unsigned)canonical_receipt_minted,
        (unsigned)transition_verified,
        (unsigned)child_identity_matches,
        (unsigned)signature_verified,
        (unsigned)environment_verified,
        (unsigned)authority_handoff_exact,
        (unsigned long long)environment.witness_sequence,
        (unsigned)signature.signature_length);
    return 0;
}
