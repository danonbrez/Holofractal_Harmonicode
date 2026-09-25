#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_sink = 0U;

struct Selection {
    bool ok = false;
    std::uint32_t index = std::numeric_limits<std::uint32_t>::max();
    std::uint64_t descriptor_signature64 = 0U;
    std::uint64_t validation_count = 0U;
    std::uint32_t phase_distance_squared = 0U;
};

struct Key {
    std::uint32_t phase_distance_squared;
    std::uint64_t cost;
    std::uint64_t represented_span;
    std::uint64_t route_signature;
};

constexpr std::array<std::uint32_t, 4> kQuarterPhases{{0U, 18U, 36U, 54U}};

std::uint32_t circular_distance_squared(std::uint32_t phase, std::uint32_t target) {
    const std::uint32_t cycle = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_CYCLE;
    const std::uint32_t forward = (phase + cycle - target) % cycle;
    const std::uint32_t reverse = (target + cycle - phase) % cycle;
    const std::uint32_t distance = std::min(forward, reverse);
    return distance * distance;
}

Key key_for(const HHSExactPass219Lane5DirectWitnessRouteV1 &route, std::uint32_t target) {
    return Key{
        circular_distance_squared(route.phase_slot, target),
        route.integer_route_cost,
        route.represented_span,
        route.route_signature64,
    };
}

bool key_less(const Key &left, const Key &right) {
    if (left.phase_distance_squared != right.phase_distance_squared)
        return left.phase_distance_squared < right.phase_distance_squared;
    if (left.cost != right.cost)
        return left.cost < right.cost;
    if (left.represented_span != right.represented_span)
        return left.represented_span > right.represented_span;
    return left.route_signature < right.route_signature;
}

HHSExactPass219Lane5DirectWitnessRouteV1 make_route(
    std::uint32_t index,
    std::uint32_t champion_index
) {
    HHSExactPass219Lane5DirectWitnessRouteV1 route{};
    const std::uint32_t phase = kQuarterPhases[index % kQuarterPhases.size()];

    route.struct_size = sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION;
    route.previous_signature64 = UINT64_C(0x1000000000000000) + index + 1U;
    route.current_signature64 = UINT64_C(0x2000000000000000) + index + 1U;
    route.provenance_signature64 = UINT64_C(0x3000000000000000) + index + 1U;
    route.goal_signature64 = UINT64_C(0x4000000000000001);
    route.forbidden_boundary_signature64 = UINT64_C(0x5000000000000000) + index + 1U;
    route.reciprocal_inverse_signature64 = UINT64_C(0x6000000000000000) + index + 1U;
    route.candidate_signature64 = route.goal_signature64;
    route.route_signature64 = UINT64_C(0xF000000000000000) - index;
    route.represented_span = (static_cast<std::uint64_t>(index) + 1U) * UINT64_C(1000000);
    route.evidence_count = 5U;
    route.contradiction_check_count = index == champion_index ? 1U : 2U;
    route.integer_route_cost =
        static_cast<std::uint64_t>(route.evidence_count) +
        static_cast<std::uint64_t>(route.contradiction_check_count) + 1U;
    route.materialized_intermediate_states = 0U;
    route.phase_slot = phase;
    route.inverse_phase_slot =
        (phase + HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_HALF) %
        HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_CYCLE;
    route.trinary_collapse = static_cast<std::int8_t>((index % 3U) - 1);
    route.binary_collapse = static_cast<std::uint8_t>(index % 2U);
    route.nested_zero_slot = route.binary_collapse == 0U ? 1U : 0U;
    route.replay_witness_verified = 1U;
    route.exact_goal_reached = 1U;
    route.contradiction_free = 1U;
    route.goal_forbidden_conflict = 0U;
    route.reciprocal_phase_verified = 1U;
    route.bigint_serialization_addressed = 1U;
    route.candidate_only = 1U;
    route.canonical_mutation_authority = 0U;
    route.canonical_hash72_authority = 0U;
    route.canonical_hash216_authority = 0U;
    route.canonical_persistence_authority = 0U;
    route.pqc_key_authority = 0U;
    route.receipt_clock_authority = 0U;
    route.requires_signed_environmental_vm81_admission = 1U;
    return route;
}

std::uint32_t champion_for(std::uint32_t count, std::uint32_t target) {
    const auto it = std::find(kQuarterPhases.begin(), kQuarterPhases.end(), target);
    if (it == kQuarterPhases.end() || count < 4U || (count % 4U) != 0U)
        std::abort();
    const std::uint32_t target_offset =
        static_cast<std::uint32_t>(std::distance(kQuarterPhases.begin(), it));
    return count - 4U + target_offset;
}

std::vector<HHSExactPass219Lane5DirectWitnessRouteV1> make_workload(
    std::uint32_t count,
    std::uint32_t target
) {
    const std::uint32_t champion = champion_for(count, target);
    std::vector<HHSExactPass219Lane5DirectWitnessRouteV1> routes;
    routes.reserve(count);
    for (std::uint32_t i = 0U; i < count; ++i)
        routes.push_back(make_route(i, champion));
    return routes;
}

Selection exhaustive_updated_objective(
    const std::vector<HHSExactPass219Lane5DirectWitnessRouteV1> &routes,
    std::uint32_t target
) {
    Selection selection{};
    Key best{};
    bool have_best = false;

    for (std::uint32_t i = 0U; i < routes.size(); ++i) {
        HHSExactPass219Lane5DirectWitnessReceiptV1 receipt{};
        ++selection.validation_count;
        if (hhs_exact_pass219_lane5_direct_witness_route_validate(
                &routes[i], &receipt) != HHS_EXACT_STATUS_OK)
            continue;

        const Key candidate_key = key_for(routes[i], target);
        if (!have_best || key_less(candidate_key, best)) {
            have_best = true;
            best = candidate_key;
            selection.ok = true;
            selection.index = i;
            selection.descriptor_signature64 = receipt.descriptor_signature64;
            selection.phase_distance_squared = candidate_key.phase_distance_squared;
        }
    }
    return selection;
}

Selection circular_attractor_fast_path(
    const std::vector<HHSExactPass219Lane5DirectWitnessRouteV1> &routes,
    std::uint32_t target
) {
    Selection selection{};
    std::uint32_t candidate_index = 0U;
    Key best = key_for(routes[0], target);
    for (std::uint32_t i = 1U; i < routes.size(); ++i) {
        const Key candidate = key_for(routes[i], target);
        if (key_less(candidate, best)) {
            best = candidate;
            candidate_index = i;
        }
    }

    HHSExactPass219Lane5DirectWitnessReceiptV1 receipt{};
    selection.validation_count = 1U;
    if (hhs_exact_pass219_lane5_direct_witness_route_validate(
            &routes[candidate_index], &receipt) == HHS_EXACT_STATUS_OK) {
        selection.ok = true;
        selection.index = candidate_index;
        selection.descriptor_signature64 = receipt.descriptor_signature64;
        selection.phase_distance_squared = best.phase_distance_squared;
        return selection;
    }

    Selection fallback = exhaustive_updated_objective(routes, target);
    fallback.validation_count += 1U;
    return fallback;
}

template <typename Fn>
std::uint64_t median_batch_ns(Fn &&fn, std::uint32_t repetitions) {
    fn();
    std::vector<std::uint64_t> samples;
    samples.reserve(repetitions);
    for (std::uint32_t i = 0U; i < repetitions; ++i) {
        const auto begin = Clock::now();
        fn();
        const auto end = Clock::now();
        samples.push_back(static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin).count()));
    }
    std::sort(samples.begin(), samples.end());
    return samples[samples.size() / 2U];
}

std::uint32_t tier_for(std::uint64_t ns) {
    std::uint32_t tier = 0U;
    if (hhs_exact_pass219_global_latency_classify_ns(ns, &tier) != HHS_EXACT_STATUS_OK)
        std::abort();
    return tier;
}

void require(bool condition, const char *message) {
    if (!condition) {
        std::cerr << message << "\n";
        std::exit(2);
    }
}

struct CaseResult {
    std::uint32_t candidate_count;
    std::uint32_t target_phase;
    std::uint32_t iterations;
    std::uint32_t selected_index;
    std::uint32_t phase_distance_squared;
    std::uint64_t exhaustive_validations;
    std::uint64_t attractor_validations;
    std::uint64_t exhaustive_batch_ns;
    std::uint64_t attractor_batch_ns;
    std::uint64_t exhaustive_mean_ns_floor;
    std::uint64_t attractor_mean_ns_floor;
    std::uint64_t speedup_x1000;
    std::uint64_t validation_reduction_x1000;
    std::uint32_t exhaustive_tier;
    std::uint32_t attractor_tier;
};

CaseResult run_case(
    std::uint32_t count,
    std::uint32_t target,
    std::uint32_t iterations
) {
    auto routes = make_workload(count, target);
    const Selection exhaustive = exhaustive_updated_objective(routes, target);
    const Selection attractor = circular_attractor_fast_path(routes, target);
    const std::uint32_t expected = champion_for(count, target);

    require(exhaustive.ok && attractor.ok, "selection failed");
    require(exhaustive.index == attractor.index, "attractor/exhaustive selected-index mismatch");
    require(exhaustive.index == expected, "unexpected selected candidate");
    require(exhaustive.descriptor_signature64 == attractor.descriptor_signature64,
            "attractor/exhaustive descriptor mismatch");
    require(exhaustive.phase_distance_squared == 0U &&
            attractor.phase_distance_squared == 0U,
            "selected route is not at circular attractor closure");
    require(exhaustive.validation_count == count, "exhaustive validation count drift");
    require(attractor.validation_count == 1U, "attractor fast path did not close in one proof validation");

    const auto exhaustive_batch = median_batch_ns([&]() {
        std::uint64_t sink = 0U;
        for (std::uint32_t i = 0U; i < iterations; ++i) {
            const Selection s = exhaustive_updated_objective(routes, target);
            if (!s.ok || s.index != expected)
                std::abort();
            sink ^= s.descriptor_signature64 + s.index;
        }
        g_sink ^= sink;
    }, 7U);

    const auto attractor_batch = median_batch_ns([&]() {
        std::uint64_t sink = 0U;
        for (std::uint32_t i = 0U; i < iterations; ++i) {
            const Selection s = circular_attractor_fast_path(routes, target);
            if (!s.ok || s.index != expected)
                std::abort();
            sink ^= s.descriptor_signature64 + s.index;
        }
        g_sink ^= sink;
    }, 7U);

    const std::uint64_t exhaustive_mean = exhaustive_batch / iterations;
    const std::uint64_t attractor_mean = attractor_batch / iterations;

    return CaseResult{
        count,
        target,
        iterations,
        expected,
        0U,
        exhaustive.validation_count,
        attractor.validation_count,
        exhaustive_batch,
        attractor_batch,
        exhaustive_mean,
        attractor_mean,
        (exhaustive_batch * UINT64_C(1000)) /
            (attractor_batch == 0U ? UINT64_C(1) : attractor_batch),
        (exhaustive.validation_count * UINT64_C(1000)) /
            (attractor.validation_count == 0U ? UINT64_C(1) : attractor.validation_count),
        tier_for(exhaustive_mean),
        tier_for(attractor_mean),
    };
}

void run_negative_fallback_control() {
    auto routes = make_workload(256U, 0U);
    const std::uint32_t champion = champion_for(256U, 0U);

    routes[0].phase_slot = 0U;
    routes[0].inverse_phase_slot = 36U;
    routes[0].contradiction_check_count = 1U;
    routes[0].integer_route_cost = 6U;  // impossible: full validator must reject.
    routes[0].represented_span = routes[champion].represented_span + UINT64_C(1);

    const Selection exhaustive = exhaustive_updated_objective(routes, 0U);
    const Selection attractor = circular_attractor_fast_path(routes, 0U);
    require(exhaustive.ok && attractor.ok, "negative fallback did not recover");
    require(exhaustive.index == champion && attractor.index == champion,
            "negative fallback selected wrong route");
    require(exhaustive.descriptor_signature64 == attractor.descriptor_signature64,
            "negative fallback descriptor mismatch");
    require(attractor.validation_count == 257U,
            "negative fallback did not invoke fail-closed exhaustive recovery");

    auto authority_tamper = make_workload(64U, 18U);
    const std::uint32_t best = champion_for(64U, 18U);
    authority_tamper[best].canonical_hash216_authority = 1U;
    const Selection exhaustive2 = exhaustive_updated_objective(authority_tamper, 18U);
    const Selection attractor2 = circular_attractor_fast_path(authority_tamper, 18U);
    require(exhaustive2.ok && attractor2.ok, "authority fallback did not recover");
    require(exhaustive2.index == attractor2.index,
            "authority fallback semantic mismatch");
    require(attractor2.index != best,
            "candidate requesting Hash216 authority was not rejected");
}

}  // namespace

int main(int argc, char **argv) {
    require(hhs_exact_pass219_global_latency_policy_validate() == HHS_EXACT_STATUS_OK,
            "global 25/3 latency policy validation failed");

    HHSExactPass219Lane5DirectWitnessAuthorityV1 authority{};
    require(hhs_exact_pass219_lane5_direct_witness_routing_authority(&authority) ==
                HHS_EXACT_STATUS_OK,
            "Lane 5 direct-witness authority unavailable");
    require(authority.candidate_only == 1U, "Lane 5 candidate-only boundary drift");
    require(authority.canonical_vm81_mutation_authority == 0U,
            "Lane 5 VM81 authority drift");
    require(authority.canonical_hash72_authority == 0U,
            "Lane 5 Hash72 authority drift");
    require(authority.canonical_hash216_authority == 0U,
            "Lane 5 Hash216 authority drift");
    require(authority.floating_point_canonical_authority == 0U,
            "Lane 5 floating-point authority drift");

    run_negative_fallback_control();

    constexpr std::array<std::uint32_t, 4> counts{{64U, 256U, 1024U, 4096U}};
    constexpr std::array<std::uint32_t, 4> iterations{{1000U, 300U, 80U, 20U}};

    std::vector<CaseResult> results;
    for (std::size_t ci = 0U; ci < counts.size(); ++ci) {
        for (const std::uint32_t target : kQuarterPhases)
            results.push_back(run_case(counts[ci], target, iterations[ci]));
    }

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        require(static_cast<bool>(file), "unable to open output file");
        out = &file;
    }

    *out << "{\n"
         << "  \"schema\": \"HHS_PASS219_LANE5_CIRCULAR_ATTRACTOR_GLOBAL_OPTIMIZER_BENCHMARK_V1\",\n"
         << "  \"base_main\": \"85f7e072c966500e1da2d3b24d36d17ba9850b0b\",\n"
         << "  \"timing_clock\": \"std::chrono::steady_clock\",\n"
         << "  \"timing_is_canonical\": false,\n"
         << "  \"objective_order\": [\"circular_phase_distance_squared\",\"integer_route_cost\",\"represented_span_desc\",\"route_signature64\"],\n"
         << "  \"global_constraint_validation\": \"existing_native_direct_witness_validator\",\n"
         << "  \"attractor_fast_path_full_validations\": 1,\n"
         << "  \"negative_invalid_best_fallback_passed\": true,\n"
         << "  \"negative_authority_escalation_fallback_passed\": true,\n"
         << "  \"candidate_only\": true,\n"
         << "  \"canonical_vm81_mutation_authority\": false,\n"
         << "  \"canonical_hash72_authority\": false,\n"
         << "  \"canonical_hash216_authority\": false,\n"
         << "  \"floating_point_canonical_authority\": false,\n"
         << "  \"cases\": [\n";

    for (std::size_t i = 0U; i < results.size(); ++i) {
        const auto &r = results[i];
        *out << "    {"
             << "\"candidate_count\":" << r.candidate_count << ","
             << "\"target_phase\":" << r.target_phase << ","
             << "\"iterations\":" << r.iterations << ","
             << "\"selected_index\":" << r.selected_index << ","
             << "\"phase_distance_squared\":" << r.phase_distance_squared << ","
             << "\"exhaustive_full_validations\":" << r.exhaustive_validations << ","
             << "\"attractor_full_validations\":" << r.attractor_validations << ","
             << "\"validation_reduction_x1000\":" << r.validation_reduction_x1000 << ","
             << "\"exhaustive_batch_median_ns\":" << r.exhaustive_batch_ns << ","
             << "\"attractor_batch_median_ns\":" << r.attractor_batch_ns << ","
             << "\"exhaustive_mean_ns_floor\":" << r.exhaustive_mean_ns_floor << ","
             << "\"attractor_mean_ns_floor\":" << r.attractor_mean_ns_floor << ","
             << "\"observed_speedup_x1000\":" << r.speedup_x1000 << ","
             << "\"exhaustive_latency_tier\":" << r.exhaustive_tier << ","
             << "\"attractor_latency_tier\":" << r.attractor_tier << ","
             << "\"exact_selected_route_equal\":true"
             << "}";
        if (i + 1U != results.size())
            *out << ",";
        *out << "\n";
    }

    *out << "  ],\n"
         << "  \"result\": \"PASS\"\n"
         << "}\n";

    return g_sink == UINT64_C(0xFFFFFFFFFFFFFFFF) ? 7 : 0;
}
