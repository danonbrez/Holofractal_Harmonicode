#include "hhs_runtime_exact_abi.h"

#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>

namespace {

struct Sample {
    HHSExactVM81Frame frame{};
    HHSExactPass219Hash216TransitionViewV1 transition{};
    std::uint8_t target{};
};

void fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) {
    for (std::size_t i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

void fill_identity216(char out[HHS_EXACT_UQCEL_HASH216_STRLEN], std::uint8_t offset) {
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 5U + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

/* The calibration target is a stable Hash216 hydration-lane relation. Raw VM81
 * payload bits vary between train and heldout samples, while the exact lane
 * identity and all popcount-level class evidence remain stable. This tests
 * whether the local/bank learner acquires the declared lane relation without
 * pretending to generalize to an unseen Hash216 identity. */
bool init_transition(HHSExactPass219Hash216TransitionViewV1& transition,
                     std::uint8_t lane) {
    char previous[HHS_EXACT_HASH72_STRLEN]{};
    char change[HHS_EXACT_HASH72_STRLEN]{};
    char receipt[HHS_EXACT_HASH72_STRLEN]{};
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
    const std::uint8_t base = static_cast<std::uint8_t>(lane * 13U + 1U);
    fill_hash72(previous, base);
    fill_hash72(change, static_cast<std::uint8_t>(base + 1U));
    fill_hash72(receipt, static_cast<std::uint8_t>(base + 2U));
    fill_identity216(identity, static_cast<std::uint8_t>(base + 3U));
    return hhs_exact_pass219_hash216_transition_init(
               previous, change, receipt, identity, &transition) == HHS_EXACT_STATUS_OK;
}

Sample make_sample(std::uint8_t lane, std::uint8_t variant) {
    Sample sample{};
    sample.target = lane;
    const std::uint8_t target_bank = lane;
    for (std::uint32_t cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell) {
        const std::uint32_t row = cell / 9U;
        const std::uint32_t col = cell % 9U;
        const std::uint8_t bank = static_cast<std::uint8_t>((row / 3U) * 3U + col / 3U);
        const std::uint64_t sparse = UINT64_C(1) << ((cell + variant * 7U) % 63U);
        const std::uint64_t second = UINT64_C(1) << ((cell * 3U + variant + 11U) % 63U);
        sample.frame.words[cell] = sparse | second;
        if (bank == target_bank) {
            const std::uint64_t notch = UINT64_C(1) << ((cell + variant * 5U) % 63U);
            sample.frame.words[cell] = ~notch;
        }
    }
    if (!init_transition(sample.transition, lane))
        std::memset(&sample.transition, 0, sizeof(sample.transition));
    return sample;
}

void zero_trainable_weights(HHSExactPass219Holo4StateV1& state) {
    std::memset(state.core.weights, 0, sizeof(state.core.weights));
    state.core.bias = 0;
    std::memset(state.cell_lane_weights, 0, sizeof(state.cell_lane_weights));
    std::memset(state.bank_lane_weights, 0, sizeof(state.bank_lane_weights));
    std::memset(state.lane_bias, 0, sizeof(state.lane_bias));
}

std::uint32_t accuracy_x1000(
    HHSExactPass219Holo4StateV1 state,
    const std::array<Sample, 32>& samples
) {
    std::uint32_t correct = 0U;
    for (const Sample& sample : samples) {
        HHSExactPass219Holo4PreparedV1 prepared{};
        HHSExactPass219Holo4DecisionV1 decision{};
        if (hhs_exact_pass219_holo4_route(
                &sample.frame, &sample.transition,
                HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
                &state, &prepared, &decision) != HHS_EXACT_STATUS_OK)
            return 0U;
        if (decision.selected_lane == sample.target)
            ++correct;
    }
    return (correct * 1000U) / static_cast<std::uint32_t>(samples.size());
}

bool raw_payload_sets_are_distinct(
    const std::array<Sample, 32>& train,
    const std::array<Sample, 32>& heldout
) {
    for (std::size_t i = 0U; i < train.size(); ++i) {
        if (std::memcmp(&train[i].frame, &heldout[i].frame, sizeof(HHSExactVM81Frame)) == 0)
            return false;
        if (std::memcmp(train[i].transition.transition_identity216,
                        heldout[i].transition.transition_identity216,
                        HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
            return false;
    }
    return true;
}

}  // namespace

int main() {
    HHSExactPass219Holo4DescriptorV1 descriptor{};
    HHSExactPass219Holo4StateV1 state{};
    if (hhs_exact_pass219_holo4_descriptor(&descriptor) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_holo4_state_init(&state) != HHS_EXACT_STATUS_OK)
        return 1;
    zero_trainable_weights(state);
    if (hhs_exact_pass219_holo4_validate_state(&state) != HHS_EXACT_STATUS_OK)
        return 2;

    std::array<Sample, 32> train{};
    std::array<Sample, 32> heldout{};
    for (std::uint32_t i = 0U; i < train.size(); ++i) {
        const std::uint8_t lane = static_cast<std::uint8_t>(i % 4U);
        const std::uint8_t variant = static_cast<std::uint8_t>((i / 4U) % 8U);
        train[i] = make_sample(lane, variant);
        heldout[i] = make_sample(lane, static_cast<std::uint8_t>(variant + 8U));
        if (train[i].transition.struct_size == 0U || heldout[i].transition.struct_size == 0U)
            return 3;
    }
    const bool raw_payload_distinct = raw_payload_sets_are_distinct(train, heldout);
    if (!raw_payload_distinct)
        return 4;

    const std::uint32_t pretrain = accuracy_x1000(state, heldout);
    const std::uint32_t epochs = 48U;
    const std::uint32_t training_steps = epochs * static_cast<std::uint32_t>(train.size());
    for (std::uint32_t epoch = 0U; epoch < epochs; ++epoch) {
        for (std::uint32_t j = 0U; j < train.size(); ++j) {
            const std::uint32_t index = (j * 13U + epoch * 7U) % static_cast<std::uint32_t>(train.size());
            const Sample& sample = train[index];
            HHSExactPass219Holo4PreparedV1 prepared{};
            HHSExactPass219Holo4DecisionV1 decision{};
            if (hhs_exact_pass219_holo4_route(
                    &sample.frame, &sample.transition,
                    sample.target, 1,
                    &state, &prepared, &decision) != HHS_EXACT_STATUS_OK)
                return 5;
        }
    }
    if (hhs_exact_pass219_holo4_validate_state(&state) != HHS_EXACT_STATUS_OK)
        return 6;
    const std::uint32_t posttrain = accuracy_x1000(state, heldout);

    constexpr std::uint32_t prepare_cell_visits = 81U;
    constexpr std::uint32_t prepare_graph_visits = 1620U;
    constexpr std::uint32_t score_cell_visits = 81U;
    constexpr std::uint32_t score_bank_visits = 9U;
    constexpr std::uint32_t naive_total_work =
        4U * (prepare_cell_visits + prepare_graph_visits + score_cell_visits + score_bank_visits);
    constexpr std::uint32_t shared_total_work =
        prepare_cell_visits + prepare_graph_visits +
        4U * (score_cell_visits + score_bank_visits);
    constexpr std::uint32_t work_reduction_x1000 =
        (naive_total_work * 1000U) / shared_total_work;

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_CORE_HOLOGRAPHIC_FOUR_LANE_BENCHMARK_V1\",\n");
    std::printf("  \"cell_count\": %u,\n", descriptor.cell_count);
    std::printf("  \"sudoku_peers_per_cell\": %u,\n", descriptor.peers_per_cell);
    std::printf("  \"directed_graph_edges\": %u,\n", descriptor.directed_graph_edges);
    std::printf("  \"lane_count\": %u,\n", descriptor.lane_count);
    std::printf("  \"phase_modulus\": %u,\n", descriptor.phase_modulus);
    std::printf("  \"update_quantum\": %u,\n", descriptor.update_quantum);
    std::printf("  \"naive_independent_lane_work\": %u,\n", naive_total_work);
    std::printf("  \"shared_tensor_four_lane_work\": %u,\n", shared_total_work);
    std::printf("  \"deterministic_work_reduction_x1000\": %u,\n", work_reduction_x1000);
    std::printf("  \"heldout_raw_payloads_distinct\": %s,\n", raw_payload_distinct ? "true" : "false");
    std::printf("  \"lane_identity_stable_across_variants\": true,\n");
    std::printf("  \"unseen_hash216_identity_generalization_claim\": false,\n");
    std::printf("  \"heldout_pretrain_accuracy_x1000\": %u,\n", pretrain);
    std::printf("  \"heldout_posttrain_accuracy_x1000\": %u,\n", posttrain);
    std::printf("  \"training_steps\": %u,\n", training_steps);
    std::printf("  \"learning_updates\": %u,\n", state.update_count);
    std::printf("  \"candidate_only\": true,\n");
    std::printf("  \"canonical_authority_changed\": false\n");
    std::printf("}\n");

    if (descriptor.cell_count != 81U || descriptor.peers_per_cell != 20U ||
        descriptor.directed_graph_edges != 1620U || descriptor.lane_count != 4U)
        return 7;
    if (naive_total_work != 7164U || shared_total_work != 2061U || work_reduction_x1000 != 3475U)
        return 8;
    if (posttrain <= pretrain)
        return 9;
    return 0;
}
