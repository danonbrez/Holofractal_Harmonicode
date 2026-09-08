#define main hhs_pass219_phase6_reference_main
#include "hhcq_joint_local_router_phase6_benchmark.cpp"
#undef main

namespace {

constexpr std::array<std::uint16_t, 24> kPhase11Primes = {{
    2U, 3U, 5U, 7U, 11U, 13U, 17U, 19U,
    23U, 29U, 31U, 37U, 41U, 43U, 47U, 53U,
    59U, 61U, 67U, 71U, 73U, 79U, 83U, 89U
}};

std::uint32_t digest_byte11(const std::string& digest, std::size_t byte_index) {
    const std::size_t offset = (byte_index * 2U) % digest.size();
    const int hi = hex_value(digest[offset]);
    const int lo = hex_value(digest[(offset + 1U) % digest.size()]);
    if (hi < 0 || lo < 0) return 0U;
    return static_cast<std::uint32_t>((hi << 4) | lo);
}

void prime_pair11(
    const std::string& digest,
    std::size_t anchor,
    std::uint16_t& p,
    std::uint16_t& q
) {
    const std::uint32_t b0 = digest_byte11(digest, 0U);
    const std::uint32_t b1 = digest_byte11(digest, 1U);
    std::size_t pi = (b0 + anchor) % kPhase11Primes.size();
    std::size_t qi = (b1 + 2U * anchor + 1U) % kPhase11Primes.size();
    if (qi == pi) qi = (qi + 1U) % kPhase11Primes.size();
    p = kPhase11Primes[pi];
    q = kPhase11Primes[qi];
}

bool phase11_surface_for(
    const HHSExactVM81Frame& frame,
    std::size_t anchor_index,
    HHSExactPass219OctonionSurfaceV1& out
) {
    const std::uint16_t anchor = anchor_for(anchor_index);
    const std::uint8_t cell = static_cast<std::uint8_t>(anchor / 64U);
    if (hhs_exact_pass219_octonion_from_vm81(
            &frame,
            cell,
            static_cast<std::uint8_t>((cell + 1U) % HHS_EXACT_VM81_CELLS),
            static_cast<std::uint8_t>((cell + 9U) % HHS_EXACT_VM81_CELLS),
            static_cast<std::uint8_t>((cell + 10U) % HHS_EXACT_VM81_CELLS),
            &out) != HHS_EXACT_STATUS_OK)
        return false;
    return hhs_exact_pass219_octonion_validate_surface(&out) == HHS_EXACT_STATUS_OK;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fprintf(stderr, "usage: %s <phase3-frame-binary>\n", argv[0]);
        return 2;
    }

    HHSExactPass219HHCQ8BasisParityDescriptorV1 descriptor{};
    if (hhs_exact_pass219_hhcq_8basis_parity_descriptor(&descriptor) !=
            HHS_EXACT_STATUS_OK ||
        descriptor.source_bytes != 700U ||
        descriptor.inherited_policy_state_bytes != 112U ||
        descriptor.a2 != 1U || descriptor.b2 != 2U || descriptor.c2 != 3U ||
        descriptor.update_quantum != 5U || descriptor.phase_modulus != 72U ||
        descriptor.parameter_count != 5184U || descriptor.basis_count != 8U ||
        descriptor.complete_8basis_equilibrium != 1U ||
        descriptor.ordered_noncommutative_products_preserved != 1U ||
        descriptor.exact_rational_macro_p != 1U ||
        descriptor.independent_equilibrium_validator != 1U ||
        descriptor.candidate_transport_delta_only != 1U ||
        descriptor.squared_coordinate_orientation_gate != 1U ||
        descriptor.x2_parity_equals_x_parity != 1U ||
        descriptor.symbolic_exponent_retained != 1U ||
        descriptor.ordinary_negative_base_exponent_evaluated != 0U ||
        descriptor.matrix_order_contract_preserved != 1U ||
        descriptor.phase10_prime_rational_semantics_inherited != 1U ||
        descriptor.candidate_only != 1U ||
        descriptor.canonical_mutation_authority != 0U ||
        descriptor.canonical_hash72_authority != 0U ||
        descriptor.canonical_hash216_authority != 0U ||
        descriptor.canonical_persistence_authority != 0U ||
        descriptor.floating_point_authority != 0U)
        return 3;

    std::uint32_t exhaustive_direct = 0U;
    std::uint32_t exhaustive_reversed = 0U;
    for (std::uint32_t x = 0U; x < 72U; ++x) {
        HHSExactPass219OctonionStateV1 state{};
        HHSExactPass219HHCQParityGateV1 gate{};
        if (hhs_exact_pass219_octonion_expand(
                static_cast<std::uint8_t>(x), 1U, 2U, 3U, &state) !=
                HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_octonion_validate_state(&state) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_hhcq_parity_gate(
                2U, 3U, &state, 0U, &gate) != HHS_EXACT_STATUS_OK ||
            gate.x_squared_parity != static_cast<std::uint8_t>(x & 1U) ||
            gate.x2_parity_identity_exact != 1U)
            return 4;
        if (gate.orientation == HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_DIRECT)
            ++exhaustive_direct;
        else if (gate.orientation == HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_REVERSED)
            ++exhaustive_reversed;
        else
            return 5;
    }
    if (exhaustive_direct != 36U || exhaustive_reversed != 36U)
        return 6;

    std::ifstream in(argv[1], std::ios::binary);
    if (!in) return 7;
    std::array<char, 8> magic{};
    if (!read_exact(in, magic.data(), magic.size()) ||
        std::string(magic.data(), magic.size()) != "HHS3WGT1") return 8;
    std::uint32_t version = 0U;
    std::uint32_t record_count = 0U;
    std::uint32_t checkpoint_count = 0U;
    std::uint32_t frame_kind_count = 0U;
    if (!read_u32_le(in, version) || !read_u32_le(in, record_count) ||
        !read_u32_le(in, checkpoint_count) || !read_u32_le(in, frame_kind_count)) return 9;
    if (version != kVersion || checkpoint_count != kCheckpointCount ||
        frame_kind_count != kFrameKindCount || record_count != 2116U) return 10;

    std::uint32_t summary_records = 0U;
    std::uint32_t local_samples = 0U;
    std::uint32_t phase5_roundtrip_checks = 0U;
    std::uint32_t full_surface_checks = 0U;
    std::uint32_t equilibrium_construct_checks = 0U;
    std::uint32_t independent_equilibrium_checks = 0U;
    std::uint32_t replay_checks = 0U;
    std::uint32_t matrix_order_checks = 0U;
    std::uint32_t phase10_product_closure_checks = 0U;
    std::uint32_t constraint_intersection_checks = 0U;
    std::uint32_t drift_detection_checks = 0U;
    std::uint32_t drift_fail_closed_checks = 0U;
    std::uint32_t integer_macro_p = 0U;
    std::uint32_t half_integer_macro_p = 0U;
    std::uint32_t authenticated_direct = 0U;
    std::uint32_t authenticated_reversed = 0U;
    std::set<std::string> unique_digests;
    std::uint64_t signature = UINT64_C(0x2198ba5115e00131);

    for (std::uint32_t i = 0U; i < record_count; ++i) {
        Record record{};
        if (!read_record(in, record)) return 11;
        if (record.frame_kind != kSummaryFrameKind) continue;
        ++summary_records;
        unique_digests.insert(record.chunk_digest);

        HHSExactVM81Frame frame{};
        HHSExactPass219CoreCircuitFeaturesV1 core{};
        if (!import_frame(record, frame)) return 12;
        if (hhs_exact_pass219_core_circuit_extract(&frame, &core) != HHS_EXACT_STATUS_OK)
            return 13;

        for (std::size_t anchor = 0U; anchor < kAnchorCount; ++anchor) {
            HHSExactPass219HHCQJointPreparedV1 prepared{};
            HHSExactPass219OctonionSurfaceV1 surface{};
            HHSExactPass219HHCQ8BasisEquilibriumV1 constructed{};
            HHSExactPass219HHCQ8BasisEquilibriumV1 independent{};
            HHSExactPass219HHCQ8BasisManifoldV1 state_a{};
            HHSExactPass219HHCQ8BasisManifoldV1 state_b{};
            HHSExactPass219HHCQ8BasisManifoldV1 vm_manifold{};
            HHSExactPass219HHCQ8BasisManifoldV1 drifted{};
            std::uint16_t p = 0U;
            std::uint16_t q = 0U;

            if (!prepare_local(frame, core, anchor, prepared)) return 14;
            if (!phase5_roundtrip_exact(frame, prepared)) return 15;
            ++phase5_roundtrip_checks;
            if (!phase11_surface_for(frame, anchor, surface)) return 16;
            ++full_surface_checks;

            prime_pair11(record.chunk_digest, anchor, p, q);
            if (hhs_exact_pass219_hhcq_8basis_equilibrium_construct(
                    p, q, &surface.state, &constructed) != HHS_EXACT_STATUS_OK ||
                constructed.equilibrium_exact != 1U ||
                constructed.transport_reconciliation_required != 0U ||
                constructed.canonical_authority_changed != 0U ||
                constructed.floating_point_authority != 0U)
                return 17;
            ++equilibrium_construct_checks;
            if (2U * constructed.macro_p_numerator !=
                constructed.macro_p_denominator *
                    (static_cast<std::uint64_t>(constructed.phase_sum) + p + q))
                return 18;
            if (constructed.macro_p_denominator == 1U)
                ++integer_macro_p;
            else if (constructed.macro_p_denominator == 2U)
                ++half_integer_macro_p;
            else
                return 19;

            if (hhs_exact_pass219_hhcq_8basis_equilibrium_validate(
                    p, q, &surface.state,
                    constructed.macro_p_numerator,
                    constructed.macro_p_denominator,
                    &independent) != HHS_EXACT_STATUS_OK ||
                independent.equilibrium_exact != 1U ||
                independent.macro_p_supplied_independently != 1U ||
                independent.transport_reconciliation_required != 0U)
                return 20;
            ++independent_equilibrium_checks;

            if (hhs_exact_pass219_hhcq_8basis_manifold_evaluate(
                    p, q, &surface.state,
                    constructed.macro_p_numerator,
                    constructed.macro_p_denominator,
                    prepared.resolution.resolution_index,
                    &state_a) != HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_hhcq_8basis_manifold_evaluate(
                    p, q, &surface.state,
                    constructed.macro_p_numerator,
                    constructed.macro_p_denominator,
                    prepared.resolution.resolution_index,
                    &state_b) != HHS_EXACT_STATUS_OK ||
                std::memcmp(&state_a, &state_b, sizeof(state_a)) != 0)
                return 21;
            ++replay_checks;
            if (state_a.matrix_order_exact != 1U) return 22;
            ++matrix_order_checks;
            if (state_a.phase10_product_closure_valid != 1U) return 23;
            ++phase10_product_closure_checks;
            if (state_a.constraint_intersection_satisfied != 1U ||
                state_a.equilibrium_exact != 1U ||
                state_a.parity_orientation_exact != 1U ||
                state_a.candidate_only != 1U ||
                state_a.canonical_mutation_authority != 0U ||
                state_a.canonical_hash72_authority != 0U ||
                state_a.canonical_hash216_authority != 0U ||
                state_a.canonical_persistence_authority != 0U ||
                state_a.floating_point_authority != 0U)
                return 24;
            ++constraint_intersection_checks;

            const std::uint16_t native_anchor = anchor_for(anchor);
            const std::uint8_t cell = static_cast<std::uint8_t>(native_anchor / 64U);
            if (hhs_exact_pass219_hhcq_8basis_from_vm81(
                    &frame,
                    cell,
                    static_cast<std::uint8_t>((cell + 1U) % HHS_EXACT_VM81_CELLS),
                    static_cast<std::uint8_t>((cell + 9U) % HHS_EXACT_VM81_CELLS),
                    static_cast<std::uint8_t>((cell + 10U) % HHS_EXACT_VM81_CELLS),
                    p, q,
                    constructed.macro_p_numerator,
                    constructed.macro_p_denominator,
                    prepared.resolution.resolution_index,
                    &vm_manifold) != HHS_EXACT_STATUS_OK ||
                vm_manifold.full_octonion_surface_validated != 1U ||
                vm_manifold.constraint_intersection_satisfied != 1U ||
                vm_manifold.equilibrium.equilibrium_signature64 !=
                    state_a.equilibrium.equilibrium_signature64 ||
                vm_manifold.parity_gate.parity_signature64 !=
                    state_a.parity_gate.parity_signature64)
                return 25;

            if (state_a.parity_gate.orientation ==
                    HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_DIRECT)
                ++authenticated_direct;
            else if (state_a.parity_gate.orientation ==
                    HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_REVERSED)
                ++authenticated_reversed;
            else
                return 26;

            if (hhs_exact_pass219_hhcq_8basis_manifold_evaluate(
                    p, q, &surface.state,
                    constructed.macro_p_numerator + constructed.macro_p_denominator,
                    constructed.macro_p_denominator,
                    prepared.resolution.resolution_index,
                    &drifted) != HHS_EXACT_STATUS_OK ||
                drifted.equilibrium.transport_reconciliation_required != 1U ||
                drifted.equilibrium.transport_delta_numerator != 2 ||
                drifted.equilibrium.transport_delta_denominator != 1U)
                return 27;
            ++drift_detection_checks;
            if (drifted.constraint_intersection_satisfied != 0U ||
                drifted.canonical_mutation_authority != 0U ||
                drifted.canonical_hash72_authority != 0U ||
                drifted.canonical_hash216_authority != 0U ||
                drifted.canonical_persistence_authority != 0U ||
                drifted.floating_point_authority != 0U)
                return 28;
            ++drift_fail_closed_checks;

            signature ^= state_a.manifold_signature64 + UINT64_C(0x9e3779b97f4a7c15);
            signature ^= vm_manifold.manifold_signature64;
            signature ^= drifted.manifold_signature64;
            ++local_samples;
        }
    }

    if (summary_records != 529U || unique_digests.size() != 489U ||
        local_samples != 4761U || phase5_roundtrip_checks != 4761U ||
        full_surface_checks != 4761U || equilibrium_construct_checks != 4761U ||
        independent_equilibrium_checks != 4761U || replay_checks != 4761U ||
        matrix_order_checks != 4761U || phase10_product_closure_checks != 4761U ||
        constraint_intersection_checks != 4761U || drift_detection_checks != 4761U ||
        drift_fail_closed_checks != 4761U ||
        integer_macro_p + half_integer_macro_p != 4761U ||
        authenticated_direct == 0U || authenticated_reversed == 0U)
        return 29;

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_HHCQ_8BASIS_EQUILIBRIUM_PARITY_PHASE11_V1\",\n");
    std::printf("  \"classification\": \"EIGHT_BASIS_EQUILIBRIUM_PARITY_EXACT_PRE_TRANSPORT\",\n");
    std::printf("  \"phase3_frame_binary_sha256\": \"63d0f8816d4c04e10eb5d9644c9c60015b8cdd3b1235f114b3f1821ef08a3433\",\n");
    std::printf("  \"source_bytes\": 700,\n");
    std::printf("  \"source_sha256\": \"7d87d468e528f30df6768b130f626077ab9786e82d2dbe577a120753cdaedc60\",\n");
    std::printf("  \"derived_update_quantum\": 5,\n");
    std::printf("  \"derived_phase_modulus\": 72,\n");
    std::printf("  \"derived_parameter_count\": 5184,\n");
    std::printf("  \"exhaustive_direct_orientations\": %u,\n", exhaustive_direct);
    std::printf("  \"exhaustive_reversed_orientations\": %u,\n", exhaustive_reversed);
    std::printf("  \"summary_records\": %u,\n", summary_records);
    std::printf("  \"authenticated_unique_digests\": %zu,\n", unique_digests.size());
    std::printf("  \"local_samples\": %u,\n", local_samples);
    std::printf("  \"phase5_exact_roundtrip_checks\": %u,\n", phase5_roundtrip_checks);
    std::printf("  \"full_octonion_surface_checks\": %u,\n", full_surface_checks);
    std::printf("  \"equilibrium_constructor_checks\": %u,\n", equilibrium_construct_checks);
    std::printf("  \"independent_equilibrium_checks\": %u,\n", independent_equilibrium_checks);
    std::printf("  \"deterministic_replay_checks\": %u,\n", replay_checks);
    std::printf("  \"matrix_order_checks\": %u,\n", matrix_order_checks);
    std::printf("  \"phase10_product_closure_checks\": %u,\n", phase10_product_closure_checks);
    std::printf("  \"constraint_intersection_checks\": %u,\n", constraint_intersection_checks);
    std::printf("  \"transport_drift_detection_checks\": %u,\n", drift_detection_checks);
    std::printf("  \"transport_drift_fail_closed_checks\": %u,\n", drift_fail_closed_checks);
    std::printf("  \"integer_macro_p_states\": %u,\n", integer_macro_p);
    std::printf("  \"half_integer_macro_p_states\": %u,\n", half_integer_macro_p);
    std::printf("  \"authenticated_direct_orientations\": %u,\n", authenticated_direct);
    std::printf("  \"authenticated_reversed_orientations\": %u,\n", authenticated_reversed);
    std::printf("  \"x2_parity_equals_x_parity\": true,\n");
    std::printf("  \"ordinary_negative_base_exponent_evaluated\": false,\n");
    std::printf("  \"symbolic_exponent_retained\": true,\n");
    std::printf("  \"actual_phase_transport_mutation_performed\": false,\n");
    std::printf("  \"candidate_transport_delta_only\": true,\n");
    std::printf("  \"fixed_policy_state_bytes\": 112,\n");
    std::printf("  \"candidate_only\": true,\n");
    std::printf("  \"canonical_authority_changed\": false,\n");
    std::printf("  \"floating_point_authority\": false,\n");
    std::printf("  \"signature64\": \"%llu\"\n",
                static_cast<unsigned long long>(signature));
    std::printf("}\n");
    return 0;
}
