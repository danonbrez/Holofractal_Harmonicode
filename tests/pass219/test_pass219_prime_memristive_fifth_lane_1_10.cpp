#include "hhs_pass219_prime_memristive_fifth_lane_1_10.hpp"

#define main hhs_pass219_i10_embedded_main
#include "test_pass219_prime_memristive_fifth_lane_1_9.cpp"
#undef main

#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

static void i11_fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) {
    for (std::size_t i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static void i11_fill_identity216(
    char out[HHS_EXACT_UQCEL_HASH216_STRLEN],
    std::uint8_t offset) {
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 7U + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

static HHSExactPass219Hash216TransitionViewV1 i11_build_transition(std::uint8_t offset) {
    HHSExactPass219Hash216TransitionViewV1 transition{};
    char previous[HHS_EXACT_HASH72_STRLEN]{};
    char change[HHS_EXACT_HASH72_STRLEN]{};
    char receipt[HHS_EXACT_HASH72_STRLEN]{};
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
    i11_fill_hash72(previous, offset);
    i11_fill_hash72(change, static_cast<std::uint8_t>(offset + 1U));
    i11_fill_hash72(receipt, static_cast<std::uint8_t>(offset + 2U));
    i11_fill_identity216(identity, static_cast<std::uint8_t>(offset + 3U));
    if (hhs_exact_pass219_hash216_transition_init(
            previous, change, receipt, identity, &transition) != HHS_EXACT_STATUS_OK)
        std::memset(&transition, 0, sizeof(transition));
    return transition;
}

static HHSExactVM81Frame i11_build_frame() {
    HHSExactVM81Frame frame{};
    for (std::uint32_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        const std::uint64_t a = UINT64_C(0x9e3779b97f4a7c15) * (i + 1U);
        const std::uint64_t b = UINT64_C(0x0102040810204081) ^
            (static_cast<std::uint64_t>(i) << (i % 17U));
        frame.words[i] = a ^ b;
    }
    return frame;
}

static std::array<std::int64_t, HHS_PASS219_PRIME_LANE_CELL_COUNT> i11_magic_square() {
    std::array<std::int64_t, HHS_PASS219_PRIME_LANE_CELL_COUNT> cells{};
    int row = 0;
    int column = 4;
    for (int value = 1; value <= 81; ++value) {
        cells[static_cast<std::size_t>(row * 9 + column)] = value;
        const int next_row = (row + 8) % 9;
        const int next_column = (column + 1) % 9;
        if (cells[static_cast<std::size_t>(next_row * 9 + next_column)] != 0) {
            row = (row + 1) % 9;
        } else {
            row = next_row;
            column = next_column;
        }
    }
    return cells;
}

static std::string i11_hex(const std::vector<std::uint8_t>& bytes) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string out{};
    out.reserve(bytes.size() * 2U);
    for (const auto byte : bytes) {
        out.push_back(digits[(byte >> 4U) & 0x0fU]);
        out.push_back(digits[byte & 0x0fU]);
    }
    return out;
}

static bool i11_same_budget(
    const PrimeLaneActivationBudgetStateV8& a,
    const PrimeLaneActivationBudgetStateV8& b) {
    return a.neighborhood_binding_signature64 == b.neighborhood_binding_signature64 &&
           a.capacity == b.capacity && a.available == b.available &&
           a.consumed_total == b.consumed_total &&
           a.replenished_total == b.replenished_total &&
           a.debit_ordinal == b.debit_ordinal;
}

int main() {
    CHECK(hhs_pass219_i10_embedded_main() == 0);
    CHECK(HHS_EXACT_PASS219_HOLO4_LANE_COUNT == 4U);
    CHECK(HHS_PASS219_PRIME_LANE_I11_NAMESPACE == UINT32_C(0x21911));
    CHECK(HHS_PASS219_PRIME_LANE_I11_MAX_ADDRESS_BYTES == 384U);
    CHECK(hhs_pass219_prime_lane_bigint_address_authority_valid(
        PrimeLaneBigIntAddressAuthorityV11{}));

    HHSExactPass219Holo4StateV1 holo4_state{};
    HHSExactPass219Holo4PreparedV1 prepared{};
    const auto transition = i11_build_transition(23U);
    const auto frame = i11_build_frame();
    CHECK(transition.struct_size == sizeof(transition));
    CHECK(hhs_exact_pass219_holo4_state_init(&holo4_state) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_holo4_prepare(
              &frame, &transition, &holo4_state, &prepared) == HHS_EXACT_STATUS_OK);
    const HHSExactPass219Holo4StateV1 frozen_holo4_state = holo4_state;

    const auto cells = i11_magic_square();
    const auto fingerprint = PrimeMemristiveFifthLaneV1::fingerprint(cells);
    CHECK(hhs_pass219_prime_lane_authority_valid(fingerprint.authority));
    for (const auto& fibre : fingerprint.fibres)
        CHECK(fibre.modular_magic_closure);

    constexpr std::uint8_t address_cell = 40U;
    PrimeLaneFiveLaneAddressV11 address_a{};
    PrimeLaneFiveLaneAddressV11 address_b{};
    CHECK(PrimeLaneFiveLaneBigIntCodecV11::encode(
        prepared, fingerprint, address_cell, address_a));
    CHECK(PrimeLaneFiveLaneBigIntCodecV11::encode(
        prepared, fingerprint, address_cell, address_b));
    CHECK(address_a.bytes_be == address_b.bytes_be);
    CHECK(address_a.address_signature64 == address_b.address_signature64);
    CHECK(!address_a.bytes_be.empty());
    CHECK(address_a.bytes_be.front() != 0U);
    CHECK(address_a.bytes_be.size() <= HHS_PASS219_PRIME_LANE_I11_MAX_ADDRESS_BYTES);
    CHECK(address_a.bit_length > 0U);

    PrimeLaneFiveLaneDecodedAddressV11 decoded{};
    CHECK(PrimeLaneFiveLaneBigIntCodecV11::decode(address_a, decoded));
    CHECK(PrimeLaneFiveLaneBigIntCodecV11::matches(prepared, fingerprint, decoded));
    CHECK(decoded.cell81 == address_cell);
    CHECK(decoded.tensor_signature64 == prepared.tensor_signature64);
    CHECK(decoded.fingerprint_signature64 == fingerprint.fingerprint_signature64);
    CHECK(decoded.local_signature64 == prepared.cells[address_cell].local_signature64);
    for (std::size_t lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane)
        CHECK(decoded.hash216_position[lane] == prepared.cells[address_cell].hash216_position[lane]);
    for (std::size_t fibre = 0U; fibre < HHS_PASS219_PRIME_LANE_FIBRE_COUNT; ++fibre) {
        CHECK(decoded.cell_residue[fibre] == fingerprint.cell_residue[fibre][address_cell]);
        CHECK(decoded.u[fibre] == fingerprint.fibres[fibre].u);
        CHECK(decoded.v[fibre] == fingerprint.fibres[fibre].v);
        CHECK(decoded.rho[fibre] == fingerprint.fibres[fibre].rho);
        CHECK(decoded.magic_sum_residue[fibre] == fingerprint.fibres[fibre].magic_sum_residue);
        CHECK(decoded.modular_magic_closure[fibre] == 1U);
    }

    PrimeLaneFiveLaneAddressV11 neighboring_address{};
    CHECK(PrimeLaneFiveLaneBigIntCodecV11::encode(
        prepared, fingerprint, static_cast<std::uint8_t>(address_cell + 1U), neighboring_address));
    CHECK(neighboring_address.bytes_be != address_a.bytes_be);
    CHECK(neighboring_address.address_signature64 != address_a.address_signature64);

    PrimeLaneFiveLaneAddressV11 noncanonical = address_a;
    noncanonical.bytes_be.insert(noncanonical.bytes_be.begin(), 0U);
    CHECK(!PrimeLaneFiveLaneBigIntCodecV11::decode(noncanonical, decoded));

    {
        std::ofstream file("/tmp/pass219_i11_address.hex", std::ios::trunc);
        CHECK(file.good());
        file << i11_hex(address_a.bytes_be) << '\n';
        CHECK(file.good());
    }

    constexpr std::uint64_t source_binding = UINT64_C(0xc100000000000001);
    constexpr std::uint64_t target_binding = UINT64_C(0xc100000000000002);
    constexpr std::uint64_t query_context = UINT64_C(0xc200000000000001);
    constexpr std::uint64_t source_context = UINT64_C(0xc200000000000002);
    constexpr std::uint64_t composition = UINT64_C(0xc300000000000001);

    auto target = candidate(
        query_context, source_context, composition, target_binding,
        HHS_PASS219_PRIME_LANE_MODALITY_TEXT, 320);
    const PrimeLaneReplayAssociationKeyV6 target_association = target.transition.key.target;
    PrimeLaneReplayConditionedPrefetchV7 prefetch{};
    CHECK(prefetch.register_target(target_association, target.neighborhood));
    CHECK(prefetch.observe_transition(source_binding, target_association, 1, 1U));

    PrimeLaneAdaptiveReplayLedgerV6 replay{};
    PrimeLaneReplayEventV6 replay_event{};
    replay_event.key = target_association;
    replay_event.admission_feedback_trinary = 1;
    replay_event.warm_reference_work = 1U;
    replay_event.cold_posting_work = 32U;
    replay_event.sequence = 1U;
    PrimeLaneReplayReceiptV6 replay_receipt{};
    CHECK(replay.apply(replay_event, replay_receipt));

    PrimeLaneBudgetedPredictiveHydratorV8 hydrator{};
    CHECK(hydrator.register_budget(source_binding, 64U, 64U));
    PrimeLaneActivationBudgetStateV8 budget_before{};
    CHECK(hydrator.budget_for(source_binding, budget_before));

    PrimeLaneArbitrationCandidateReceiptV10 winner{};
    winner.query_context_signature64 = query_context;
    winner.active_modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;
    winner.neighborhood_binding_signature64 = source_binding;
    winner.composition_signature64 = composition;
    winner.exact_hop_floor = 17U;
    winner.work_allocation = 40U;
    winner.competition_rank = 1U;
    winner.winner_ordinal = 1U;
    winner.eligible = true;
    winner.winner = true;
    winner.exclusion = PrimeLaneArbitrationExclusionV10::none;

    PrimeLaneHash216CandidateGraphV3 graph{};
    PrimeLaneRouteDecisionV1 cold_decision{};
    PrimeLaneSparseWinnerExecutorV11 executor{};
    PrimeLaneSparseWinnerExecutionReceiptV11 execution{};
    CHECK(executor.execute_one_hop(
        winner, prepared, fingerprint, address_cell,
        HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
        replay, prefetch, graph, cold_decision, 1U, hydrator, execution));
    CHECK(execution.source_neighborhood_binding_signature64 == source_binding);
    CHECK(execution.target_neighborhood_binding_signature64 == target_binding);
    CHECK(execution.winner_ordinal == 1U);
    CHECK(execution.allocated_work == 40U);
    CHECK(execution.exact_work_spent == 17U);
    CHECK(execution.remaining_allocation == 23U);
    CHECK(execution.inherited_budget_receipt.exact_hop_cost == 17U);
    CHECK(execution.inherited_budget_receipt.budget_before == 64U);
    CHECK(execution.inherited_budget_receipt.budget_after == 47U);
    CHECK(execution.five_lane_address.bytes_be == address_a.bytes_be);

    PrimeLaneActivationBudgetStateV8 budget_after{};
    CHECK(hydrator.budget_for(source_binding, budget_after));
    CHECK(budget_after.available == 47U);
    CHECK(budget_after.consumed_total == 17U);
    CHECK(budget_after.debit_ordinal == 1U);

    std::vector<PrimeLaneEnergyHopReceiptV8> reverse_receipts{
        execution.inherited_budget_receipt};
    CHECK(hydrator.reverse_receipts(reverse_receipts));
    PrimeLaneActivationBudgetStateV8 restored{};
    CHECK(hydrator.budget_for(source_binding, restored));
    CHECK(i11_same_budget(budget_before, restored));

    PrimeLaneArbitrationCandidateReceiptV10 nonwinner = winner;
    nonwinner.winner = false;
    nonwinner.winner_ordinal = 0U;
    nonwinner.exclusion = PrimeLaneArbitrationExclusionV10::sparse_limit;
    PrimeLaneSparseWinnerExecutionReceiptV11 rejected{};
    CHECK(!executor.execute_one_hop(
        nonwinner, prepared, fingerprint, address_cell,
        HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
        replay, prefetch, graph, cold_decision, 1U, hydrator, rejected));
    PrimeLaneActivationBudgetStateV8 after_nonwinner{};
    CHECK(hydrator.budget_for(source_binding, after_nonwinner));
    CHECK(i11_same_budget(restored, after_nonwinner));

    PrimeLaneArbitrationCandidateReceiptV10 underfunded = winner;
    underfunded.work_allocation = 16U;
    underfunded.exact_hop_floor = 16U;
    CHECK(!executor.execute_one_hop(
        underfunded, prepared, fingerprint, address_cell,
        HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
        replay, prefetch, graph, cold_decision, 1U, hydrator, rejected));
    PrimeLaneActivationBudgetStateV8 after_underfunded{};
    CHECK(hydrator.budget_for(source_binding, after_underfunded));
    CHECK(i11_same_budget(restored, after_underfunded));

    PrimeLaneVerifiedOutcomeMetabolismV9 metabolism{};
    CHECK(metabolism.register_route(source_binding, 128U));
    PrimeLaneMetabolicStateV9 metabolic_before{};
    PrimeLaneMetabolicStateV9 metabolic_after{};
    CHECK(metabolism.state_for(source_binding, metabolic_before));
    CHECK(metabolism.state_for(source_binding, metabolic_after));
    CHECK(metabolic_before.vitality == metabolic_after.vitality);
    CHECK(metabolic_before.positive_verified == metabolic_after.positive_verified);
    CHECK(metabolic_before.negative_verified == metabolic_after.negative_verified);

    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);

    std::printf(
        "lane5_i11_native=PASS address_bytes=%zu address_bits=%u address_signature=%llu "
        "cell=%u winner_spent=%llu winner_remaining=%llu budget_restored=%llu holo4_lanes=%u\n",
        address_a.bytes_be.size(),
        address_a.bit_length,
        static_cast<unsigned long long>(address_a.address_signature64),
        static_cast<unsigned>(address_cell),
        static_cast<unsigned long long>(execution.exact_work_spent),
        static_cast<unsigned long long>(execution.remaining_allocation),
        static_cast<unsigned long long>(restored.available),
        static_cast<unsigned>(HHS_EXACT_PASS219_HOLO4_LANE_COUNT));
    return 0;
}
