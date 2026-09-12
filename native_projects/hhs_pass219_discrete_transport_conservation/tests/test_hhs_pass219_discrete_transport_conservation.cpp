#include "hhs_pass219_discrete_transport_conservation_1_29.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>

namespace {

using hhs::pass219::RNAAdmissionView;
using hhs::pass219::transport::ContractReport;
using hhs::pass219::transport::Direction;
using hhs::pass219::transport::Node;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::cerr << "CHECK failed at " << __FILE__ << ':' << __LINE__ << ": " #expr "\n"; \
        return 1; \
    } \
} while (false)

struct ResolverContext final {
    std::uint32_t calls{};
};

HHSExactStatus index_resolver(
    const char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    std::uint8_t lane_role,
    std::uint8_t lane_position72,
    std::uint16_t absolute_position216,
    std::uint8_t glyph,
    std::uint8_t out_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES],
    void* context
) {
    auto* ctx = static_cast<ResolverContext*>(context);
    if (transition_identity216 == nullptr || out_sha256 == nullptr || ctx == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (absolute_position216 !=
        static_cast<std::uint16_t>(static_cast<std::uint16_t>(lane_role) * 72U + lane_position72))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (std::size_t i = 0U; i < HHS_EXACT_PASS219_HASH216_SHA256_BYTES; ++i) {
        out_sha256[i] = static_cast<std::uint8_t>(
            glyph ^ lane_role ^ lane_position72 ^
            static_cast<std::uint8_t>(absolute_position216) ^
            static_cast<std::uint8_t>(i) ^
            static_cast<std::uint8_t>(
                transition_identity216[i % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]
            )
        );
    }
    ++ctx->calls;
    return HHS_EXACT_STATUS_OK;
}

void set_view(HHSExactBigUIntView& view, const std::uint8_t* bytes, std::size_t length) {
    view.struct_size = static_cast<std::uint32_t>(sizeof(view));
    view.byte_length = static_cast<std::uint32_t>(length);
    view.bytes_be = bytes;
}

void build_candidate_frame(HHSExactVM81Frame& out) {
    static constexpr std::array<std::uint8_t, 32U> environment_root = {
        0xdaU,0x28U,0xe8U,0x22U,0x48U,0x38U,0x99U,0x97U,
        0x59U,0xd0U,0x71U,0xa3U,0x6fU,0xb2U,0x5fU,0x92U,
        0x4aU,0xf1U,0x0aU,0x9fU,0xffU,0xe2U,0xacU,0xd7U,
        0x9bU,0x4bU,0x2cU,0x0cU,0x78U,0x40U,0x85U,0x1bU,
    };

    std::memset(&out, 0, sizeof(out));
    out.words[0] = UINT64_C(0x4832313949313632);
    out.words[1] = UINT64_C(30);
    out.words[2] = UINT64_C(29);
    out.words[3] = UINT64_C(31);
    out.words[4] = UINT64_C(1);
    out.words[5] = UINT64_C(900);
    out.words[6] = UINT64_C(810000);
    out.words[7] = UINT64_C(26970);
    out.words[8] = UINT64_C(71022);
    out.words[9] = UINT64_C(1023);
    out.words[10] = UINT64_C(31);
    out.words[11] = UINT64_C(18) |
                    (UINT64_C(54) << 8U) |
                    (UINT64_C(18) << 16U) |
                    (UINT64_C(54) << 24U);

    for (std::uint32_t chunk = 0U; chunk < 4U; ++chunk) {
        std::uint64_t word = 0U;
        for (std::uint32_t byte_index = 0U; byte_index < 8U; ++byte_index) {
            word |= static_cast<std::uint64_t>(environment_root[chunk * 8U + byte_index])
                    << (8U * byte_index);
        }
        out.words[12U + chunk] = word;
    }
}

int run() {
    static constexpr std::array<std::uint8_t, 1U> p_capital = {0x1eU};
    static constexpr std::array<std::uint8_t, 1U> p_lower = {0x1dU};
    static constexpr std::array<std::uint8_t, 1U> q_lower = {0x1fU};
    static constexpr std::array<std::uint8_t, 1U> delta = {0x01U};
    static constexpr std::array<std::uint8_t, 2U> p_squared = {0x03U, 0x84U};

    HHSExactUQCELInputV1 input{};
    HHSExactVM81Frame candidate{};
    HHSExactVM81Frame committed{};
    HHSExactPass219RNAAdmissionV1 admission{};
    std::array<std::uint8_t, HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES> source_sha{};
    ResolverContext resolver_context{};

    build_candidate_frame(candidate);
    CHECK(hhs_exact_uqcel_source_sha256(source_sha.data()) == HHS_EXACT_STATUS_OK);

    input.struct_size = static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    set_view(input.P, p_capital.data(), p_capital.size());
    set_view(input.p, p_lower.data(), p_lower.size());
    set_view(input.q, q_lower.data(), q_lower.size());
    set_view(input.delta, delta.data(), delta.size());
    set_view(input.A, p_squared.data(), p_squared.size());
    set_view(input.B, p_squared.data(), p_squared.size());
    input.cell81 = 0U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    std::memcpy(input.source_envelope_sha256, source_sha.data(), source_sha.size());
    std::memset(input.previous_hash72, '0', HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';

    CHECK(hhs_exact_pass219_rna_admit_composed(
              &input,
              &candidate,
              0,
              0U,
              index_resolver,
              &resolver_context,
              &committed,
              &admission
          ) == HHS_EXACT_STATUS_OK);
    CHECK(admission.composed.uqcel.decision == HHS_EXACT_UQCEL_DECISION_ADMIT);
    CHECK(admission.composed.uqcel.frame_committed == 1U);
    CHECK(std::memcmp(&candidate, &committed, sizeof(candidate)) == 0);
    CHECK(resolver_context.calls == HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    CHECK(hhs_exact_pass219_hash216_indexes_complete(&admission.transition) == HHS_EXACT_STATUS_OK);

    const HHSExactPass219RNAAdmissionV1 frozen_admission = admission;
    const Node anchor{
        admission.coordinate.operation64,
        0U,
        admission.coordinate.cell81,
    };
    const bool anchor_verified = hhs::pass219::transport::rna_admission_anchor_matches(
        RNAAdmissionView(&admission), anchor
    );
    CHECK(anchor_verified);

    static constexpr std::array<Direction, 8U> sequence = {
        Direction::X,
        Direction::W,
        Direction::Y,
        Direction::Z,
        Direction::W,
        Direction::X,
        Direction::Z,
        Direction::Y,
    };
    CHECK(hhs::pass219::transport::reverse_sequence_restores(
        anchor, sequence.data(), sequence.size()
    ));

    const bool admission_immutable =
        std::memcmp(&frozen_admission, &admission, sizeof(admission)) == 0;
    CHECK(admission_immutable);

    ContractReport report = hhs::pass219::transport::audit_entire_address_manifold();
    report.rna_admission_anchor_verified = anchor_verified;
    report.rna_record_immutable_under_transport = admission_immutable;
    report.pass = report.pass &&
                  report.rna_admission_authority_delegated &&
                  report.rna_admission_anchor_verified &&
                  report.rna_record_immutable_under_transport;

    CHECK(report.node_count == UINT64_C(373248));
    CHECK(report.address_count == UINT64_C(1492992));
    CHECK(report.discrete_divergence_nodes_checked == report.node_count);
    CHECK(report.reciprocal_edge_addresses_checked == report.address_count);
    CHECK(report.admission_preservation_addresses_checked == report.address_count);
    CHECK(report.zero_diffusion_addresses_checked == report.address_count);
    CHECK(report.composed_reverse_addresses_checked == report.address_count);
    CHECK(report.unique_target_addresses == report.address_count);
    CHECK(report.failure_count == 0U);
    CHECK(report.discrete_divergence_gate);
    CHECK(report.reciprocal_edge_balance_gate);
    CHECK(report.admission_preservation_gate);
    CHECK(report.zero_canonical_diffusion_gate);
    CHECK(report.composed_reverse_closure_gate);
    CHECK(report.exhaustive_address_coverage);
    CHECK(report.target_map_bijective);
    CHECK(!report.lossy_compression_used);
    CHECK(!report.neighbor_averaging_used);
    CHECK(!report.hash216_cryptographic_inversion_used);
    CHECK(!report.canonical_vm81_mutation_authority);
    CHECK(!report.canonical_hash72_mint_authority);
    CHECK(!report.canonical_hash216_persistence_authority);
    CHECK(!report.floating_point_canonical_authority);
    CHECK(!report.scalar_projection_substitution_authority);
    CHECK(!report.timing_authority);
    CHECK(report.pass);

    std::cout << hhs::pass219::transport::report_json(report) << '\n';
    return 0;
}

}  // namespace

int main() {
    return run();
}
