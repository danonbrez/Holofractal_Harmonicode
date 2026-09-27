#include "hhs_pass220_lane5_global_tool_surface_v1.hpp"

#include <cstdio>
#include <cstring>

#define CHECK(expr) do { if (!(expr)) { std::fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); return 1; } } while (0)

static void fill_hex(char *out, std::size_t chars, char value) {
    for (std::size_t i = 0U; i < chars; ++i) out[i] = value;
    out[chars] = '\0';
}

int main() {
    HHSExactPass220Lane5GlobalToolSurfaceV1 tool{};
    tool.struct_size = static_cast<std::uint32_t>(sizeof(tool));
    tool.version = HHS_PASS220_LANE5_GLOBAL_TOOL_SURFACE_VERSION;
    tool.kind_code = 1U;
    tool.projection_bits = HHS_PASS220_LANE5_GLOBAL_TOOL_PROJECTION_BITS;
    tool.pass219_bound = 1U;
    tool.pass220_bound = 0U;
    tool.candidate_only = 1U;
    tool.lane5_selection_unchanged = 1U;
    tool.cpp_surface_bound = 1U;
    fill_hex(tool.tool_id_sha256, HHS_PASS220_LANE5_GLOBAL_TOOL_SHA256_HEX_CHARS, 'a');
    fill_hex(tool.projection_sha256, HHS_PASS220_LANE5_GLOBAL_TOOL_SHA256_HEX_CHARS, 'b');
    for (std::size_t i = 0U; i < HHS_PASS220_LANE5_GLOBAL_TOOL_HASH216_CHARS; ++i) {
        tool.hash216[i] = static_cast<char>('A' + (i % 26U));
    }
    tool.hash216[HHS_PASS220_LANE5_GLOBAL_TOOL_HASH216_CHARS] = '\0';

    CHECK(hhs_pass220_lane5_global_tool_surface_validate_v1(&tool) ==
          HHS_PASS220_LANE5_GLOBAL_TOOL_OK);

    HHSExactPass220Lane5GlobalToolSurfaceV1 pass220 = tool;
    pass220.kind_code = 2U;
    pass220.pass219_bound = 0U;
    pass220.pass220_bound = 1U;
    CHECK(hhs_pass220_lane5_global_tool_surface_validate_v1(&pass220) ==
          HHS_PASS220_LANE5_GLOBAL_TOOL_OK);

    HHSExactPass220Lane5GlobalToolSurfaceV1 selector_drift = tool;
    selector_drift.lane5_selection_unchanged = 0U;
    CHECK(hhs_pass220_lane5_global_tool_surface_validate_v1(&selector_drift) ==
          HHS_PASS220_LANE5_GLOBAL_TOOL_INVARIANT_FAILURE);

    HHSExactPass220Lane5GlobalToolSurfaceV1 authority = tool;
    authority.canonical_hash216_authority = 1U;
    CHECK(hhs_pass220_lane5_global_tool_surface_validate_v1(&authority) ==
          HHS_PASS220_LANE5_GLOBAL_TOOL_INVARIANT_FAILURE);

    HHSExactPass220Lane5GlobalToolSurfaceV1 wrong_width = tool;
    wrong_width.projection_bits = 648U;
    CHECK(hhs_pass220_lane5_global_tool_surface_validate_v1(&wrong_width) ==
          HHS_PASS220_LANE5_GLOBAL_TOOL_INVARIANT_FAILURE);

    HHSExactPass220Lane5GlobalToolSurfaceV1 no_scope = tool;
    no_scope.pass219_bound = 0U;
    no_scope.pass220_bound = 0U;
    CHECK(hhs_pass220_lane5_global_tool_surface_validate_v1(&no_scope) ==
          HHS_PASS220_LANE5_GLOBAL_TOOL_INVARIANT_FAILURE);

    std::puts("HHS_PASS220_LANE5_GLOBAL_TOOL_SURFACE_V1_PASS");
    return 0;
}
