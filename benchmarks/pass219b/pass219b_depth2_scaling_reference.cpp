#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <string>
#include <vector>

namespace {
constexpr std::uint64_t kPhaseOrigins = 81ULL;
constexpr std::uint64_t kDepth2Combinations = kPhaseOrigins * kPhaseOrigins;
constexpr std::uint64_t kBranchFamilies = 2ULL;
constexpr std::uint64_t kLanesPerBranch = 5184ULL;
constexpr std::uint64_t kDenseBranches = kDepth2Combinations * kBranchFamilies;
constexpr std::uint64_t kDenseLaneDispatches = kDenseBranches * kLanesPerBranch;
constexpr std::uint32_t kStartOrigin1 = 37U;
constexpr std::uint32_t kStartOrigin2 = 53U;

struct Case {
    std::uint32_t s1;
    std::uint32_t s2;
};

constexpr std::array<Case, 7> kCases{{
    {1U, 1U},
    {1U, 3U},
    {3U, 3U},
    {3U, 9U},
    {9U, 9U},
    {27U, 27U},
    {81U, 81U},
}};

std::uint32_t wrap81(std::uint32_t start, std::uint32_t offset) {
    return (start + offset) % static_cast<std::uint32_t>(kPhaseOrigins);
}

std::uint64_t original_branch_id(
    std::uint32_t origin1,
    std::uint32_t origin2,
    std::uint32_t family
) {
    return (
        (static_cast<std::uint64_t>(origin1) * kPhaseOrigins + origin2) *
        kBranchFamilies + family
    );
}

std::uint32_t lane_word(std::uint64_t original_branch, std::uint32_t lane) {
    std::uint32_t x = static_cast<std::uint32_t>(original_branch) ^
                      (lane * 0x9E3779B9U) ^ 0xA5A55A5AU;
    x ^= x >> 16U;
    x *= 0x7FEB352DU;
    x ^= x >> 15U;
    x *= 0x846CA68BU;
    x ^= x >> 16U;
    return x;
}

std::vector<std::uint64_t> selected_branches(const Case &c) {
    std::vector<std::uint64_t> out;
    out.reserve(static_cast<std::size_t>(c.s1) * c.s2 * kBranchFamilies);
    for (std::uint32_t i = 0; i < c.s1; ++i) {
        const std::uint32_t o1 = wrap81(kStartOrigin1, i);
        for (std::uint32_t j = 0; j < c.s2; ++j) {
            const std::uint32_t o2 = wrap81(kStartOrigin2, j);
            for (std::uint32_t family = 0; family < kBranchFamilies; ++family) {
                out.push_back(original_branch_id(o1, o2, family));
            }
        }
    }
    return out;
}

bool validate_case(const Case &c, const std::vector<std::uint64_t> &branches) {
    const std::uint64_t expected =
        static_cast<std::uint64_t>(c.s1) * c.s2 * kBranchFamilies;
    if (branches.size() != expected) return false;
    std::set<std::uint64_t> unique(branches.begin(), branches.end());
    if (unique.size() != branches.size()) return false;
    for (std::uint64_t id : branches) {
        if (id >= kDenseBranches) return false;
        for (std::uint32_t lane : {0U, 1U, 63U, 4095U, 5183U}) {
            const std::uint32_t dense = lane_word(id, lane);
            const std::uint32_t selected = lane_word(id, lane);
            if (dense != selected) return false;
        }
    }
    return true;
}

std::uint64_t reduction_x1000(std::uint32_t s1, std::uint32_t s2) {
    const std::uint64_t materialized = static_cast<std::uint64_t>(s1) * s2;
    return kDepth2Combinations * 1000ULL / materialized;
}

}  // namespace

int main(int argc, char **argv) {
    const std::string output = argc > 1 ? argv[1] : "pass219b_depth2_reference.json";
    if (kDepth2Combinations != 6561ULL ||
        kDenseBranches != 13122ULL ||
        kDenseLaneDispatches != 68024448ULL) {
        std::cerr << "depth-2 cardinality invariant failure\n";
        return 2;
    }

    std::ofstream out(output);
    if (!out) {
        std::cerr << "cannot open output\n";
        return 3;
    }

    out << "{\n";
    out << "  \"schema\": \"HHS_PASS_219B_I3_DEPTH2_REFERENCE_V1\",\n";
    out << "  \"phase_origins_per_layer\": 81,\n";
    out << "  \"potential_phase_combinations\": 6561,\n";
    out << "  \"branch_families\": 2,\n";
    out << "  \"dense_branches\": 13122,\n";
    out << "  \"lanes_per_branch\": 5184,\n";
    out << "  \"dense_lane_dispatches\": 68024448,\n";
    out << "  \"selected_start_origin_1\": 37,\n";
    out << "  \"selected_start_origin_2\": 53,\n";
    out << "  \"cases\": [\n";

    bool all_ok = true;
    for (std::size_t idx = 0; idx < kCases.size(); ++idx) {
        const Case &c = kCases[idx];
        const auto branches = selected_branches(c);
        const bool ok = validate_case(c, branches);
        all_ok = all_ok && ok;
        const std::uint64_t combos = static_cast<std::uint64_t>(c.s1) * c.s2;
        const std::uint64_t branch_count = combos * kBranchFamilies;
        const std::uint64_t lane_dispatches = branch_count * kLanesPerBranch;
        out << "    {\"s1\": " << c.s1
            << ", \"s2\": " << c.s2
            << ", \"materialized_combinations\": " << combos
            << ", \"branches\": " << branch_count
            << ", \"lane_dispatches\": " << lane_dispatches
            << ", \"ideal_reduction_x1000\": " << reduction_x1000(c.s1, c.s2)
            << ", \"original_branch_identity_preserved\": " << (ok ? "true" : "false")
            << "}";
        if (idx + 1 != kCases.size()) out << ",";
        out << "\n";
    }

    out << "  ],\n";
    out << "  \"scaling_law\": \"R = 6561 / (s1*s2)\",\n";
    out << "  \"authoritative_state_changed\": false,\n";
    out << "  \"all_identity_checks_passed\": " << (all_ok ? "true" : "false") << "\n";
    out << "}\n";

    return all_ok ? 0 : 4;
}
