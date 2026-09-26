#include "hhs_pass219_prime_memristive_fifth_lane_1_6.hpp"

#include <array>
#include <cstdint>
#include <cstdio>
#include <vector>

using namespace hhs::rna;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed: %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (false)

static PrimeLanePreparedRecordV2 record(std::uint32_t id, std::int64_t offset) {
    PrimeLanePreparedRecordV2 out{};
    out.record_id = id;
    for (std::size_t i = 0U; i < out.cells.size(); ++i)
        out.cells[i] = static_cast<std::int64_t>(i) + offset;
    out.fingerprint = PrimeMemristiveFifthLaneV1::fingerprint(out.cells);
    return out;
}

static PrimeLaneContextRouteV3 route(
    std::uint64_t context,
    std::uint64_t composition,
    std::uint8_t fibre) {
    PrimeLaneContextRouteV3 out{};
    out.context_signature64 = context;
    out.component_plan_count = 1U;
    out.selected_count = 1U;
    out.fibre_index[0] = fibre;
    out.composition_signature64 = composition;
    return out;
}

static PrimeLaneHash216NeighborhoodRefV6 neighborhood(std::uint64_t binding) {
    PrimeLaneHash216NeighborhoodRefV6 out{};
    out.key.source_context_signature64 = UINT64_C(0xd100000000000001);
    out.key.composition_signature64 = UINT64_C(0xd200000000000001);
    out.key.modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;
    out.binding_signature64 = binding;
    out.observed_sequence = 1U;
    PrimeLaneHash216NeighborhoodMemberV6 member{};
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        member.identity216[i] = '0';
    member.identity216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    member.identity_signature64 = binding ^ UINT64_C(0x5a5a5a5a5a5a5a5a);
    if (member.identity_signature64 == 0U)
        member.identity_signature64 = 1U;
    member.alias_cardinality = 1U;
    out.members.push_back(member);
    return out;
}

int main() {
    CHECK(HHS_EXACT_PASS219_HOLO4_LANE_COUNT == 4U);

    // I2: zero-axis indexed query and linear oracle must represent the same
    // unconstrained candidate universe; malformed fibre indices fail closed.
    PrimeLaneCandidateIndexV2 index{};
    std::vector<PrimeLanePreparedRecordV2> records{record(7U, 11), record(3U, 29)};
    CHECK(index.build(records));
    PrimeLaneRouteDecisionV1 zero_axes{};
    PrimeLaneCandidateResultV2 indexed_zero{};
    PrimeLaneLinearResultV2 linear_zero{};
    CHECK(index.query(zero_axes, 1U, indexed_zero));
    CHECK(index.linear_scan(zero_axes, 0U, linear_zero));
    CHECK(indexed_zero.record_ids == linear_zero.record_ids);
    CHECK(indexed_zero.record_ids.size() == 2U);
    CHECK(indexed_zero.record_ids[0] == 3U && indexed_zero.record_ids[1] == 7U);
    CHECK(!indexed_zero.candidate_budget_reached);

    PrimeLaneRouteDecisionV1 malformed_axis{};
    malformed_axis.selected_count = 1U;
    malformed_axis.fibre_index[0] = static_cast<std::uint8_t>(HHS_PASS219_PRIME_LANE_FIBRE_COUNT);
    PrimeLaneCandidateResultV2 rejected_indexed{};
    PrimeLaneLinearResultV2 rejected_linear{};
    CHECK(!index.query(malformed_axis, 1U, rejected_indexed));
    CHECK(!index.linear_scan(malformed_axis, 1U, rejected_linear));

    // I4: every uint32 quantum, including UINT32_MAX, must move utility
    // monotonically toward zero without narrowing/sign inversion.
    PrimeLaneAdaptiveContextRouterV4 adaptive{};
    constexpr std::uint64_t positive_context = UINT64_C(0xd300000000000001);
    constexpr std::uint64_t negative_context = UINT64_C(0xd300000000000002);
    constexpr std::uint64_t positive_composition = UINT64_C(0xd400000000000001);
    constexpr std::uint64_t negative_composition = UINT64_C(0xd400000000000002);
    CHECK(adaptive.register_route(route(positive_context, positive_composition, 0U)));
    CHECK(adaptive.register_route(route(negative_context, negative_composition, 1U)));
    CHECK(adaptive.observe(positive_context, positive_composition, 100U, 0U, 0U, 1, 1U));
    CHECK(adaptive.observe(negative_context, negative_composition, 100U, 100U, 100U, -1, 1U));
    PrimeLaneRouteUtilityV4 positive_before{};
    PrimeLaneRouteUtilityV4 negative_before{};
    CHECK(adaptive.utility_for(positive_context, positive_composition, positive_before));
    CHECK(adaptive.utility_for(negative_context, negative_composition, negative_before));
    CHECK(positive_before.utility_q10 > 0);
    CHECK(negative_before.utility_q10 < 0);
    CHECK(adaptive.decay_context(positive_context, UINT32_MAX));
    CHECK(adaptive.decay_context(negative_context, UINT32_MAX));
    PrimeLaneRouteUtilityV4 positive_after{};
    PrimeLaneRouteUtilityV4 negative_after{};
    CHECK(adaptive.utility_for(positive_context, positive_composition, positive_after));
    CHECK(adaptive.utility_for(negative_context, negative_composition, negative_after));
    CHECK(positive_after.utility_q10 == 0);
    CHECK(negative_after.utility_q10 == 0);

    // I6: a malformed input neighborhood invalidates composition instead of
    // being silently omitted while a partial result is returned.
    const auto valid = neighborhood(UINT64_C(0xd500000000000001));
    auto malformed = neighborhood(UINT64_C(0xd500000000000002));
    malformed.members.front().alias_cardinality = 0U;
    PrimeLaneHash216NeighborhoodStoreV6 store{};
    PrimeLaneHash216NeighborhoodRefV6 composed{};
    PrimeLaneNeighborhoodRecallMetricsV6 metrics{};
    CHECK(store.compose({valid}, HHS_PASS219_PRIME_LANE_MODALITY_TEXT, composed, metrics));
    CHECK(!store.compose({valid, malformed}, HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                         composed, metrics));

    std::printf(
        "lane5_i11_hardening=PASS zero_axis_parity=1 fibre_bounds=1 "
        "uint32_decay_monotonic=1 malformed_neighborhood_fail_closed=1\n");
    return 0;
}
