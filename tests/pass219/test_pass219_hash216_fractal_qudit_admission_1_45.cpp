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
        frame.words[i] = UINT64_C(0x0F1E2D3C4B5A6978) ^
                         static_cast<std::uint64_t>(i * 37U);
    return frame;
}

static bool frames_equal(
    const HHSExactVM81Frame& left,
    const HHSExactVM81Frame& right
) noexcept {
    return std::memcmp(&left, &right, sizeof(left)) == 0;
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
    std::memcpy(input.previous_hash72, parent.receipt_hash72, HHS_EXACT_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

static HHSExactPass219Hash216FractalQuditWitnessV1 build_witness(
    const HHSExactUQCELInputV1& input
) {
    HHSExactPass219Hash216FractalQuditWitnessV1 witness{};
    std::uint16_t local = 0U;
    if (hhs_exact_vm5184_address_encode(
            input.cell81, input.left_basis8, input.right_basis8, &local) !=
        HHS_EXACT_STATUS_OK)
        std::abort();
    witness.struct_size = static_cast<std::uint32_t>(sizeof(witness));
    witness.version = HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VERSION;
    witness.declared_scope_mask = HHS_EXACT_PASS219_FQ_SCOPE_REQUIRED;
    witness.local5184 = local;
    witness.hash72_major = static_cast<std::uint8_t>(local / 72U);
    witness.hash72_minor = static_cast<std::uint8_t>(local % 72U);
    witness.cell81 = input.cell81;
    witness.operation64 = static_cast<std::uint8_t>(
        input.left_basis8 * HHS_EXACT_PHASE_BASIS_COUNT + input.right_basis8);
    witness.u72_left = 1;
    witness.u72_right = 1;
    witness.xy_plus_zw = 2;
    /* cell 41 -> 41 mod 9 = 5 -> Lo Shu value 7, antipode 3. */
    witness.lo_shu_n = 7U;
    witness.lo_shu_antipode = 3U;
    witness.sigma = 1;
    witness.mass_t = 2;
    witness.mass_x = 1;
    witness.mass_y = 1;
    witness.mass_D = 18;
    witness.mass_N = 324;
    return witness;
}

int main() {
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_admission_version() ==
          HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VERSION);
    CHECK(install_root_key());
    CHECK(hhs_exact_pass219_vm81_pqc_signature_provider_available(
              HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65) == 1U);

    HHSExactPass219Hash216TransitionViewV1 parent{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) ==
          HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&parent) ==
          HHS_EXACT_STATUS_OK);

    UQCELOwners owners{};
    HHSExactUQCELInputV1 input{};
    CHECK(build_input(owners, parent, input) == HHS_EXACT_STATUS_OK);
    const auto witness = build_witness(input);
    CHECK(witness.local5184 == 2625U);
    CHECK(witness.hash72_major == 36U);
    CHECK(witness.hash72_minor == 33U);
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_witness_validate(
              &input, &parent, &witness) == HHS_EXACT_STATUS_OK);

    auto bad_scope = witness;
    bad_scope.declared_scope_mask &= ~HHS_EXACT_PASS219_FQ_SCOPE_MASS_FACTORIZATION;
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_witness_validate(
              &input, &parent, &bad_scope) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    auto bad_local = witness;
    bad_local.hash72_minor = static_cast<std::uint8_t>(bad_local.hash72_minor + 1U);
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_witness_validate(
              &input, &parent, &bad_local) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    auto bad_mass = witness;
    bad_mass.mass_N += 1;
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_witness_validate(
              &input, &parent, &bad_mass) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    auto bad_constructor = witness;
    bad_constructor.xy_plus_zw = 3;
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_witness_validate(
              &input, &parent, &bad_constructor) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    const HHSExactVM81Frame candidate = build_candidate();
    HHSExactVM81Frame committed{};
    HHSExactPass219RNAAdmissionV1 admission{};
    HHSExactPass219VM81PQCFirewallReceiptV1 firewall{};
    HHSExactPass219VM81PQCSignatureReceiptV1 signature{};
    HHSExactPass219VM81EnvironmentReceiptV1 environment{};

    CHECK(hhs_exact_pass219_vm81_environment_admit_signed(
              220U,
              HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65,
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
              &environment) == HHS_EXACT_STATUS_OK);
    CHECK(frames_equal(committed, candidate));
    CHECK(firewall.decision == HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED);
    CHECK(signature.decision == HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED);
    CHECK(environment.decision == HHS_EXACT_PASS219_VM81_ENV_DECISION_READY);

    const HHSExactVM81Frame before_hydration = committed;
    HHSExactPass219Hash216FractalQuditReceiptV1 proof{};
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_hydrate_proof(
              &input,
              &committed,
              &parent,
              &admission,
              &firewall,
              &signature,
              &environment,
              &witness,
              &proof) == HHS_EXACT_STATUS_OK);
    CHECK(frames_equal(committed, before_hydration));
    CHECK(proof.accepted == 1U);
    CHECK(proof.verified_scope_mask == HHS_EXACT_PASS219_FQ_SCOPE_REQUIRED);
    CHECK(proof.failed_scope_mask == 0U);
    CHECK(proof.reason == HHS_EXACT_PASS219_FQ_REASON_NONE);
    CHECK(proof.scaling_closed == 1U);
    CHECK(proof.dual_coordinate_verified == 1U);
    CHECK(proof.pq_window_verified == 1U);
    CHECK(proof.constructor_verified == 1U);
    CHECK(proof.lo_shu_reciprocal_verified == 1U);
    CHECK(proof.mass_factorization_verified == 1U);
    CHECK(proof.parent_hash216_verified == 1U);
    CHECK(proof.child_hash216_verified == 1U);
    CHECK(proof.signed_environment_verified == 1U);
    CHECK(proof.inherited_canonical_admission_verified == 1U);
    CHECK(proof.proof_transition_indexed == 1U);
    CHECK(proof.canonical_vm81_mutation_authority == 0U);
    CHECK(proof.canonical_hash72_authority == 0U);
    CHECK(proof.canonical_hash216_authority == 0U);
    CHECK(proof.canonical_persistence_authority == 0U);
    CHECK(proof.receipt_clock_authority == 0U);
    CHECK(proof.floating_point_canonical_authority == 0U);
    CHECK(proof.witness_signature64 != 0U);
    CHECK(proof.parent_signature64 != 0U);
    CHECK(proof.child_signature64 != 0U);
    CHECK(proof.receipt_signature64 != 0U);
    CHECK(std::memcmp(
              proof.proof_transition.previous_hash72,
              input.previous_hash72,
              HHS_EXACT_HASH72_STRLEN) == 0);
    CHECK(std::memcmp(
              proof.proof_transition.change_hash72,
              proof.witness_hash72,
              HHS_EXACT_HASH72_STRLEN) == 0);
    CHECK(std::memcmp(
              proof.proof_transition.receipt_hash72,
              admission.transition.receipt_hash72,
              HHS_EXACT_HASH72_STRLEN) == 0);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&proof.proof_transition) ==
          HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_receipt_replay(
              &input,
              &committed,
              &parent,
              &admission,
              &firewall,
              &signature,
              &environment,
              &witness,
              &proof) == HHS_EXACT_STATUS_OK);

    auto tampered_proof = proof;
    tampered_proof.witness_hash72[0] =
        tampered_proof.witness_hash72[0] == '0' ? '1' : '0';
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_receipt_replay(
              &input,
              &committed,
              &parent,
              &admission,
              &firewall,
              &signature,
              &environment,
              &witness,
              &tampered_proof) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    auto tampered_environment = environment;
    tampered_environment.witness_sequence += 1U;
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_receipt_replay(
              &input,
              &committed,
              &parent,
              &admission,
              &firewall,
              &signature,
              &tampered_environment,
              &witness,
              &proof) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    HHSExactPass219Hash216FractalQuditReceiptV1 rejected{};
    CHECK(hhs_exact_pass219_hash216_fractal_qudit_hydrate_proof(
              &input,
              &committed,
              &parent,
              &admission,
              &firewall,
              &signature,
              &environment,
              &bad_mass,
              &rejected) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    CHECK(rejected.accepted == 0U);
    CHECK((rejected.failed_scope_mask &
           HHS_EXACT_PASS219_FQ_SCOPE_MASS_FACTORIZATION) != 0U);

    std::printf(
        "PASS219_HASH216_FRACTAL_QUDIT_ADMISSION_1_45_PASS "
        "local=%u witness=%llu receipt=%llu env=%llu\n",
        static_cast<unsigned>(proof.local5184),
        static_cast<unsigned long long>(proof.witness_signature64),
        static_cast<unsigned long long>(proof.receipt_signature64),
        static_cast<unsigned long long>(proof.environment_witness_sequence));
    return 0;
}
