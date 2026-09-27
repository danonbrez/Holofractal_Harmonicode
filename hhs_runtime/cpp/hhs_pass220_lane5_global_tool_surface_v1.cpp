#include "../include/hhs_pass220_lane5_global_tool_surface_v1.hpp"

#include <cctype>
#include <cstring>

namespace {

bool valid_hex64(const char *value) {
    if (value == nullptr || std::strlen(value) != HHS_PASS220_LANE5_GLOBAL_TOOL_SHA256_HEX_CHARS) {
        return false;
    }
    for (std::size_t i = 0; i < HHS_PASS220_LANE5_GLOBAL_TOOL_SHA256_HEX_CHARS; ++i) {
        const unsigned char c = static_cast<unsigned char>(value[i]);
        if (!std::isxdigit(c)) {
            return false;
        }
    }
    return true;
}

bool valid_hash216(const char *value) {
    if (value == nullptr || std::strlen(value) != HHS_PASS220_LANE5_GLOBAL_TOOL_HASH216_CHARS) {
        return false;
    }
    for (std::size_t i = 0; i < HHS_PASS220_LANE5_GLOBAL_TOOL_HASH216_CHARS; ++i) {
        const unsigned char c = static_cast<unsigned char>(value[i]);
        if (c < 0x21U || c > 0x7eU) {
            return false;
        }
    }
    return true;
}

}  // namespace

extern "C" HHSExactPass220Lane5GlobalToolStatusV1
hhs_pass220_lane5_global_tool_surface_validate_v1(
    const HHSExactPass220Lane5GlobalToolSurfaceV1 *tool
) {
    if (tool == nullptr) {
        return HHS_PASS220_LANE5_GLOBAL_TOOL_INVALID_ARGUMENT;
    }
    if (tool->struct_size != sizeof(*tool) ||
        tool->version != HHS_PASS220_LANE5_GLOBAL_TOOL_SURFACE_VERSION) {
        return HHS_PASS220_LANE5_GLOBAL_TOOL_INVALID_ARGUMENT;
    }
    if (tool->kind_code != 1U && tool->kind_code != 2U) {
        return HHS_PASS220_LANE5_GLOBAL_TOOL_INVARIANT_FAILURE;
    }
    if ((tool->pass219_bound != 1U && tool->pass220_bound != 1U) ||
        tool->projection_bits != HHS_PASS220_LANE5_GLOBAL_TOOL_PROJECTION_BITS ||
        tool->candidate_only != 1U ||
        tool->lane5_selection_unchanged != 1U ||
        tool->cpp_surface_bound != 1U) {
        return HHS_PASS220_LANE5_GLOBAL_TOOL_INVARIANT_FAILURE;
    }
    if (tool->canonical_vm81_mutation_authority != 0U ||
        tool->canonical_hash72_authority != 0U ||
        tool->canonical_hash216_authority != 0U ||
        tool->canonical_persistence_authority != 0U ||
        tool->floating_point_canonical_authority != 0U) {
        return HHS_PASS220_LANE5_GLOBAL_TOOL_INVARIANT_FAILURE;
    }
    if (!valid_hex64(tool->tool_id_sha256) ||
        !valid_hex64(tool->projection_sha256) ||
        !valid_hash216(tool->hash216)) {
        return HHS_PASS220_LANE5_GLOBAL_TOOL_INVARIANT_FAILURE;
    }
    return HHS_PASS220_LANE5_GLOBAL_TOOL_OK;
}
