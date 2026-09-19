#include "hhs_pass219_multisource_convergence_i14.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

#define CHECK(expr) do { if (!(expr)) { std::fprintf(stderr, "CHECK failed %s:%d: %s\n", __FILE__, __LINE__, #expr); return 1; } } while (0)

struct Owners final { std::uint8_t P{4U}, p{3U}, q{5U}, delta{1U}, A{16U}, B{16U}; };

static HHSExactBigUIntView view_of(const std::uint8_t* v) {
    HHSExactBigUIntView out{}; out.struct_size = sizeof(out); out.byte_length = 1U; out.bytes_be = v; return out;
}

static bool install_root_key() {
    std::string hex; static constexpr char digits[] = "0123456789abcdef";
    for (std::size_t i = 0; i < HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES; ++i) {
        const auto v = static_cast<std::uint8_t>(i + 1U);
        hex.push_back(digits[(v >> 4U) & 0x0FU]); hex.push_back(digits[v & 0x0FU]);
    }
    return setenv(HHS_EXACT_PASS219_VM81_PQC_KEY_ENV, hex.c_str(), 1) == 0;
}

static HHSExactVM81Frame candidate_frame() {
    HHSExactVM81Frame f{};
    for (std::size_t i = 0; i < HHS_EXACT_VM81_CELLS; ++i)
        f.words[i] = UINT64_C(0x0102030405060708) ^ static_cast<std::uint64_t>(i);
    return f;
}

static void bind_frame(HHSExactPass219AdmissibleProjectionI13& p, const HHSExactVM81Frame& f) {
    std::array<std::uint8_t, HHS_EXACT_VM81_FRAME_BYTES> bytes{}; std::size_t written = 0U;
    if (hhs_exact_vm81_frame_export_le(&f, bytes.data(), bytes.size(), &written) != HHS_EXACT_STATUS_OK || written != bytes.size()) std::abort();
    hhs_hash72_compute_bytes(bytes.data(), bytes.size(), p.closure_proof.candidate_frame_hash72);
}

static HHSExactPass219AdmissibleProjectionI13 projection_for(
    const HHSExactVM81Frame& frame, std::uint8_t seed, std::uint32_t architecture, char root_char) {
    HHSExactPass219AdmissibleProjectionI13 p{};
    p.struct_size = sizeof(p); p.version = HHS_EXACT_PASS219_PQC_MEMBRANE_I13_VERSION;
    p.provenance.struct_size = sizeof(p.provenance); p.provenance.version = p.version;
    for (std::size_t i = 0; i < HHS_EXACT_PASS219_PQC_SOURCE_HASH_BYTES; ++i) p.provenance.source_hash[i] = static_cast<std::uint8_t>(seed + i);
    p.provenance.architecture_id = architecture;
    std::memset(p.provenance.projection_root_hash216, root_char, HHS_HASH216_BYTES_LEN); p.provenance.projection_root_hash216[HHS_HASH216_BYTES_LEN] = '\0';
    p.provenance.immutable_source_archive = 1U; p.provenance.source_archive_outside_pqc = 1U; p.provenance.raw_weight_blob_absent = 1U; p.provenance.provenance_anchor_inside_pqc = 1U;
    p.lane_mappings.struct_size = sizeof(p.lane_mappings); p.lane_mappings.version = p.version;
    for (std::size_t lane = 0; lane < HHS_EXACT_PASS219_PQC_PROJECTION_LANES; ++lane)
        for (std::size_t j = 0; j < HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES; ++j)
            p.lane_mappings.lane_root_sha256[lane][j] = static_cast<std::uint8_t>(1U + lane * 17U + j);
    p.lane_mappings.harmonic36_coordinate = UINT64_C(0x123456789); p.lane_mappings.prime_factor_surface_index = 307U;
    p.lane_mappings.projection_lane_count = 5U; p.lane_mappings.canonical_holo4_lane_count = 4U; p.lane_mappings.fifth_lane_candidate_only = 1U; p.lane_mappings.five_lane_projection_verified = 1U;
    p.closure_proof.struct_size = sizeof(p.closure_proof); p.closure_proof.version = p.version;
    for (std::size_t i = 0; i < HHS_EXACT_PASS219_PQC_PROOF_SHA256_BYTES; ++i) {
        p.closure_proof.exact_constraint_surface_sha256[i] = static_cast<std::uint8_t>(0x31U + i);
        p.closure_proof.projection_proof_sha256[i] = static_cast<std::uint8_t>(seed + 0x40U + i);
    }
    p.closure_proof.exact_rational_only = 1U; p.closure_proof.delta_e_zero = 1U; p.closure_proof.psi_zero = 1U; p.closure_proof.omega_true = 1U;
    p.closure_proof.xy_n4_unity_verified = 1U; p.closure_proof.algebraic_solver_verified = 1U; p.closure_proof.manifold_closed = 1U; p.closure_proof.no_probabilistic_payload = 1U;
    bind_frame(p, frame);
    p.lifecycle.struct_size = sizeof(p.lifecycle); p.lifecycle.version = p.version; p.lifecycle.phase = HHS_EXACT_PASS219_ORACLE_DEPENDENCY; p.lifecycle.frontier_miss_count = 1U; p.lifecycle.external_oracle_enabled = 1U; p.lifecycle.canonical_routes_only = 1U;
    p.speculative_candidate_only = 1U;
    return p;
}

static HHSExactStatus build_input(Owners& o, const HHSExactPass219Hash216TransitionViewV1& parent, HHSExactUQCELInputV1& input) {
    input = {}; input.struct_size = sizeof(input); input.uqcel_version = hhs_exact_uqcel_version(); input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.P = view_of(&o.P); input.p = view_of(&o.p); input.q = view_of(&o.q); input.delta = view_of(&o.delta); input.A = view_of(&o.A); input.B = view_of(&o.B);
    input.cell81 = 41U; input.left_basis8 = HHS_EXACT_PHASE_X; input.right_basis8 = HHS_EXACT_PHASE_Y;
    auto status = hhs_exact_uqcel_source_sha256(input.source_envelope_sha256); if (status != HHS_EXACT_STATUS_OK) return status;
    std::memcpy(input.previous_hash72, parent.receipt_hash72, HHS_EXACT_HASH72_STRLEN); return HHS_EXACT_STATUS_OK;
}

static HHSExactPass219AdmittedSourceEvidenceI14 fixture_evidence(
    const HHSExactPass219AdmissibleProjectionI13& projection,
    const HHSExactVM81Frame& frame,
    const HHSExactPass219Hash216TransitionViewV1& transition,
    std::uint8_t salt) {
    HHSExactPass219AdmittedSourceEvidenceI14 e{};
    e.struct_size = sizeof(e); e.version = HHS_EXACT_PASS219_MULTISOURCE_I14_VERSION; e.projection = projection; e.committed_frame = frame;
    e.admission.struct_size = sizeof(e.admission); e.admission.version = hhs_exact_pass219_rna_version(); e.admission.transition = transition;
    e.firewall_receipt.struct_size = sizeof(e.firewall_receipt); e.firewall_receipt.version = HHS_EXACT_PASS219_VM81_PQC_VERSION; e.firewall_receipt.decision = HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED;
    std::memcpy(e.firewall_receipt.candidate_hash72, projection.closure_proof.candidate_frame_hash72, HHS_HASH72_BYTES_STRLEN);
    std::memcpy(e.firewall_receipt.child_hash216_identity, transition.transition_identity216, HHS_EXACT_UQCEL_HASH216_STRLEN);
    e.firewall_receipt.parent_hash216_verified = 1U; e.firewall_receipt.child_hash216_verified = 1U; e.firewall_receipt.rna_cell_wall_routed = 1U; e.firewall_receipt.pqc_authenticated = 1U; e.firewall_receipt.inherited_rna_authority_invoked = 1U; e.firewall_receipt.canonical_receipt_owned_by_inherited_authority = 1U;
    e.signature_receipt.struct_size = sizeof(e.signature_receipt); e.signature_receipt.version = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION; e.signature_receipt.algorithm = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65; e.signature_receipt.decision = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED; e.signature_receipt.signature_length = 1U; e.signature_receipt.provider_available = 1U; e.signature_receipt.key_derived_from_kernel_root = 1U; e.signature_receipt.signature_generated_inside_kernel = 1U; e.signature_receipt.signature_verified_before_vm81 = 1U;
    for (std::size_t i = 0; i < 32U; ++i) { e.signature_receipt.public_key_sha256[i] = static_cast<std::uint8_t>(salt + i + 1U); e.signature_receipt.signed_message_sha256[i] = static_cast<std::uint8_t>(salt + i + 33U); e.signature_receipt.signature_sha256[i] = static_cast<std::uint8_t>(salt + i + 65U); }
    e.environment_receipt.struct_size = sizeof(e.environment_receipt); e.environment_receipt.version = HHS_EXACT_PASS219_VM81_ENV_VERSION; e.environment_receipt.state = HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING; e.environment_receipt.decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_READY; e.environment_receipt.reason = HHS_EXACT_PASS219_VM81_ENV_REASON_NONE; e.environment_receipt.genesis_verified = 1U; e.environment_receipt.witness_verified = 1U; e.environment_receipt.environment_signature_verified = 1U;
    for (std::size_t i = 0; i < 32U; ++i) e.environment_receipt.witness_sha256[i] = static_cast<std::uint8_t>(salt + i + 7U);
    e.i13_membrane_passed = 1U; return e;
}

static int fixture_logic_tests(const HHSExactVM81Frame& frame) {
    HHSExactPass219Hash216TransitionViewV1 parent{}; CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) == HHS_EXACT_STATUS_OK);
    char receipt_hash72[HHS_HASH72_BYTES_STRLEN]; static const char receipt_material[] = "I14 canonical route receipt"; hhs_hash72_compute_bytes(receipt_material, sizeof(receipt_material) - 1U, receipt_hash72);
    HHSExactPass219Hash216TransitionViewV1 route{}; CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_init(parent.receipt_hash72, projection_for(frame, 1U, HHS_EXACT_PASS219_SOURCE_ARCH_LLAMA3, 'L').closure_proof.candidate_frame_hash72, receipt_hash72, &route) == HHS_EXACT_STATUS_OK);
    auto p1 = projection_for(frame, 1U, HHS_EXACT_PASS219_SOURCE_ARCH_LLAMA3, 'L'); auto p2 = projection_for(frame, 101U, HHS_EXACT_PASS219_SOURCE_ARCH_QWEN2, 'Q');
    std::array<HHSExactPass219AdmittedSourceEvidenceI14, 2> evidence{fixture_evidence(p1, frame, route, 3U), fixture_evidence(p2, frame, route, 71U)};
    CHECK(hhs_exact_pass219_i14_admitted_evidence_valid(&evidence[0]) == 1U); CHECK(hhs_exact_pass219_i14_admitted_evidence_valid(&evidence[1]) == 1U);
    HHSExactPass219MultiSourceConvergenceReceiptI14 r{}; CHECK(hhs_exact_pass219_multisource_convergence_i14(evidence.data(), evidence.size(), &r) == HHS_EXACT_STATUS_OK);
    CHECK(r.decision == HHS_EXACT_PASS219_MULTISOURCE_CONVERGED); CHECK(r.deduplication_authorized == 1U); CHECK(r.unique_source_count == 2U); CHECK(r.canonical_identity_equal == 1U); CHECK(r.committed_frame_equal == 1U); CHECK(std::memcmp(r.source_route_binding_hash216[0], r.source_route_binding_hash216[1], HHS_HASH216_BYTES_STRLEN) != 0);
    auto duplicate = evidence; std::memcpy(duplicate[1].projection.provenance.source_hash, duplicate[0].projection.provenance.source_hash, HHS_EXACT_PASS219_PQC_SOURCE_HASH_BYTES); CHECK(hhs_exact_pass219_multisource_convergence_i14(duplicate.data(), duplicate.size(), &r) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    auto tampered = evidence; tampered[1].firewall_receipt.candidate_hash72[0] = tampered[1].firewall_receipt.candidate_hash72[0] == 'A' ? 'B' : 'A'; CHECK(hhs_exact_pass219_i14_admitted_evidence_valid(&tampered[1]) == 0U);
    char other_receipt[HHS_HASH72_BYTES_STRLEN]; static const char other_material[] = "I14 divergent route receipt"; hhs_hash72_compute_bytes(other_material, sizeof(other_material) - 1U, other_receipt);
    HHSExactPass219Hash216TransitionViewV1 other_route{}; CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_init(parent.receipt_hash72, p2.closure_proof.candidate_frame_hash72, other_receipt, &other_route) == HHS_EXACT_STATUS_OK);
    auto divergent = evidence; divergent[1] = fixture_evidence(p2, frame, other_route, 71U); CHECK(hhs_exact_pass219_multisource_convergence_i14(divergent.data(), divergent.size(), &r) == HHS_EXACT_STATUS_OK); CHECK(r.decision == HHS_EXACT_PASS219_MULTISOURCE_NOT_CONVERGED); CHECK(r.deduplication_authorized == 0U);
    return 0;
}

static HHSExactPass219AdmittedSourceEvidenceI14 live_evidence(
    const HHSExactPass219AdmissibleProjectionI13& p, const HHSExactVM81Frame& frame,
    const HHSExactPass219RNAAdmissionV1& admission, const HHSExactPass219VM81PQCFirewallReceiptV1& firewall,
    const HHSExactPass219VM81PQCSignatureReceiptV1& signature, const HHSExactPass219VM81EnvironmentReceiptV1& environment) {
    HHSExactPass219AdmittedSourceEvidenceI14 e{}; e.struct_size = sizeof(e); e.version = HHS_EXACT_PASS219_MULTISOURCE_I14_VERSION; e.projection = p; e.committed_frame = frame; e.admission = admission; e.firewall_receipt = firewall; e.signature_receipt = signature; e.environment_receipt = environment; e.i13_membrane_passed = 1U; return e;
}

static int optional_live_convergence(const HHSExactVM81Frame& candidate) {
    const std::uint32_t algorithm = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65;
    if (hhs_exact_pass219_vm81_pqc_signature_provider_available(algorithm) != 1U) { std::puts("I14_LIVE_MULTISOURCE_NOT_CLAIMED_PQC_PROVIDER_UNAVAILABLE"); return 0; }
    HHSExactPass219Hash216TransitionViewV1 parent{}; CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) == HHS_EXACT_STATUS_OK);
    Owners owners{}; HHSExactUQCELInputV1 input{}; CHECK(build_input(owners, parent, input) == HHS_EXACT_STATUS_OK);
    auto p1 = projection_for(candidate, 1U, HHS_EXACT_PASS219_SOURCE_ARCH_LLAMA3, 'L'); auto p2 = projection_for(candidate, 101U, HHS_EXACT_PASS219_SOURCE_ARCH_QWEN2, 'Q');
    std::array<HHSExactPass219AdmittedSourceEvidenceI14, 2> ev{};
    for (std::size_t i = 0; i < ev.size(); ++i) {
        const auto& p = i == 0U ? p1 : p2; HHSExactVM81Frame committed{}; HHSExactPass219RNAAdmissionV1 admission{}; HHSExactPass219VM81PQCFirewallReceiptV1 firewall{}; HHSExactPass219VM81PQCSignatureReceiptV1 signature{}; HHSExactPass219VM81EnvironmentReceiptV1 environment{};
        CHECK(hhs_exact_pass219_pqc_membrane_ingest_i13(&p, 220U, algorithm, &input, &candidate, &parent, 0, 0U, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0, &committed, &admission, &firewall, &signature, &environment) == HHS_EXACT_STATUS_OK);
        ev[i] = live_evidence(p, committed, admission, firewall, signature, environment); CHECK(hhs_exact_pass219_i14_admitted_evidence_valid(&ev[i]) == 1U);
    }
    HHSExactPass219MultiSourceConvergenceReceiptI14 receipt{}; CHECK(hhs_exact_pass219_multisource_convergence_i14(ev.data(), ev.size(), &receipt) == HHS_EXACT_STATUS_OK); CHECK(receipt.decision == HHS_EXACT_PASS219_MULTISOURCE_CONVERGED); CHECK(receipt.deduplication_authorized == 1U); std::puts("I14_LIVE_MULTISOURCE_CONVERGENCE_PASS"); return 0;
}

int main() {
    CHECK(install_root_key()); const auto frame = candidate_frame(); CHECK(fixture_logic_tests(frame) == 0); CHECK(optional_live_convergence(frame) == 0); std::puts("PASS219_MULTISOURCE_CONVERGENCE_I14_PASS"); return 0;
}
