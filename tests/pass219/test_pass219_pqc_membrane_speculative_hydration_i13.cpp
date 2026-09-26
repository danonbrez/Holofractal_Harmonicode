#include "hhs_pass219_pqc_membrane_speculative_hydration_i13.h"

#include <array>
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

struct UQCELOwnersI13 final {
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
        frame.words[i] = UINT64_C(0x0102030405060708) ^ static_cast<std::uint64_t>(i);
    return frame;
}

static HHSExactStatus build_input(
    UQCELOwnersI13& owners,
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

static void bind_candidate_hash72(
    HHSExactPass219AdmissibleProjectionI13& projection,
    const HHSExactVM81Frame& frame
) {
    std::array<std::uint8_t, HHS_EXACT_VM81_FRAME_BYTES> bytes{};
    std::size_t written = 0U;
    if (hhs_exact_vm81_frame_export_le(
            &frame, bytes.data(), bytes.size(), &written) != HHS_EXACT_STATUS_OK ||
        written != bytes.size())
        std::abort();
    hhs_hash72_compute_bytes(
        bytes.data(), bytes.size(), projection.closure_proof.candidate_frame_hash72);
}

static HHSExactPass219AdmissibleProjectionI13 valid_projection(
    const HHSExactVM81Frame& frame
) {
    HHSExactPass219AdmissibleProjectionI13 projection{};
    projection.struct_size = static_cast<std::uint32_t>(sizeof(projection));
    projection.version = HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION;

    projection.provenance.struct_size = static_cast<std::uint32_t>(sizeof(projection.provenance));
    projection.provenance.version = HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION;
    for (std::size_t i = 0U; i < HHS_EXACT_PASS219_PQC_SOURCE_HASH_BYTES; ++i)
        projection.provenance.source_hash[i] = static_cast<std::uint8_t>(i + 1U);
    projection.provenance.architecture_id = HHS_EXACT_PASS219_SOURCE_ARCH_QWEN2;
    std::memset(
        projection.provenance.projection_root_hash216,
        'R', HHS_HASH216_BYTES_LEN);
    projection.provenance.projection_root_hash216[HHS_HASH216_BYTES_LEN] = '\0';
    projection.provenance.immutable_source_archive = 1U;
    projection.provenance.source_archive_outside_pqc = 1U;
    projection.provenance.raw_weight_blob_absent = 1U;
    projection.provenance.provenance_anchor_inside_pqc = 1U;

    projection.lane_mappings.struct_size = static_cast<std::uint32_t>(sizeof(projection.lane_mappings));
    projection.lane_mappings.version = HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION;
    for (std::size_t lane = 0U; lane < HHS_EXACT_PASS219_PQC_PROJECTION_LANES; ++lane) {
        for (std::size_t j = 0U; j < HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES; ++j)
            projection.lane_mappings.lane_root_sha256[lane][j] =
                static_cast<std::uint8_t>(1U + lane * 17U + j);
    }
    projection.lane_mappings.harmonic36_coordinate = UINT64_C(0x123456789);
    projection.lane_mappings.prime_factor_surface_index = UINT64_C(307);
    projection.lane_mappings.projection_lane_count = 5U;
    projection.lane_mappings.canonical_holo4_lane_count = 4U;
    projection.lane_mappings.fifth_lane_candidate_only = 1U;
    projection.lane_mappings.five_lane_projection_verified = 1U;

    projection.closure_proof.struct_size = static_cast<std::uint32_t>(sizeof(projection.closure_proof));
    projection.closure_proof.version = HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION;
    for (std::size_t i = 0U; i < HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES; ++i) {
        projection.closure_proof.exact_constraint_surface_sha256[i] =
            static_cast<std::uint8_t>(0x31U + i);
        projection.closure_proof.projection_proof_sha256[i] =
            static_cast<std::uint8_t>(0x71U + i);
    }
    projection.closure_proof.exact_rational_only = 1U;
    projection.closure_proof.delta_e_zero = 1U;
    projection.closure_proof.psi_zero = 1U;
    projection.closure_proof.omega_true = 1U;
    projection.closure_proof.xy_n4_unity_verified = 1U;
    projection.closure_proof.algebraic_solver_verified = 1U;
    projection.closure_proof.manifold_closed = 1U;
    projection.closure_proof.no_probabilistic_payload = 1U;
    bind_candidate_hash72(projection, frame);

    projection.lifecycle.struct_size = static_cast<std::uint32_t>(sizeof(projection.lifecycle));
    projection.lifecycle.version = HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION;
    projection.lifecycle.phase = HHS_EXACT_PASS219_ORACLE_DEPENDENCY;
    projection.lifecycle.verified_route_count = 0U;
    projection.lifecycle.required_route_count = 0U;
    projection.lifecycle.frontier_miss_count = 1U;
    projection.lifecycle.external_oracle_enabled = 1U;
    projection.lifecycle.oracle_severance_authorized = 0U;
    projection.lifecycle.canonical_routes_only = 1U;

    projection.speculative_candidate_only = 1U;
    projection.probabilistic_payload_present = 0U;
    projection.requests_direct_model_commit = 0U;
    projection.requests_non_vm81_canonical_commit = 0U;
    return projection;
}

static bool frame_is_zero(const HHSExactVM81Frame& frame) noexcept {
    const HHSExactVM81Frame zero{};
    return std::memcmp(&frame, &zero, sizeof(frame)) == 0;
}

static int negative_membrane_tests(const HHSExactVM81Frame& frame) {
    {
        auto p = valid_projection(frame);
        p.provenance.source_archive_outside_pqc = 0U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.provenance.source_hash[0] = 0U;
        std::memset(p.provenance.source_hash, 0, sizeof(p.provenance.source_hash));
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.lane_mappings.canonical_holo4_lane_count = 5U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.lane_mappings.fifth_lane_candidate_only = 0U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.lane_mappings.harmonic36_coordinate = HHS_EXACT_PASS219_PQC_HARMONIC36_MAX + 1U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.closure_proof.exact_rational_only = 0U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.closure_proof.delta_e_zero = 0U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.closure_proof.psi_zero = 0U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.closure_proof.omega_true = 0U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.probabilistic_payload_present = 1U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.requests_direct_model_commit = 1U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
    }
    {
        auto p = valid_projection(frame);
        p.lifecycle.phase = HHS_EXACT_PASS219_NATIVE_AUTONOMY;
        p.lifecycle.external_oracle_enabled = 0U;
        p.lifecycle.oracle_severance_authorized = 1U;
        p.lifecycle.required_route_count = 100U;
        p.lifecycle.verified_route_count = 99U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 0U);
        p.lifecycle.verified_route_count = 100U;
        CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&p) == 1U);
    }
    return 0;
}

int main() {
    CHECK(install_root_key());

    HHSExactPass219Hash216TransitionViewV1 parent{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) ==
          HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&parent) ==
          HHS_EXACT_STATUS_OK);

    UQCELOwnersI13 owners{};
    HHSExactUQCELInputV1 input{};
    CHECK(build_input(owners, parent, input) == HHS_EXACT_STATUS_OK);

    const HHSExactVM81Frame candidate = build_candidate();
    auto projection = valid_projection(candidate);
    CHECK(hhs_exact_pass219_pqc_projection_valid_i13(&projection) == 1U);

    {
        auto mismatched = projection;
        mismatched.closure_proof.candidate_frame_hash72[0] =
            mismatched.closure_proof.candidate_frame_hash72[0] == 'X' ? 'Y' : 'X';
        HHSExactVM81Frame committed{};
        HHSExactPass219RNAAdmissionV1 admission{};
        HHSExactPass219VM81PQCFirewallReceiptV1 firewall{};
        HHSExactPass219VM81PQCSignatureReceiptV1 signature{};
        HHSExactPass219VM81EnvironmentReceiptV1 environment{};
        CHECK(hhs_exact_pass219_pqc_membrane_ingest_i13(
                  &mismatched,
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
                  &environment) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
        CHECK(frame_is_zero(committed));
    }

    HHSExactVM81Frame committed{};
    HHSExactPass219RNAAdmissionV1 admission{};
    HHSExactPass219VM81PQCFirewallReceiptV1 firewall{};
    HHSExactPass219VM81PQCSignatureReceiptV1 signature{};
    HHSExactPass219VM81EnvironmentReceiptV1 environment{};

    const std::uint32_t algorithm =
        HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65;
    const bool provider_available =
        hhs_exact_pass219_vm81_pqc_signature_provider_available(algorithm) == 1U;

    const HHSExactStatus status = hhs_exact_pass219_pqc_membrane_ingest_i13(
        &projection,
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

    if (provider_available) {
        CHECK(status == HHS_EXACT_STATUS_OK);
        CHECK(std::memcmp(&committed, &candidate, sizeof(candidate)) == 0);
        CHECK(firewall.decision == HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED);
        CHECK(firewall.parent_hash216_verified == 1U);
        CHECK(firewall.child_hash216_verified == 1U);
        CHECK(firewall.rna_cell_wall_routed == 1U);
        CHECK(firewall.inherited_rna_authority_invoked == 1U);
        CHECK(firewall.firewall_is_canonical_authority == 0U);
        CHECK(environment.canonical_mutation_authority == 0U);
        CHECK(environment.canonical_receipt_authority == 0U);
        CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&admission.transition) ==
              HHS_EXACT_STATUS_OK);
    } else {
        CHECK(status == HHS_EXACT_STATUS_INVARIANT_FAILURE);
        CHECK(frame_is_zero(committed));
        CHECK(firewall.inherited_rna_authority_invoked == 0U);
    }

    CHECK(negative_membrane_tests(candidate) == 0);
    std::puts("PASS219_PQC_MEMBRANE_SPECULATIVE_HYDRATION_I13_PASS");
    return 0;
}
