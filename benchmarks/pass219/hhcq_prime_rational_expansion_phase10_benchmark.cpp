#define main hhs_pass219_phase9_reference_main
#include "hhcq_reciprocal_economy_phase9_benchmark.cpp"
#undef main

namespace {

constexpr std::array<std::uint16_t, 24> kPhase10Primes = {{
    2U, 3U, 5U, 7U, 11U, 13U, 17U, 19U,
    23U, 29U, 31U, 37U, 41U, 43U, 47U, 53U,
    59U, 61U, 67U, 71U, 73U, 79U, 83U, 89U
}};

std::uint32_t digest_byte10(const std::string& digest, std::size_t byte_index) {
    const std::size_t offset = (byte_index * 2U) % digest.size();
    const int hi = hex_value(digest[offset]);
    const int lo = hex_value(digest[(offset + 1U) % digest.size()]);
    if (hi < 0 || lo < 0) return 0U;
    return static_cast<std::uint32_t>((hi << 4) | lo);
}

void phase_pair10(
    const std::string& digest,
    std::size_t anchor,
    std::uint16_t& p,
    std::uint16_t& q,
    std::uint8_t& x,
    std::uint8_t& y
) {
    const std::uint32_t b0 = digest_byte10(digest, 0U);
    const std::uint32_t b1 = digest_byte10(digest, 1U);
    const std::uint32_t b2 = digest_byte10(digest, 2U);
    const std::uint32_t b3 = digest_byte10(digest, 3U);
    std::size_t pi = (b0 + anchor) % kPhase10Primes.size();
    std::size_t qi = (b1 + 2U * anchor + 1U) % kPhase10Primes.size();
    if (qi == pi) qi = (qi + 1U) % kPhase10Primes.size();
    p = kPhase10Primes[pi];
    q = kPhase10Primes[qi];
    x = static_cast<std::uint8_t>((b2 + 5U * anchor) % 72U);
    y = static_cast<std::uint8_t>((b3 + 7U * anchor) % 72U);
    if (x == 0U && y == 0U) y = 1U;
}

HHSExactPass219HHCQPrimeRationalCandidateV1 direct_candidate10(
    const HHSExactPass219HHCQPreparedLocalV1& prepared,
    std::uint16_t p,
    std::uint16_t q,
    std::uint8_t x,
    std::uint8_t y,
    std::uint32_t route_id
) {
    HHSExactPass219HHCQPrimeRationalCandidateV1 c{};
    c.struct_size = static_cast<std::uint32_t>(sizeof(c));
    c.version = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION;
    c.route_id = route_id;
    c.prime_p = p;
    c.prime_q = q;
    c.x_phase72 = x;
    c.y_phase72 = y;
    c.intrinsic_resolution_index = prepared.resolution.resolution_index;
    c.effective_resolution_index = prepared.resolution.resolution_index;
    c.required_resolution_index = prepared.resolution.resolution_index;
    c.latency_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.memory_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.compression_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.translation_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.exact_semantic_closure = 1U;
    c.exact_reconstruction = 1U;
    c.all_native_modalities_translatable = 1U;
    c.one_step_translation = 1U;
    c.phase5_resolution_locked = 1U;
    c.candidate_only = 1U;
    return c;
}

bool lower_unproven_candidate10(
    const HHSExactPass219HHCQPreparedLocalV1& prepared,
    std::uint16_t factor,
    std::uint8_t x,
    std::uint8_t y,
    std::uint32_t route_id,
    HHSExactPass219HHCQPrimeRationalCandidateV1& out
) {
    const std::uint32_t required_parameters =
        static_cast<std::uint32_t>(prepared.resolution.resolution_parameters);
    const std::uint32_t target_parameters = required_parameters * factor;
    std::uint8_t intrinsic_index = 0U;
    if (factor != 2U && factor != 3U) return false;
    if (target_parameters > HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT ||
        !find_resolution_index9(target_parameters, intrinsic_index) ||
        intrinsic_index >= prepared.resolution.resolution_index)
        return false;

    const std::uint64_t coarse_units =
        HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS / factor;
    out = {};
    out.struct_size = static_cast<std::uint32_t>(sizeof(out));
    out.version = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION;
    out.route_id = route_id;
    out.prime_p = 2U;
    out.prime_q = 5U;
    out.x_phase72 = x;
    out.y_phase72 = y;
    out.intrinsic_resolution_index = intrinsic_index;
    out.effective_resolution_index = prepared.resolution.resolution_index;
    out.required_resolution_index = prepared.resolution.resolution_index;
    out.latency_units = coarse_units;
    out.memory_units = coarse_units;
    out.compression_units = coarse_units;
    out.translation_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    out.redundancy_spend_units = coarse_units;
    out.ecc_spend_units = coarse_units;
    out.lossy_information_units = static_cast<std::uint32_t>(
        HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS - coarse_units);
    out.recovered_information_units = out.lossy_information_units;
    out.exact_semantic_closure = 0U;
    out.exact_reconstruction = 0U;
    out.all_native_modalities_translatable = 0U;
    out.one_step_translation = 1U;
    out.phase5_resolution_locked = 1U;
    out.candidate_only = 1U;
    return true;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fprintf(stderr, "usage: %s <phase3-frame-binary>\n", argv[0]);
        return 2;
    }

    HHSExactPass219HHCQPrimeRationalDescriptorV1 descriptor{};
    if (hhs_exact_pass219_hhcq_prime_rational_descriptor(&descriptor) !=
            HHS_EXACT_STATUS_OK ||
        descriptor.inherited_policy_state_bytes != 112U ||
        descriptor.source_bytes != 135U ||
        descriptor.economy_parity_units != 5184U ||
        descriptor.phase_modulus != 72U || descriptor.divisor_count != 35U ||
        descriptor.two_prime_rational_boundary != 1U ||
        descriptor.ab_equals_p4_constructor != 1U ||
        descriptor.reciprocal_ab_ba_closure != 1U ||
        descriptor.symbolic_polynomial_root_retained != 1U ||
        descriptor.exact_rational_cross_multiplication != 1U ||
        descriptor.monotone_resolution_expansion != 1U ||
        descriptor.exact_one_to_one_information_closure != 1U ||
        descriptor.phase5_resolution_locked != 1U ||
        descriptor.candidate_only != 1U ||
        descriptor.canonical_mutation_authority != 0U ||
        descriptor.canonical_hash72_authority != 0U ||
        descriptor.canonical_hash216_authority != 0U ||
        descriptor.canonical_persistence_authority != 0U ||
        descriptor.floating_point_authority != 0U)
        return 3;

    std::array<std::uint8_t, 35> exhaustive_resolution_seen{};
    std::array<std::uint8_t, 72> exhaustive_phase_seen{};
    for (std::uint32_t x = 0U; x < 72U; ++x) {
        for (std::uint32_t y = 0U; y < 72U; ++y) {
            if (x == 0U && y == 0U) continue;
            HHSExactPass219HHCQPrimeRationalExpansionV1 e{};
            if (hhs_exact_pass219_hhcq_prime_rational_expand(
                    2U, 3U, static_cast<std::uint8_t>(x),
                    static_cast<std::uint8_t>(y), 0U, &e) != HHS_EXACT_STATUS_OK)
                return 4;
            exhaustive_resolution_seen[e.polynomial_resolution_index] = 1U;
            exhaustive_phase_seen[e.expansion_phase72] = 1U;
        }
    }
    std::uint32_t exhaustive_resolution_coverage = 0U;
    std::uint32_t exhaustive_phase_coverage = 0U;
    for (std::uint8_t v : exhaustive_resolution_seen) exhaustive_resolution_coverage += v != 0U;
    for (std::uint8_t v : exhaustive_phase_seen) exhaustive_phase_coverage += v != 0U;
    if (exhaustive_resolution_coverage != 35U || exhaustive_phase_coverage != 72U)
        return 5;

    std::ifstream in(argv[1], std::ios::binary);
    if (!in) return 6;
    std::array<char, 8> magic{};
    if (!read_exact(in, magic.data(), magic.size()) ||
        std::string(magic.data(), magic.size()) != "HHS3WGT1") return 7;
    std::uint32_t version = 0U;
    std::uint32_t record_count = 0U;
    std::uint32_t checkpoint_count = 0U;
    std::uint32_t frame_kind_count = 0U;
    if (!read_u32_le(in, version) || !read_u32_le(in, record_count) ||
        !read_u32_le(in, checkpoint_count) || !read_u32_le(in, frame_kind_count)) return 8;
    if (version != kVersion || checkpoint_count != kCheckpointCount ||
        frame_kind_count != kFrameKindCount || record_count != 2116U) return 9;

    std::uint32_t summary_records = 0U;
    std::uint32_t local_samples = 0U;
    std::uint32_t phase5_roundtrip_checks = 0U;
    std::uint32_t expansion_replay_checks = 0U;
    std::uint32_t noncoarsening_checks = 0U;
    std::uint32_t finer_expansions = 0U;
    std::uint32_t equal_expansions = 0U;
    std::uint32_t direct_admitted = 0U;
    std::uint32_t factor2_candidates = 0U;
    std::uint32_t factor3_candidates = 0U;
    std::uint32_t unproven_candidates = 0U;
    std::uint32_t unproven_rational_bounds_met = 0U;
    std::uint32_t unproven_budget_positive = 0U;
    std::uint32_t unproven_information_one_to_one = 0U;
    std::uint32_t unproven_admitted = 0U;
    std::array<std::uint32_t, 35> authenticated_polynomial_resolution_counts{};
    std::array<std::uint32_t, 35> authenticated_expanded_resolution_counts{};
    std::set<std::string> unique_digests;
    std::uint64_t signature = UINT64_C(0x219ab10c5e00130);

    for (std::uint32_t i = 0U; i < record_count; ++i) {
        Record record{};
        if (!read_record(in, record)) return 10;
        if (record.frame_kind != kSummaryFrameKind) continue;
        ++summary_records;
        unique_digests.insert(record.chunk_digest);
        HHSExactVM81Frame frame{};
        HHSExactPass219CoreCircuitFeaturesV1 core{};
        if (!import_frame(record, frame)) return 11;
        if (hhs_exact_pass219_core_circuit_extract(&frame, &core) != HHS_EXACT_STATUS_OK)
            return 12;

        for (std::size_t anchor = 0U; anchor < kAnchorCount; ++anchor) {
            HHSExactPass219HHCQPreparedLocalV1 prepared{};
            if (!prepare_local(frame, core, anchor, prepared)) return 13;
            if (!phase5_roundtrip_exact(frame, prepared)) return 14;
            ++phase5_roundtrip_checks;

            std::uint16_t p = 0U;
            std::uint16_t q = 0U;
            std::uint8_t x = 0U;
            std::uint8_t y = 0U;
            phase_pair10(record.chunk_digest, anchor, p, q, x, y);
            HHSExactPass219HHCQPrimeRationalExpansionV1 expansion_a{};
            HHSExactPass219HHCQPrimeRationalExpansionV1 expansion_b{};
            if (hhs_exact_pass219_hhcq_prime_rational_expand(
                    p, q, x, y, prepared.resolution.resolution_index, &expansion_a) !=
                    HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_hhcq_prime_rational_expand(
                    p, q, x, y, prepared.resolution.resolution_index, &expansion_b) !=
                    HHS_EXACT_STATUS_OK ||
                std::memcmp(&expansion_a, &expansion_b, sizeof(expansion_a)) != 0)
                return 15;
            ++expansion_replay_checks;
            if (expansion_a.noncoarsening != 1U ||
                expansion_a.expanded_resolution_index < prepared.resolution.resolution_index ||
                static_cast<std::uint32_t>(expansion_a.expanded_resolution_parameters) *
                    static_cast<std::uint32_t>(expansion_a.expanded_region_count) != 5184U ||
                expansion_a.product_ab_equals_p4 != 1U ||
                expansion_a.sqrt_ab_equals_p2 != 1U ||
                expansion_a.reciprocal_product_equals_one != 1U ||
                expansion_a.polynomial_fraction_reduced != 1U ||
                expansion_a.symbolic_sqrt_a_times_b_retained != 1U ||
                expansion_a.canonical_authority_changed != 0U ||
                expansion_a.floating_point_authority != 0U)
                return 16;
            ++noncoarsening_checks;
            if (expansion_a.expanded_resolution_index > prepared.resolution.resolution_index)
                ++finer_expansions;
            else
                ++equal_expansions;
            ++authenticated_polynomial_resolution_counts[expansion_a.polynomial_resolution_index];
            ++authenticated_expanded_resolution_counts[expansion_a.expanded_resolution_index];

            HHSExactPass219HHCQPrimeRationalCandidateV1 direct = direct_candidate10(
                prepared, p, q, x, y,
                UINT32_C(100000) + local_samples);
            HHSExactPass219HHCQPrimeRationalResultV1 direct_result{};
            if (hhs_exact_pass219_hhcq_prime_rational_evaluate(
                    &direct, &direct_result) != HHS_EXACT_STATUS_OK ||
                direct_result.decision != HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_ADMITTED ||
                direct_result.rational_bounds_met != 1U ||
                direct_result.information_one_to_one != 1U ||
                direct_result.expanded_resolution_met != 1U ||
                direct_result.net_budget_units != 0 ||
                direct_result.canonical_authority_changed != 0U ||
                direct_result.floating_point_authority != 0U)
                return 17;
            ++direct_admitted;
            signature ^= direct_result.result_signature64 + UINT64_C(0x9e3779b97f4a7c15);

            HHSExactPass219HHCQPrimeRationalCandidateV1 lower{};
            if (lower_unproven_candidate10(
                    prepared, 2U, x, y, UINT32_C(200002), lower)) {
                HHSExactPass219HHCQPrimeRationalResultV1 r{};
                if (hhs_exact_pass219_hhcq_prime_rational_evaluate(&lower, &r) !=
                    HHS_EXACT_STATUS_OK) return 18;
                ++factor2_candidates;
                ++unproven_candidates;
                if (r.rational_bounds_met != 0U) ++unproven_rational_bounds_met;
                if (r.budget_nonnegative != 0U) ++unproven_budget_positive;
                if (r.information_one_to_one != 0U) ++unproven_information_one_to_one;
                if (r.decision == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_ADMITTED)
                    ++unproven_admitted;
                signature ^= r.result_signature64;
            }
            if (lower_unproven_candidate10(
                    prepared, 3U, x, y, UINT32_C(200003), lower)) {
                HHSExactPass219HHCQPrimeRationalResultV1 r{};
                if (hhs_exact_pass219_hhcq_prime_rational_evaluate(&lower, &r) !=
                    HHS_EXACT_STATUS_OK) return 19;
                ++factor3_candidates;
                ++unproven_candidates;
                if (r.rational_bounds_met != 0U) ++unproven_rational_bounds_met;
                if (r.budget_nonnegative != 0U) ++unproven_budget_positive;
                if (r.information_one_to_one != 0U) ++unproven_information_one_to_one;
                if (r.decision == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_ADMITTED)
                    ++unproven_admitted;
                signature ^= r.result_signature64;
            }
            ++local_samples;
        }
    }

    if (summary_records != 529U || local_samples != 4761U ||
        phase5_roundtrip_checks != 4761U || expansion_replay_checks != 4761U ||
        noncoarsening_checks != 4761U || direct_admitted != 4761U ||
        unique_digests.size() != 489U ||
        factor2_candidates == 0U || factor3_candidates == 0U ||
        unproven_candidates == 0U ||
        unproven_rational_bounds_met != unproven_candidates ||
        unproven_budget_positive != unproven_candidates ||
        unproven_information_one_to_one != unproven_candidates ||
        unproven_admitted != 0U || finer_expansions == 0U)
        return 20;

    std::uint32_t authenticated_polynomial_resolution_diversity = 0U;
    std::uint32_t authenticated_expanded_resolution_diversity = 0U;
    for (std::size_t i = 0U; i < 35U; ++i) {
        if (authenticated_polynomial_resolution_counts[i] != 0U)
            ++authenticated_polynomial_resolution_diversity;
        if (authenticated_expanded_resolution_counts[i] != 0U)
            ++authenticated_expanded_resolution_diversity;
    }

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_HHCQ_PRIME_RATIONAL_EXPANSION_PHASE10_V1\",\n");
    std::printf("  \"classification\": \"PRIME_RATIONAL_EXPANSION_FAIL_CLOSED_PRE_RECONSTRUCTION\",\n");
    std::printf("  \"phase3_frame_binary_sha256\": \"63d0f8816d4c04e10eb5d9644c9c60015b8cdd3b1235f114b3f1821ef08a3433\",\n");
    std::printf("  \"extension_source_bytes\": 135,\n");
    std::printf("  \"extension_source_sha256\": \"6d91bf7d4a70edf34ec5cd30a4ea7d04cc08af5013f7631576b118c369b2ea14\",\n");
    std::printf("  \"economy_parity_units\": 5184,\n");
    std::printf("  \"exhaustive_phase72_coverage\": %u,\n", exhaustive_phase_coverage);
    std::printf("  \"exhaustive_phase5_resolution_coverage\": %u,\n", exhaustive_resolution_coverage);
    std::printf("  \"summary_records\": %u,\n", summary_records);
    std::printf("  \"authenticated_unique_digests\": %zu,\n", unique_digests.size());
    std::printf("  \"local_samples\": %u,\n", local_samples);
    std::printf("  \"phase5_exact_roundtrip_checks\": %u,\n", phase5_roundtrip_checks);
    std::printf("  \"expansion_replay_checks\": %u,\n", expansion_replay_checks);
    std::printf("  \"noncoarsening_checks\": %u,\n", noncoarsening_checks);
    std::printf("  \"finer_expansions\": %u,\n", finer_expansions);
    std::printf("  \"equal_expansions\": %u,\n", equal_expansions);
    std::printf("  \"authenticated_polynomial_resolution_diversity\": %u,\n",
                authenticated_polynomial_resolution_diversity);
    std::printf("  \"authenticated_expanded_resolution_diversity\": %u,\n",
                authenticated_expanded_resolution_diversity);
    std::printf("  \"direct_lossless_admitted\": %u,\n", direct_admitted);
    std::printf("  \"factor2_lower_resolution_candidates\": %u,\n", factor2_candidates);
    std::printf("  \"factor3_lower_resolution_candidates\": %u,\n", factor3_candidates);
    std::printf("  \"unproven_lower_resolution_candidates\": %u,\n", unproven_candidates);
    std::printf("  \"unproven_rational_bounds_met\": %u,\n", unproven_rational_bounds_met);
    std::printf("  \"unproven_budget_positive\": %u,\n", unproven_budget_positive);
    std::printf("  \"unproven_information_1to1\": %u,\n", unproven_information_one_to_one);
    std::printf("  \"unproven_admitted\": %u,\n", unproven_admitted);
    std::printf("  \"ab_equals_p4_constructor\": true,\n");
    std::printf("  \"reciprocal_ab_ba_closure\": true,\n");
    std::printf("  \"symbolic_sqrt_a_times_b_retained\": true,\n");
    std::printf("  \"lower_resolution_execution_measured\": false,\n");
    std::printf("  \"exact_reconstruction_required_before_admission\": true,\n");
    std::printf("  \"fixed_policy_state_bytes\": 112,\n");
    std::printf("  \"candidate_only\": true,\n");
    std::printf("  \"canonical_authority_changed\": false,\n");
    std::printf("  \"floating_point_authority\": false,\n");
    std::printf("  \"signature64\": \"%llu\"\n",
                static_cast<unsigned long long>(signature));
    std::printf("}\n");
    return 0;
}
