#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <vector>

namespace {
using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_sink = 0U;
constexpr std::uint32_t kFrames = 256U;
constexpr std::uint32_t kRounds = 1024U;
constexpr int kSamples = 9;
constexpr std::uint32_t kReferencePasses =
    1U + HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES +
    HHS_EXACT_PASS219_CORE_CIRCUIT_LOSHU_FEATURES;

std::uint64_t mix64(std::uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

std::uint64_t rotl64(std::uint64_t value, std::uint32_t shift) {
    shift &= 63U;
    if (shift == 0U)
        return value;
    return (value << shift) | (value >> (64U - shift));
}

std::uint32_t popcount64(std::uint64_t value) {
    std::uint32_t count = 0U;
    while (value != 0U) {
        value &= value - UINT64_C(1);
        ++count;
    }
    return count;
}

HHSExactVM81Frame make_frame(std::uint64_t seed) {
    HHSExactVM81Frame frame{};
    for (std::uint32_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        seed = mix64(seed ^ (static_cast<std::uint64_t>(i + 1U) << 32U));
        frame.words[i] = seed;
    }
    return frame;
}

HHSExactPass219CoreCircuitFeaturesV1 reference_extract(
    const HHSExactVM81Frame &frame
) {
    HHSExactPass219CoreCircuitFeaturesV1 out{};
    out.struct_size = sizeof(out);
    out.version = HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION;
    out.word_visits = HHS_EXACT_VM81_CELLS;

    for (std::uint32_t cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell) {
        const std::uint64_t word = frame.words[cell];
        const std::uint32_t pc = popcount64(word);
        out.total_popcount += pc;
        out.nonzero_words += word != 0U ? 1U : 0U;
        out.xor_signature64 ^= rotl64(word, cell & 63U);
        out.sum_signature64 += word;
    }

    for (std::uint32_t phase = 0U;
         phase < HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES;
         ++phase) {
        for (std::uint32_t cell = phase;
             cell < HHS_EXACT_VM81_CELLS;
             cell += HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES)
            out.phase_popcount[phase] += popcount64(frame.words[cell]);
        const std::uint32_t p = out.phase_popcount[phase] %
                                HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS;
        out.trinary_phase[phase] =
            p < 24U ? static_cast<std::int8_t>(-1) :
            (p < 48U ? static_cast<std::int8_t>(0) :
                       static_cast<std::int8_t>(1));
    }

    for (std::uint32_t row = 0U;
         row < HHS_EXACT_PASS219_CORE_CIRCUIT_LOSHU_FEATURES;
         ++row) {
        for (std::uint32_t cell = row;
             cell < HHS_EXACT_VM81_CELLS;
             cell += HHS_EXACT_PASS219_CORE_CIRCUIT_LOSHU_FEATURES)
            out.loshu_popcount[row] += popcount64(frame.words[cell]);
    }

    out.hydration_signature64 =
        mix64(out.xor_signature64 ^ rotl64(out.sum_signature64, 17U) ^
              (static_cast<std::uint64_t>(out.total_popcount) << 32U) ^
              static_cast<std::uint64_t>(out.nonzero_words) ^
              UINT64_C(0x2190000000000048));
    return out;
}

bool feature_equal(const HHSExactPass219CoreCircuitFeaturesV1 &a,
                   const HHSExactPass219CoreCircuitFeaturesV1 &b) {
    return a.struct_size == b.struct_size && a.version == b.version &&
           a.word_visits == b.word_visits &&
           a.nonzero_words == b.nonzero_words &&
           a.total_popcount == b.total_popcount &&
           std::memcmp(a.phase_popcount, b.phase_popcount,
                       sizeof(a.phase_popcount)) == 0 &&
           std::memcmp(a.loshu_popcount, b.loshu_popcount,
                       sizeof(a.loshu_popcount)) == 0 &&
           std::memcmp(a.trinary_phase, b.trinary_phase,
                       sizeof(a.trinary_phase)) == 0 &&
           a.xor_signature64 == b.xor_signature64 &&
           a.sum_signature64 == b.sum_signature64 &&
           a.hydration_signature64 == b.hydration_signature64;
}

template <class Fn>
std::uint64_t median_ns(Fn fn) {
    fn();
    std::vector<std::uint64_t> values;
    values.reserve(static_cast<std::size_t>(kSamples));
    for (int sample = 0; sample < kSamples; ++sample) {
        const auto begin = Clock::now();
        fn();
        const auto end = Clock::now();
        values.push_back(static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin)
                .count()));
    }
    std::sort(values.begin(), values.end());
    return values[values.size() / 2U];
}

std::uint64_t ratio_x1000(std::uint64_t numerator, std::uint64_t denominator) {
    return denominator == 0U ? 0U : (numerator * UINT64_C(1000)) / denominator;
}

std::int8_t calibration_target(
    const HHSExactPass219CoreCircuitFeaturesV1 &f
) {
    static const std::int32_t hidden[
        HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT
    ] = {5, -4, 3, 2, -1, 4, -3, 1};
    std::int32_t score = -1;
    for (std::uint32_t i = 0U;
         i < HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT;
         ++i)
        score += hidden[i] * static_cast<std::int32_t>(f.trinary_phase[i]);
    return score >= 0 ? static_cast<std::int8_t>(1)
                      : static_cast<std::int8_t>(-1);
}

std::uint32_t accuracy_x1000(
    const std::array<HHSExactVM81Frame, kFrames> &frames,
    const HHSExactPass219CoreCircuitStateV1 &state
) {
    std::uint32_t correct = 0U;
    for (const auto &frame : frames) {
        HHSExactPass219CoreCircuitFeaturesV1 features{};
        HHSExactPass219CoreCircuitDecisionV1 decision{};
        if (hhs_exact_pass219_core_circuit_extract(&frame, &features) !=
                HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_core_circuit_predict(
                &features, &state, &decision) != HHS_EXACT_STATUS_OK)
            std::abort();
        const std::int8_t predicted =
            decision.prediction_trinary == 0 ? static_cast<std::int8_t>(-1)
                                             : decision.prediction_trinary;
        correct += predicted == calibration_target(features) ? 1U : 0U;
    }
    return (correct * 1000U) / kFrames;
}
}  // namespace

int main() {
    std::array<HHSExactVM81Frame, kFrames> frames{};
    for (std::uint32_t i = 0U; i < kFrames; ++i)
        frames[i] = make_frame(UINT64_C(0x2190000000000000) + i);

    bool exact_feature_equal = true;
    for (const auto &frame : frames) {
        const auto reference = reference_extract(frame);
        HHSExactPass219CoreCircuitFeaturesV1 fused{};
        if (hhs_exact_pass219_core_circuit_extract(&frame, &fused) !=
            HHS_EXACT_STATUS_OK)
            std::abort();
        if (!feature_equal(reference, fused))
            exact_feature_equal = false;
    }

    std::uint32_t cursor = 0U;
    const auto reference_ns = median_ns([&]() {
        for (std::uint32_t round = 0U; round < kRounds; ++round) {
            const auto out = reference_extract(frames[cursor++ % kFrames]);
            g_sink ^= out.hydration_signature64;
        }
    });
    cursor = 0U;
    const auto fused_ns = median_ns([&]() {
        for (std::uint32_t round = 0U; round < kRounds; ++round) {
            HHSExactPass219CoreCircuitFeaturesV1 out{};
            if (hhs_exact_pass219_core_circuit_extract(
                    &frames[cursor++ % kFrames], &out) != HHS_EXACT_STATUS_OK)
                std::abort();
            g_sink ^= out.hydration_signature64;
        }
    });

    HHSExactPass219CoreCircuitStateV1 state{};
    if (hhs_exact_pass219_core_circuit_state_init(&state) != HHS_EXACT_STATUS_OK)
        std::abort();
    const std::uint32_t pre_accuracy = accuracy_x1000(frames, state);
    for (std::uint32_t epoch = 0U; epoch < 12U; ++epoch) {
        for (const auto &frame : frames) {
            HHSExactPass219CoreCircuitFeaturesV1 features{};
            HHSExactPass219CoreCircuitDecisionV1 decision{};
            if (hhs_exact_pass219_core_circuit_extract(&frame, &features) !=
                HHS_EXACT_STATUS_OK)
                std::abort();
            const std::int8_t target = calibration_target(features);
            if (hhs_exact_pass219_core_circuit_step(
                    &frame, target, &state, &features, &decision) !=
                HHS_EXACT_STATUS_OK)
                std::abort();
        }
    }
    const std::uint32_t post_accuracy = accuracy_x1000(frames, state);

    const std::uint64_t ref_visits =
        static_cast<std::uint64_t>(HHS_EXACT_VM81_CELLS) * kReferencePasses;
    const std::uint64_t fused_visits = HHS_EXACT_VM81_CELLS;

    std::cout << "{\n"
              << "  \"exact_feature_equal\": "
              << (exact_feature_equal ? "true" : "false") << ",\n"
              << "  \"reference_passes\": " << kReferencePasses << ",\n"
              << "  \"fused_passes\": 1,\n"
              << "  \"reference_word_visits\": " << ref_visits << ",\n"
              << "  \"fused_word_visits\": " << fused_visits << ",\n"
              << "  \"algorithmic_work_reduction_x1000\": "
              << ratio_x1000(ref_visits, fused_visits) << ",\n"
              << "  \"reference_batch_median_ns\": " << reference_ns << ",\n"
              << "  \"fused_batch_median_ns\": " << fused_ns << ",\n"
              << "  \"wall_speedup_x1000\": "
              << ratio_x1000(reference_ns, fused_ns) << ",\n"
              << "  \"synthetic_pretrain_accuracy_x1000\": "
              << pre_accuracy << ",\n"
              << "  \"synthetic_posttrain_accuracy_x1000\": "
              << post_accuracy << ",\n"
              << "  \"learning_updates\": " << state.update_count << ",\n"
              << "  \"training_steps\": " << state.step_count << "\n"
              << "}\n";
    return exact_feature_equal ? 0 : 2;
}
