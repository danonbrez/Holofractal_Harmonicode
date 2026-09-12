#include "hhs_runtime_exact_abi.h"

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

struct UQCELOwners final {
    std::uint8_t P{4U};
    std::uint8_t p{3U};
    std::uint8_t q{5U};
    std::uint8_t delta{1U};
    std::uint8_t A{16U};
    std::uint8_t B{16U};
};

static HHSExactBigUIntView view_of(const std::uint8_t* value) noexcept {
    HHSExactBigUIntView view{};
    view.struct_size = static_cast<std::uint32_t>(sizeof(view));
    view.byte_length = 1U;
    view.bytes_be = value;
    return view;
}

static bool frame_is_zero(const HHSExactVM81Frame& frame) noexcept {
    HHSExactVM81Frame zero{};
    return std::memcmp(&frame, &zero, sizeof(frame)) == 0;
}

static bool frames_equal(
    const HHSExactVM81Frame& left,
    const HHSExactVM81Frame& right
) noexcept {
    return std::memcmp(&left, &right, sizeof(left)) == 0;
}

static bool install_root_key() {
    std::string hex;
    hex.reserve(HHS_EXACT_PASS219_VM81_PQC_KEY_HEX_CHARS);
    static constexpr char digits[] = "0123456789abcdef";
    for (std::size_t i = 0U; i < HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES; ++i) {
        const std::uint8_t value = static_cast<std::uint8_t>(i + 1U);
        hex.push_back(digits[(value >> 4U) & 0x0FU]);
        hex.push_back(digits[value & 0x0FU]);
    }
    return setenv(HHS_EXACT_PASS219_VM81_PQC_KEY_ENV, hex.c_str(), 1) == 0;
}

static HHSExactVM81Frame build_candidate() noexcept {
    HHSExactVM81Frame frame{};
    for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x0102030405060708) ^ static_cast<std::uint64_t>(i);
    return frame;
}

static HHSExactStatus build_input(
    UQCELOwners& owners,
    const HHSExactPass219Hash216TransitionViewV1& parent,
    HHSExactUQCELInputV1& input
) noexcept {
    input = HHSExactUQCELInputV1{};
    input.struct_size = static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.P = view_of(&owners.P);
    input.p = view_of(&owners.p);
    input.q = view_of(&owners.q);
    input.delta = view_of(&owners.delta);
    input.A = view_of(&owners.A);
    input.B = view_of(&owners.B);
    input.cell81 = 41U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    HHSExactStatus status = hhs_exact_uqcel_source_sha256(input.source_envelope_sha256);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    std::memcpy(
        input.previous_hash72,
        parent.receipt_hash72,
        HHS_EXACT_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

static int run_signed(
    std::uint32_t algorithm,
    bool invalid_constraint
) {
    CHECK(install_root_key());
    CHECK(hhs_exact_pass219_vm81_environment_version() ==
          HHS_EXACT_PASS219_VM81_ENV_VERSION);

    HHSExactPass219Hash216TransitionViewV1 parent{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) ==
          HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&parent) ==
          HHS_EXACT_STATUS_OK);

    UQCELOwners owners{};
    if (invalid_constraint)
        owners.delta = 2U;
    HHSExactUQCELInputV1 input{};
    CHECK(build_input(owners, parent, input) == HHS_EXACT_STATUS_OK);
    const HHSExactVM81Frame candidate = build_candidate();

    HHSExactVM81Frame committed{};
    HHSExactPass219RNAAdmissionV1 admission{};
    HHSExactPass219VM81PQCFirewallReceiptV1 firewall{};
    HHSExactPass219VM81PQCSignatureReceiptV1 signature{};
    HHSExactPass219VM81EnvironmentReceiptV1 environment{};

    const bool provider_available =
        hhs_exact_pass219_vm81_pqc_signature_provider_available(algorithm) == 1U;
    const HHSExactStatus status = hhs_exact_pass219_vm81_environment_admit_signed(
        220U,
        algorithm,
        &input,
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

    CHECK(environment.struct_size == sizeof(environment));
    CHECK(environment.version == HHS_EXACT_PASS219_VM81_ENV_VERSION);
    CHECK(environment.security_epoch == HHS_EXACT_PASS219_VM81_ENV_SECURITY_EPOCH);
    CHECK(environment.recovery_candidate_only == 1U);
    CHECK(environment.canonical_mutation_authority == 0U);
    CHECK(environment.canonical_receipt_authority == 0U);
    CHECK(signature.struct_size == sizeof(signature));
    CHECK(signature.version == HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION);
    CHECK(signature.algorithm == algorithm);
    CHECK(signature.external_key_authority == 0U);
    CHECK(signature.external_signature_authority == 0U);
    CHECK(signature.signature_is_canonical_receipt == 0U);

    if (!provider_available) {
        CHECK(status == HHS_EXACT_STATUS_INVARIANT_FAILURE);
        CHECK(environment.state == HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN);
        CHECK(environment.decision == HHS_EXACT_PASS219_VM81_ENV_DECISION_FROZEN);
        CHECK(environment.reason == HHS_EXACT_PASS219_VM81_ENV_REASON_ENVIRONMENT_SIGNATURE);
        CHECK(environment.environment_signature_verified == 0U);
        CHECK(firewall.decision == HHS_EXACT_PASS219_VM81_PQC_DECISION_HALTED);
        CHECK(firewall.halt_reason ==
              HHS_EXACT_PASS219_VM81_PQC_HALT_ENVIRONMENT_DIVERGENCE);
        CHECK(firewall.inherited_rna_authority_invoked == 0U);
        CHECK(frame_is_zero(committed));
        std::printf("PQC_PROVIDER_UNAVAILABLE_FAIL_CLOSED algorithm=%u\n", algorithm);
        return 0;
    }

    CHECK(environment.state == HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING);
    CHECK(environment.decision == HHS_EXACT_PASS219_VM81_ENV_DECISION_READY);
    CHECK(environment.reason == HHS_EXACT_PASS219_VM81_ENV_REASON_NONE);
    CHECK(environment.genesis_verified == 1U);
    CHECK(environment.witness_verified == 1U);
    CHECK(environment.environment_signature_verified == 1U);
    CHECK(environment.witness_sequence >= 1U);

    CHECK(signature.provider_available == 1U);
    CHECK(signature.key_derived_from_kernel_root == 1U);
    CHECK(signature.signature_generated_inside_kernel == 1U);
    CHECK(signature.signature_verified_before_vm81 == 1U);
    CHECK(signature.decision == HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED);
    CHECK(signature.signature_length > 0U);
    CHECK(firewall.pqc_authenticated == 1U);

    if (invalid_constraint) {
        CHECK(status == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
        CHECK(firewall.decision ==
              HHS_EXACT_PASS219_VM81_PQC_DECISION_CANONICAL_REJECTED);
        CHECK(firewall.halted == 0U);
        CHECK(firewall.inherited_rna_authority_invoked == 1U);
        CHECK(frame_is_zero(committed));
        std::printf("PQC_SIGNED_CANONICAL_REJECTION algorithm=%u\n", algorithm);
        return 0;
    }

    CHECK(status == HHS_EXACT_STATUS_OK);
    CHECK(firewall.decision == HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED);
    CHECK(firewall.halted == 0U);
    CHECK(firewall.parent_hash216_verified == 1U);
    CHECK(firewall.child_hash216_verified == 1U);
    CHECK(firewall.rna_cell_wall_routed == 1U);
    CHECK(firewall.inherited_rna_authority_invoked == 1U);
    CHECK(firewall.canonical_receipt_owned_by_inherited_authority == 1U);
    CHECK(firewall.firewall_is_canonical_authority == 0U);
    CHECK(frames_equal(committed, candidate));
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&admission.transition) ==
          HHS_EXACT_STATUS_OK);
    std::printf("PQC_SIGNED_COMMIT algorithm=%u signature_length=%u witness=%llu\n",
                algorithm,
                signature.signature_length,
                static_cast<unsigned long long>(environment.witness_sequence));
    return 0;
}

static int run_bad_profile() {
    CHECK(install_root_key());
    HHSExactPass219Hash216TransitionViewV1 parent{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) ==
          HHS_EXACT_STATUS_OK);
    UQCELOwners owners{};
    HHSExactUQCELInputV1 input{};
    CHECK(build_input(owners, parent, input) == HHS_EXACT_STATUS_OK);
    HHSExactVM81Frame candidate = build_candidate();
    HHSExactVM81Frame committed{};
    HHSExactPass219RNAAdmissionV1 admission{};
    HHSExactPass219VM81PQCFirewallReceiptV1 firewall{};
    HHSExactPass219VM81PQCSignatureReceiptV1 signature{};
    HHSExactPass219VM81EnvironmentReceiptV1 environment{};

    CHECK(hhs_exact_pass219_vm81_environment_admit_signed(
              220U, 99U, &input, &candidate, &parent,
              0, 0U, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              &committed, &admission, &firewall, &signature, &environment) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(firewall.decision == HHS_EXACT_PASS219_VM81_PQC_DECISION_HALTED);
    CHECK(firewall.inherited_rna_authority_invoked == 0U);
    CHECK(environment.decision == HHS_EXACT_PASS219_VM81_ENV_DECISION_FROZEN);
    CHECK(frame_is_zero(committed));
    return 0;
}

static int run_bad_parent() {
    CHECK(install_root_key());
    HHSExactPass219Hash216TransitionViewV1 parent{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) ==
          HHS_EXACT_STATUS_OK);
    UQCELOwners owners{};
    HHSExactUQCELInputV1 input{};
    CHECK(build_input(owners, parent, input) == HHS_EXACT_STATUS_OK);
    parent.occurrences[83].sha256_index_record[9] ^= UINT8_C(0x01);

    HHSExactVM81Frame candidate = build_candidate();
    HHSExactVM81Frame committed{};
    HHSExactPass219RNAAdmissionV1 admission{};
    HHSExactPass219VM81PQCFirewallReceiptV1 firewall{};
    HHSExactPass219VM81PQCSignatureReceiptV1 signature{};
    HHSExactPass219VM81EnvironmentReceiptV1 environment{};

    CHECK(hhs_exact_pass219_vm81_environment_admit_signed(
              220U,
              HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65,
              &input, &candidate, &parent,
              0, 0U, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              &committed, &admission, &firewall, &signature, &environment) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(firewall.halt_reason ==
          HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_HASH216_REFERENCE ||
          firewall.halt_reason == HHS_EXACT_PASS219_VM81_PQC_HALT_ENVIRONMENT_DIVERGENCE);
    CHECK(firewall.inherited_rna_authority_invoked == 0U);
    CHECK(frame_is_zero(committed));
    return 0;
}

int main(int argc, char** argv) {
    CHECK(hhs_exact_pass219_vm81_pqc_signature_version() ==
          HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION);
    CHECK(hhs_exact_pass219_vm81_environment_version() ==
          HHS_EXACT_PASS219_VM81_ENV_VERSION);
    if (argc != 2) {
        std::fprintf(stderr, "mode required\n");
        return 2;
    }
    const std::string mode(argv[1]);
    if (mode == "ml")
        return run_signed(
            HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65, false);
    if (mode == "slh")
        return run_signed(
            HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_SLH_DSA_SHA2_192S, false);
    if (mode == "constraint")
        return run_signed(
            HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65, true);
    if (mode == "bad-profile")
        return run_bad_profile();
    if (mode == "bad-parent")
        return run_bad_parent();
    std::fprintf(stderr, "unknown mode: %s\n", argv[1]);
    return 2;
}
