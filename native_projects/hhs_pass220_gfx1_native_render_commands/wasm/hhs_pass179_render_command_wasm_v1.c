#include "hhs_pass179_render_command_v1.h"

#include <stddef.h>
#include <stdint.h>

#define HHS179_WASM_MAX_COMMANDS 64U
#define HHS179_WASM_PACKET_CAPACITY \
    (HHS179_RENDER_PACKET_HEADER_BYTES + \
     HHS179_WASM_MAX_COMMANDS * HHS179_RENDER_COMMAND_BYTES)

enum {
    HHS179_WASM_ID_SCENE = 1,
    HHS179_WASM_ID_FRAME = 2,
    HHS179_WASM_ID_PRIOR = 3,
    HHS179_WASM_ID_RESOURCES = 4,
    HHS179_WASM_ID_CAMERA = 5,
    HHS179_WASM_ID_SOFTWARE_DIGEST = 6,
    HHS179_WASM_ID_BACKEND_EVIDENCE = 7
};

static HHS179RenderPacketInitV1 g_init;
static HHS179RenderCommandV1 g_commands[HHS179_WASM_MAX_COMMANDS];
static uint8_t g_packet[HHS179_WASM_PACKET_CAPACITY];
static uint32_t g_packet_size = 0U;

static void zero_bytes(uint8_t *p, size_t n) {
    size_t i;
    for (i = 0U; i < n; ++i) p[i] = 0U;
}

static void zero_init(void) {
    zero_bytes((uint8_t *)&g_init, sizeof(g_init));
    zero_bytes((uint8_t *)g_commands, sizeof(g_commands));
    zero_bytes(g_packet, sizeof(g_packet));
    g_packet_size = 0U;
}

uint32_t hhs179_wasm_abi_version(void) {
    return HHS179_RENDER_PACKET_SCHEMA_VERSION;
}

uint32_t hhs179_wasm_reset(
    uint32_t flags,
    uint32_t projection_profile,
    uint32_t target_width,
    uint32_t target_height,
    uint32_t target_format,
    uint64_t frame_index,
    int64_t exact_time_num,
    uint64_t exact_time_den
) {
    zero_init();
    g_init.struct_size = (uint32_t)sizeof(g_init);
    g_init.flags = flags;
    g_init.projection_profile = projection_profile;
    g_init.target_width = target_width;
    g_init.target_height = target_height;
    g_init.target_format = target_format;
    g_init.frame_index = frame_index;
    g_init.exact_time_num = exact_time_num;
    g_init.exact_time_den = exact_time_den;
    if (target_width == 0U || target_height == 0U || exact_time_den == 0U) {
        return HHS179_RENDER_ERR_BOUNDS;
    }
    return HHS179_RENDER_OK;
}

uint32_t hhs179_wasm_identity_ptr(uint32_t identity_kind) {
    switch (identity_kind) {
        case HHS179_WASM_ID_SCENE:
            return (uint32_t)(uintptr_t)g_init.scene_snapshot_hash216;
        case HHS179_WASM_ID_FRAME:
            return (uint32_t)(uintptr_t)g_init.frame_hash216;
        case HHS179_WASM_ID_PRIOR:
            return (uint32_t)(uintptr_t)g_init.prior_frame_hash216;
        case HHS179_WASM_ID_RESOURCES:
            return (uint32_t)(uintptr_t)g_init.resource_manifest_hash216;
        case HHS179_WASM_ID_CAMERA:
            return (uint32_t)(uintptr_t)g_init.camera_hash72;
        case HHS179_WASM_ID_SOFTWARE_DIGEST:
            return (uint32_t)(uintptr_t)g_init.software_digest_sha256;
        case HHS179_WASM_ID_BACKEND_EVIDENCE:
            return (uint32_t)(uintptr_t)g_init.backend_evidence_sha256;
        default:
            return 0U;
    }
}

uint32_t hhs179_wasm_identity_bytes(uint32_t identity_kind) {
    switch (identity_kind) {
        case HHS179_WASM_ID_SCENE:
        case HHS179_WASM_ID_FRAME:
        case HHS179_WASM_ID_PRIOR:
        case HHS179_WASM_ID_RESOURCES:
            return HHS179_RENDER_HASH216_BYTES;
        case HHS179_WASM_ID_CAMERA:
            return HHS179_RENDER_HASH72_BYTES;
        case HHS179_WASM_ID_SOFTWARE_DIGEST:
        case HHS179_WASM_ID_BACKEND_EVIDENCE:
            return HHS179_RENDER_SHA256_BYTES;
        default:
            return 0U;
    }
}

uint32_t hhs179_wasm_command_ptr(uint32_t index) {
    if (index >= HHS179_WASM_MAX_COMMANDS) return 0U;
    return (uint32_t)(uintptr_t)&g_commands[index];
}

uint32_t hhs179_wasm_command_capacity(void) {
    return HHS179_WASM_MAX_COMMANDS;
}

uint32_t hhs179_wasm_packet_ptr(void) {
    return (uint32_t)(uintptr_t)g_packet;
}

uint32_t hhs179_wasm_packet_capacity(void) {
    return HHS179_WASM_PACKET_CAPACITY;
}

uint32_t hhs179_wasm_packet_size(void) {
    return g_packet_size;
}

uint32_t hhs179_wasm_build_packet(uint32_t command_count) {
    HHS179RenderStatusV1 status;
    uint32_t i;
    size_t required = hhs179_render_packet_required_bytes(command_count);

    g_packet_size = 0U;
    if (required == 0U || required > sizeof(g_packet)) return HHS179_RENDER_ERR_CAPACITY;

    status = hhs179_render_packet_init(g_packet, sizeof(g_packet), &g_init, command_count);
    if (status != HHS179_RENDER_OK) return (uint32_t)status;

    for (i = 0U; i < command_count; ++i) {
        status = hhs179_render_packet_write_command(
            g_packet,
            sizeof(g_packet),
            i,
            &g_commands[i]
        );
        if (status != HHS179_RENDER_OK) return (uint32_t)status;
    }

    status = hhs179_render_packet_seal(g_packet, required);
    if (status != HHS179_RENDER_OK) return (uint32_t)status;

    status = hhs179_render_packet_validate(g_packet, required);
    if (status != HHS179_RENDER_OK) return (uint32_t)status;

    g_packet_size = (uint32_t)required;
    return HHS179_RENDER_OK;
}
