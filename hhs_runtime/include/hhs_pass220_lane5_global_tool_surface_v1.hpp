#ifndef HHS_PASS220_LANE5_GLOBAL_TOOL_SURFACE_V1_HPP
#define HHS_PASS220_LANE5_GLOBAL_TOOL_SURFACE_V1_HPP

#include <cstddef>
#include <cstdint>

#define HHS_PASS220_LANE5_GLOBAL_TOOL_SURFACE_VERSION UINT32_C(0x00010001)
#define HHS_PASS220_LANE5_GLOBAL_TOOL_HASH216_CHARS 216U
#define HHS_PASS220_LANE5_GLOBAL_TOOL_SHA256_HEX_CHARS 64U
#define HHS_PASS220_LANE5_GLOBAL_TOOL_PROJECTION_BITS 5184U

extern "C" {

typedef enum HHSExactPass220Lane5GlobalToolStatusV1 {
    HHS_PASS220_LANE5_GLOBAL_TOOL_OK = 0,
    HHS_PASS220_LANE5_GLOBAL_TOOL_INVALID_ARGUMENT = 1,
    HHS_PASS220_LANE5_GLOBAL_TOOL_INVARIANT_FAILURE = 2
} HHSExactPass220Lane5GlobalToolStatusV1;

typedef struct HHSExactPass220Lane5GlobalToolSurfaceV1 {
    std::uint32_t struct_size;
    std::uint32_t version;
    std::uint32_t kind_code;
    std::uint32_t projection_bits;
    std::uint8_t pass219_bound;
    std::uint8_t pass220_bound;
    std::uint8_t candidate_only;
    std::uint8_t lane5_selection_unchanged;
    std::uint8_t cpp_surface_bound;
    std::uint8_t canonical_vm81_mutation_authority;
    std::uint8_t canonical_hash72_authority;
    std::uint8_t canonical_hash216_authority;
    std::uint8_t canonical_persistence_authority;
    std::uint8_t floating_point_canonical_authority;
    std::uint8_t reserved0[2];
    char tool_id_sha256[HHS_PASS220_LANE5_GLOBAL_TOOL_SHA256_HEX_CHARS + 1U];
    char projection_sha256[HHS_PASS220_LANE5_GLOBAL_TOOL_SHA256_HEX_CHARS + 1U];
    char hash216[HHS_PASS220_LANE5_GLOBAL_TOOL_HASH216_CHARS + 1U];
} HHSExactPass220Lane5GlobalToolSurfaceV1;

HHSExactPass220Lane5GlobalToolStatusV1
hhs_pass220_lane5_global_tool_surface_validate_v1(
    const HHSExactPass220Lane5GlobalToolSurfaceV1 *tool
);

}  // extern "C"

#endif
