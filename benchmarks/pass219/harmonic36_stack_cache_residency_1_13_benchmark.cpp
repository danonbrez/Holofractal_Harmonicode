#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_residency_sink = 0U;

constexpr int kSamples = 11;
constexpr std::uint32_t kRoundsPerSample = 4096U;
constexpr std::size_t kResidents = 4U;
constexpr std::size_t kCalibrationRepeats = 5U;
constexpr std::uint32_t kRequiredBeneficialRepeats = 4U;

struct SemanticResultLayout {
    std::uint64_t tty_input;
    std::uint64_t tty_output;
    std::uint64_t ptr_word36;
    std::uint64_t ptp_output;
    std::uint32_t tty_service_count;
    std::uint32_t ptr_service_count;
    std::uint32_t ptp_service_count;
    std::uint32_t apr_service_count;
    std::uint32_t uuo_service_count;
    std::uint32_t dispatch_count;
    std::uint32_t final_pc18;
    std::uint8_t queue_cursor;
};

struct CandidateRunLayout {
    SemanticResultLayout result;
    std::uint64_t image_signature36;
    std::uint64_t workload_signature36;
    std::uint32_t working_state_bytes;
    std::uint32_t resource_events;
};

struct ResidentSpec {
    const char *name;
    std::uint64_t workload_signature36;
    std::uint64_t semantic_signature64;
    std::uint64_t h36_median_ns;
    std::uint64_t linux_median_ns;
    std::uint32_t samples;
    std::uint32_t rounds;
    std::uint32_t h36_working_bytes;
    std::uint32_t linux_working_bytes;
    std::uint32_t h36_resource_events;
    std::uint32_t linux_resource_events;
    std::uint32_t expected_selected_candidate;
    const char *expected_key216;
};

struct ResidencyMeasurement {
    std::uint64_t fresh_median_ns = 0U;
    std::uint64_t occupancy1_median_ns = 0U;
    std::uint64_t occupancy4_median_ns = 0U;
    std::uint64_t occupancy4_vs_fresh_x1000 = 0U;
    std::uint64_t occupancy4_vs_occupancy1_x1000 = 0U;
    bool occupancy4_faster_than_fresh = false;
};

struct CalibratedResidency {
    std::array<ResidencyMeasurement, kCalibrationRepeats> repeats{};
    std::uint64_t fresh_total_ns = 0U;
    std::uint64_t occupancy1_total_ns = 0U;
    std::uint64_t occupancy4_total_ns = 0U;
    std::uint64_t fresh_median_ns = 0U;
    std::uint64_t occupancy1_median_ns = 0U;
    std::uint64_t occupancy4_median_ns = 0U;
    std::uint64_t occupancy4_vs_fresh_x1000 = 0U;
    std::uint64_t occupancy4_vs_occupancy1_x1000 = 0U;
    std::uint32_t beneficial_repeat_count = 0U;
    bool aggregate_benefit = false;
    bool repeat_stability_pass = false;
};

template <class Fn>
std::uint64_t median_ns(Fn fn) {
    fn();
    std::vector<std::uint64_t> values;
    values.reserve(static_cast<std::size_t>(kSamples));
    for (int i = 0; i < kSamples; ++i) {
        const auto begin = Clock::now();
        fn();
        const auto end = Clock::now();
        values.push_back(static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(
                end - begin).count()));
    }
    std::sort(values.begin(), values.end());
    return values[values.size() / 2U];
}

std::uint64_t ratio_x1000(
    std::uint64_t numerator,
    std::uint64_t denominator
) {
    if (denominator == 0U)
        return 0U;
    if (numerator > UINT64_MAX / UINT64_C(1000))
        return (numerator / denominator) * UINT64_C(1000);
    return (numerator * UINT64_C(1000)) / denominator;
}

std::array<ResidentSpec, kResidents> resident_specs() {
    const std::uint32_t h36_working_bytes =
        static_cast<std::uint32_t>(
            sizeof(HHSExactPass219H36VMStateV1) +
            sizeof(HHSExactPass219H36MonitorStateV1) +
            sizeof(HHSExactPass219H36MonitorReceiptV1) * 2U);
    const std::uint32_t linux_working_bytes =
        static_cast<std::uint32_t>(sizeof(CandidateRunLayout));

    return {{
        {
            "FULL_MONITOR",
            UINT64_C(3734727431),
            UINT64_C(4176962402124975431),
            UINT64_C(96531),
            UINT64_C(873043),
            9U,
            32U,
            5120U,
            100U,
            14U,
            20U,
            1U,
            "5nlPI!0Xj!c(aKeM<IZL2nng*h7f>N)RQyPLzEJG6x(+(w27-U8c/AaCSlDdIwXzdTh1ayAOgIGCzpNKFcHCeTQjeQ>nvDGFbmh<KOu>5arETCTAQzeuT8q!M?IORbb-KUXE1kCW59lt7Paz74<G3NwPCa/n+BUc/WKbPPi(54!!Oor!xH7!gP1o!7IC((j--g5xg<KmJJJSWOii5M-Z9Kx1"
        },
        {
            "CONSOLE_FOCUSED",
            UINT64_C(4793332410),
            UINT64_C(6731027650694893003),
            UINT64_C(23033),
            UINT64_C(106949),
            7U,
            8U,
            h36_working_bytes,
            linux_working_bytes,
            8U,
            12U,
            1U,
            "tfuz(1iI-X7B1jH408c-6n60BAOrYQQLMA3-*O<L+kOiKL<QZ4)ABrcd3BVdRQ!70bDSzLKw2nl2cNHJzYg>(2H>gcld8e8eKYQ/JDf(pnFIan>AVJbRsT01p/8eHt(L5X?fzNw)5El3?D9RG+U!za81-</XVI-Mni(qEzL?6B+/hBs9vck0O8UPIcKHn1gnXA2ZU7eZ+pS1(u2Ujj!E5+wG"
        },
        {
            "BINARY_IO_FOCUSED",
            UINT64_C(21509979554),
            UINT64_C(1456447110141201574),
            UINT64_C(23073),
            UINT64_C(109553),
            7U,
            8U,
            h36_working_bytes,
            linux_working_bytes,
            4U,
            10U,
            1U,
            "jei)gdf/PEAs9MILOtuHOQXpnUt*Tf47PD?zy3gwy!tZT5)Int*XpA4SKMXYcEMAgr+k>Mtyimln!(PDfX3E?49PUHB2a12t5X2dOb+HT/P6z+x8(124)bX(CZXaW3<-RU(mRMEWy77XtVOU-cU<U?YXV9(aw3hQtZGE-J*6M9Nmc<kBcaIq3JCDgQ48pBMyi(O<qZy1!ag6VRtLP>WnnApX"
        },
        {
            "MONITOR_CONTROL_FOCUSED",
            UINT64_C(41886677838),
            UINT64_C(2318081696571468614),
            UINT64_C(19156),
            UINT64_C(501),
            7U,
            8U,
            h36_working_bytes,
            linux_working_bytes,
            4U,
            4U,
            2U,
            "q(IxvVjjUvereKtdppA>uu1yyYAvB3fxjJWuY!QVYp1+UiLu9IdfM+rk1m/L7bbkCTUP3ij1nlJiPvfoK)n34B1t!JNsJC>Plr96YIz*ryA9EJ(RHPeJ?bZJgvj77NPrdCO6r2Sr!WI/T!GSFi!jWlIQCPctCXujdyOXett3<ojTipoRPYVdO*+tNp4c/vTx3H8o1N3wiforBk5--61?!Q76"
        }
    }};
}

void prepare_selection(
    const ResidentSpec &spec,
    HHSExactPass219H36StackCandidateEvidenceV1 &h36,
    HHSExactPass219H36StackCandidateEvidenceV1 &linux,
    HHSExactPass219H36StackSelectionV1 &selection
) {
    if (hhs_exact_pass219_h36_stack_candidate_prepare(
            1U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
            spec.workload_signature36,
            spec.semantic_signature64,
            spec.h36_median_ns,
            spec.samples,
            spec.rounds,
            spec.h36_working_bytes,
            spec.h36_resource_events,
            1U,
            &h36) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_candidate_prepare(
            2U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
            spec.workload_signature36,
            spec.semantic_signature64,
            spec.linux_median_ns,
            spec.samples,
            spec.rounds,
            spec.linux_working_bytes,
            spec.linux_resource_events,
            1U,
            &linux) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_select(
            &h36, &linux, &selection) != HHS_EXACT_STATUS_OK ||
        selection.selected_candidate_id != spec.expected_selected_candidate ||
        std::strcmp(
            selection.selected_vector_key216,
            spec.expected_key216) != 0)
        std::abort();
}

void require_exact_lookup(
    const HHSExactPass219H36StackCacheV1 &cache,
    const HHSExactPass219H36StackSelectionV1 &expected,
    HHSExactPass219H36StackCacheReceiptV1 *out_receipt
) {
    HHSExactPass219H36StackSelectionV1 hit{};
    HHSExactPass219H36StackCacheReceiptV1 receipt{};
    if (hhs_exact_pass219_h36_stack_cache_lookup(
            &cache,
            expected.workload_signature36,
            expected.semantic_result_signature64,
            expected.selected_vector_key216,
            &hit,
            &receipt) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
            &hit, &expected) != HHS_EXACT_STATUS_OK ||
        receipt.cache_hit != 1U ||
        receipt.exact_replayable != 1U ||
        receipt.stale_signature_rejected != 1U)
        std::abort();
    if (out_receipt != nullptr)
        *out_receipt = receipt;
}

void prove_isolation(
    const HHSExactPass219H36StackCacheV1 &shared,
    const std::array<HHSExactPass219H36StackSelectionV1, kResidents> &selections
) {
    for (std::size_t i = 0U; i < selections.size(); ++i) {
        HHSExactPass219H36StackCacheReceiptV1 first{};
        HHSExactPass219H36StackCacheReceiptV1 second{};
        require_exact_lookup(shared, selections[i], &first);
        require_exact_lookup(shared, selections[i], &second);
        if (std::memcmp(&first, &second, sizeof(first)) != 0)
            std::abort();

        HHSExactPass219H36StackSelectionV1 out{};
        HHSExactPass219H36StackCacheReceiptV1 receipt{};
        if (hhs_exact_pass219_h36_stack_cache_lookup(
                &shared,
                selections[i].workload_signature36,
                selections[i].semantic_result_signature64 ^ UINT64_C(1),
                selections[i].selected_vector_key216,
                &out,
                &receipt) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
            std::abort();

        char wrong_key[HHS_EXACT_UQCEL_HASH216_STRLEN];
        std::memcpy(
            wrong_key,
            selections[i].selected_vector_key216,
            sizeof(wrong_key));
        wrong_key[0] =
            wrong_key[0] == HHS_EXACT_HASH72_ALPHABET[0]
                ? HHS_EXACT_HASH72_ALPHABET[1]
                : HHS_EXACT_HASH72_ALPHABET[0];
        if (hhs_exact_pass219_h36_stack_cache_lookup(
                &shared,
                selections[i].workload_signature36,
                selections[i].semantic_result_signature64,
                wrong_key,
                &out,
                &receipt) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
            std::abort();

        const std::size_t other = (i + 1U) % selections.size();
        if (hhs_exact_pass219_h36_stack_cache_lookup(
                &shared,
                selections[i].workload_signature36,
                selections[other].semantic_result_signature64,
                selections[other].selected_vector_key216,
                &out,
                &receipt) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
            std::abort();
    }

    char unrelated_key[HHS_EXACT_UQCEL_HASH216_STRLEN];
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        unrelated_key[i] = HHS_EXACT_HASH72_ALPHABET[0];
    unrelated_key[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    HHSExactPass219H36StackSelectionV1 out{};
    HHSExactPass219H36StackCacheReceiptV1 receipt{};
    if (hhs_exact_pass219_h36_stack_cache_lookup(
            &shared,
            UINT64_C(1),
            UINT64_C(1),
            unrelated_key,
            &out,
            &receipt) != HHS_EXACT_STATUS_RANGE_ERROR)
        std::abort();

    HHSExactPass219H36StackCacheV1 duplicate_sequence = shared;
    duplicate_sequence.entries[1].sequence =
        duplicate_sequence.entries[0].sequence;
    if (hhs_exact_pass219_h36_stack_cache_validate(
            &duplicate_sequence) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        std::abort();

    HHSExactPass219H36StackCacheV1 duplicate_identity = shared;
    duplicate_identity.entries[1].selection =
        duplicate_identity.entries[0].selection;
    if (hhs_exact_pass219_h36_stack_cache_validate(
            &duplicate_identity) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        std::abort();

    HHSExactPass219H36StackCacheV1 partial_identity = shared;
    partial_identity.entries[1].selection.workload_signature36 =
        partial_identity.entries[0].selection.workload_signature36;
    if (hhs_exact_pass219_h36_stack_cache_validate(
            &partial_identity) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        std::abort();
}

ResidencyMeasurement measure_resident(
    const HHSExactPass219H36StackCandidateEvidenceV1 &h36,
    const HHSExactPass219H36StackCandidateEvidenceV1 &linux,
    const HHSExactPass219H36StackSelectionV1 &selection,
    const HHSExactPass219H36StackCacheV1 &occupancy1,
    const HHSExactPass219H36StackCacheV1 &occupancy4,
    std::size_t calibration_repeat
) {
    ResidencyMeasurement m{};

    const auto fresh_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kRoundsPerSample; ++i) {
            HHSExactPass219H36StackSelectionV1 fresh{};
            if (hhs_exact_pass219_h36_stack_select(
                    &h36, &linux, &fresh) != HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
                    &fresh, &selection) != HHS_EXACT_STATUS_OK)
                std::abort();
            checksum ^= fresh.speedup_x1000;
            checksum ^= static_cast<std::uint8_t>(
                fresh.selected_vector_key216[i % 216U]);
        }
        g_residency_sink ^= checksum;
    };

    const auto occupancy1_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kRoundsPerSample; ++i) {
            HHSExactPass219H36StackCacheReceiptV1 receipt{};
            require_exact_lookup(occupancy1, selection, &receipt);
            checksum ^= receipt.entry_signature64;
            checksum ^= receipt.replay_signature64;
        }
        g_residency_sink ^= checksum;
    };

    const auto occupancy4_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kRoundsPerSample; ++i) {
            HHSExactPass219H36StackCacheReceiptV1 receipt{};
            require_exact_lookup(occupancy4, selection, &receipt);
            checksum ^= receipt.entry_signature64;
            checksum ^= receipt.replay_signature64;
        }
        g_residency_sink ^= checksum;
    };

    if ((calibration_repeat & 1U) == 0U) {
        m.fresh_median_ns = median_ns(fresh_sample);
        m.occupancy1_median_ns = median_ns(occupancy1_sample);
        m.occupancy4_median_ns = median_ns(occupancy4_sample);
    } else {
        m.occupancy4_median_ns = median_ns(occupancy4_sample);
        m.occupancy1_median_ns = median_ns(occupancy1_sample);
        m.fresh_median_ns = median_ns(fresh_sample);
    }
    if (m.fresh_median_ns == 0U ||
        m.occupancy1_median_ns == 0U ||
        m.occupancy4_median_ns == 0U)
        std::abort();

    m.occupancy4_faster_than_fresh =
        m.occupancy4_median_ns < m.fresh_median_ns;
    m.occupancy4_vs_fresh_x1000 =
        m.occupancy4_faster_than_fresh
            ? ratio_x1000(m.fresh_median_ns, m.occupancy4_median_ns)
            : ratio_x1000(m.occupancy4_median_ns, m.fresh_median_ns);
    m.occupancy4_vs_occupancy1_x1000 =
        ratio_x1000(m.occupancy4_median_ns, m.occupancy1_median_ns);
    return m;
}

CalibratedResidency calibrate_resident(
    const HHSExactPass219H36StackCandidateEvidenceV1 &h36,
    const HHSExactPass219H36StackCandidateEvidenceV1 &linux,
    const HHSExactPass219H36StackSelectionV1 &selection,
    const HHSExactPass219H36StackCacheV1 &occupancy1,
    const HHSExactPass219H36StackCacheV1 &occupancy4
) {
    CalibratedResidency calibrated{};
    std::array<std::uint64_t, kCalibrationRepeats> fresh_values{};
    std::array<std::uint64_t, kCalibrationRepeats> occupancy1_values{};
    std::array<std::uint64_t, kCalibrationRepeats> occupancy4_values{};

    for (std::size_t repeat = 0U;
         repeat < kCalibrationRepeats;
         ++repeat) {
        calibrated.repeats[repeat] = measure_resident(
            h36,
            linux,
            selection,
            occupancy1,
            occupancy4,
            repeat);
        const ResidencyMeasurement &m = calibrated.repeats[repeat];
        fresh_values[repeat] = m.fresh_median_ns;
        occupancy1_values[repeat] = m.occupancy1_median_ns;
        occupancy4_values[repeat] = m.occupancy4_median_ns;
        calibrated.fresh_total_ns += m.fresh_median_ns;
        calibrated.occupancy1_total_ns += m.occupancy1_median_ns;
        calibrated.occupancy4_total_ns += m.occupancy4_median_ns;
        if (m.occupancy4_faster_than_fresh)
            calibrated.beneficial_repeat_count += 1U;
    }

    std::sort(fresh_values.begin(), fresh_values.end());
    std::sort(occupancy1_values.begin(), occupancy1_values.end());
    std::sort(occupancy4_values.begin(), occupancy4_values.end());
    calibrated.fresh_median_ns =
        fresh_values[kCalibrationRepeats / 2U];
    calibrated.occupancy1_median_ns =
        occupancy1_values[kCalibrationRepeats / 2U];
    calibrated.occupancy4_median_ns =
        occupancy4_values[kCalibrationRepeats / 2U];
    calibrated.aggregate_benefit =
        calibrated.occupancy4_total_ns < calibrated.fresh_total_ns;
    calibrated.repeat_stability_pass =
        calibrated.beneficial_repeat_count >=
            kRequiredBeneficialRepeats &&
        calibrated.aggregate_benefit;
    calibrated.occupancy4_vs_fresh_x1000 =
        ratio_x1000(
            calibrated.fresh_total_ns,
            calibrated.occupancy4_total_ns);
    calibrated.occupancy4_vs_occupancy1_x1000 =
        ratio_x1000(
            calibrated.occupancy4_total_ns,
            calibrated.occupancy1_total_ns);
    return calibrated;
}

}  // namespace

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    std::cerr << "residency benchmark requires Linux x86_64\n";
    return 2;
#else
    const auto specs = resident_specs();
    std::array<HHSExactPass219H36StackCandidateEvidenceV1, kResidents> h36{};
    std::array<HHSExactPass219H36StackCandidateEvidenceV1, kResidents> linux{};
    std::array<HHSExactPass219H36StackSelectionV1, kResidents> selections{};
    std::array<HHSExactPass219H36StackCacheV1, kResidents> occupancy1{};
    HHSExactPass219H36StackCacheV1 occupancy4{};

    if (hhs_exact_pass219_h36_stack_cache_init(&occupancy4) !=
        HHS_EXACT_STATUS_OK)
        return 3;

    for (std::size_t i = 0U; i < kResidents; ++i) {
        prepare_selection(specs[i], h36[i], linux[i], selections[i]);
        if (hhs_exact_pass219_h36_stack_cache_init(&occupancy1[i]) !=
                HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_stack_cache_store(
                &occupancy1[i], &selections[i]) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_stack_cache_store(
                &occupancy4, &selections[i]) != HHS_EXACT_STATUS_OK)
            return 4;
    }

    if (occupancy4.entry_count != 4U ||
        occupancy4.next_sequence != UINT64_C(5) ||
        hhs_exact_pass219_h36_stack_cache_validate(
            &occupancy4) != HHS_EXACT_STATUS_OK)
        return 5;

    const std::uint32_t before_count = occupancy4.entry_count;
    const std::uint64_t before_sequence = occupancy4.next_sequence;
    if (hhs_exact_pass219_h36_stack_cache_store(
            &occupancy4, &selections[0]) != HHS_EXACT_STATUS_OK ||
        occupancy4.entry_count != before_count ||
        occupancy4.next_sequence != before_sequence)
        return 6;

    prove_isolation(occupancy4, selections);

    std::array<CalibratedResidency, kResidents> measurements{};
    bool all_repeat_stability_pass = true;
    for (std::size_t i = 0U; i < kResidents; ++i) {
        measurements[i] = calibrate_resident(
            h36[i], linux[i], selections[i], occupancy1[i], occupancy4);
        all_repeat_stability_pass =
            all_repeat_stability_pass &&
            measurements[i].repeat_stability_pass;
    }

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file)
            return 7;
        out = &file;
    }

    *out
        << "{\n"
        << "  \"schema\": \"HHS_PASS219_H36_STACK_CACHE_RESIDENCY_1_13_BENCHMARK_V1\",\n"
        << "  \"platform\": {\"linux\": true, \"x86_64\": true, "
        << "\"samples\": " << kSamples << ", "
        << "\"rounds_per_sample\": " << kRoundsPerSample << ", "
        << "\"calibration_repeats\": " << kCalibrationRepeats << ", "
        << "\"required_beneficial_repeats\": "
        << kRequiredBeneficialRepeats << "},\n"
        << "  \"cache\": {\"capacity\": 8, \"resident_entries\": 4, "
        << "\"next_sequence\": " << occupancy4.next_sequence << "},\n"
        << "  \"correctness\": {\n"
        << "    \"four_simultaneous_entries_valid\": true,\n"
        << "    \"all_exact_lookups_equal_fresh\": true,\n"
        << "    \"deterministic_receipts\": true,\n"
        << "    \"cross_signature_hits_rejected\": true,\n"
        << "    \"wrong_semantic_signature_rejected\": true,\n"
        << "    \"wrong_vector_key_rejected\": true,\n"
        << "    \"unrelated_identity_range_error\": true,\n"
        << "    \"duplicate_sequence_rejected\": true,\n"
        << "    \"duplicate_identity_tamper_rejected\": true,\n"
        << "    \"partial_identity_tamper_rejected\": true,\n"
        << "    \"idempotent_store_preserves_count_and_sequence\": true\n"
        << "  },\n"
        << "  \"residents\": [\n";

    for (std::size_t i = 0U; i < kResidents; ++i) {
        const auto &spec = specs[i];
        const auto &selection = selections[i];
        const auto &m = measurements[i];
        *out
            << "    {\n"
            << "      \"name\": \"" << spec.name << "\",\n"
            << "      \"workload_signature36\": "
            << spec.workload_signature36 << ",\n"
            << "      \"semantic_result_signature64\": "
            << spec.semantic_signature64 << ",\n"
            << "      \"selected_candidate_id\": "
            << selection.selected_candidate_id << ",\n"
            << "      \"vector_key216\": \""
            << selection.selected_vector_key216 << "\",\n"
            << "      \"entry_sequence_occupancy4\": "
            << occupancy4.entries[i].sequence << ",\n"
            << "      \"fresh_selection_median_ns\": "
            << m.fresh_median_ns << ",\n"
            << "      \"occupancy1_lookup_median_ns\": "
            << m.occupancy1_median_ns << ",\n"
            << "      \"occupancy4_lookup_median_ns\": "
            << m.occupancy4_median_ns << ",\n"
            << "      \"fresh_selection_total_ns\": "
            << m.fresh_total_ns << ",\n"
            << "      \"occupancy1_lookup_total_ns\": "
            << m.occupancy1_total_ns << ",\n"
            << "      \"occupancy4_lookup_total_ns\": "
            << m.occupancy4_total_ns << ",\n"
            << "      \"beneficial_repeat_count\": "
            << m.beneficial_repeat_count << ",\n"
            << "      \"aggregate_benefit\": "
            << (m.aggregate_benefit ? "true" : "false") << ",\n"
            << "      \"repeat_stability_pass\": "
            << (m.repeat_stability_pass ? "true" : "false") << ",\n"
            << "      \"occupancy4_vs_fresh_ratio_x1000\": "
            << m.occupancy4_vs_fresh_x1000 << ",\n"
            << "      \"occupancy4_vs_occupancy1_ratio_x1000\": "
            << m.occupancy4_vs_occupancy1_x1000 << ",\n"
            << "      \"repeat_measurements\": [\n";
        for (std::size_t repeat = 0U;
             repeat < kCalibrationRepeats;
             ++repeat) {
            const auto &rm = m.repeats[repeat];
            *out
                << "        {\"repeat\": " << repeat + 1U
                << ", \"measurement_order\": \""
                << (((repeat & 1U) == 0U)
                    ? "FRESH_OCC1_OCC4"
                    : "OCC4_OCC1_FRESH")
                << "\", \"fresh_ns\": " << rm.fresh_median_ns
                << ", \"occupancy1_ns\": "
                << rm.occupancy1_median_ns
                << ", \"occupancy4_ns\": "
                << rm.occupancy4_median_ns
                << ", \"occupancy4_faster_than_fresh\": "
                << (rm.occupancy4_faster_than_fresh
                    ? "true" : "false")
                << "}"
                << (repeat + 1U == kCalibrationRepeats
                    ? "\n" : ",\n");
        }
        *out
            << "      ]\n"
            << "    }" << (i + 1U == kResidents ? "\n" : ",\n");
    }

    *out
        << "  ],\n"
        << "  \"measurement\": {\n"
        << "    \"gate_kind\": "
        << "\"EXACT_INTEGER_REPEAT_STABILITY\",\n"
        << "    \"calibration_repeats\": "
        << kCalibrationRepeats << ",\n"
        << "    \"required_beneficial_repeats\": "
        << kRequiredBeneficialRepeats << ",\n"
        << "    \"aggregate_requires_occupancy4_total_lt_fresh_total\": "
        << "true,\n"
        << "    \"all_repeat_stability_pass\": "
        << (all_repeat_stability_pass ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"authority\": {\n"
        << "    \"vm81_mutation\": false,\n"
        << "    \"vm81_admission_bypass\": false,\n"
        << "    \"hash72\": false,\n"
        << "    \"hash216\": false,\n"
        << "    \"persistence\": false,\n"
        << "    \"floating_point\": false\n"
        << "  },\n"
        << "  \"authoritative_state_changed\": false\n"
        << "}\n";

    return 0;
#endif
}
