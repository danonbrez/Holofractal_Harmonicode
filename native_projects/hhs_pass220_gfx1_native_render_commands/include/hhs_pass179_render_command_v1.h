#ifndef HHS_PASS179_RENDER_COMMAND_V1_H
#define HHS_PASS179_RENDER_COMMAND_V1_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS179_RENDER_PACKET_SCHEMA_VERSION 1U
#define HHS179_RENDER_PACKET_HEADER_BYTES 1088U
#define HHS179_RENDER_COMMAND_BYTES 32U
#define HHS179_RENDER_ENDIAN_MARKER 0x01020304U
#define HHS179_RENDER_HASH216_BYTES 216U
#define HHS179_RENDER_HASH72_BYTES 72U
#define HHS179_RENDER_SHA256_BYTES 32U
#define HHS179_RENDER_MAX_COMMANDS 65535U

#define HHS179_RENDER_PACKET_FLAG_SEALED 0x00000001U
#define HHS179_RENDER_PACKET_FLAG_PROJECTION_ONLY 0x00000002U
#define HHS179_RENDER_PACKET_FLAG_COMPATIBILITY_UNADMITTED 0x00000004U

typedef enum HHS179RenderStatusV1 {
    HHS179_RENDER_OK = 0,
    HHS179_RENDER_ERR_ARGUMENT = 1,
    HHS179_RENDER_ERR_CAPACITY = 2,
    HHS179_RENDER_ERR_VERSION = 3,
    HHS179_RENDER_ERR_ENDIAN = 4,
    HHS179_RENDER_ERR_BOUNDS = 5,
    HHS179_RENDER_ERR_IDENTITY = 6,
    HHS179_RENDER_ERR_OPCODE = 7,
    HHS179_RENDER_ERR_SEQUENCE = 8,
    HHS179_RENDER_ERR_SEALED = 9,
    HHS179_RENDER_ERR_FINGERPRINT = 10
} HHS179RenderStatusV1;

typedef enum HHS179RenderOpcodeV1 {
    HHS179_CMD_BEGIN_FRAME = 1,
    HHS179_CMD_SET_VIEWPORT = 2,
    HHS179_CMD_SET_CAMERA = 3,
    HHS179_CMD_SET_TARGET = 4,
    HHS179_CMD_CLEAR = 5,
    HHS179_CMD_BIND_PIPELINE = 6,
    HHS179_CMD_BIND_MATERIAL = 7,
    HHS179_CMD_BIND_TEXTURES = 8,
    HHS179_CMD_SET_SCISSOR = 9,
    HHS179_CMD_SET_CLIP = 10,
    HHS179_CMD_DRAW_SPRITES = 11,
    HHS179_CMD_DRAW_PATHS = 12,
    HHS179_CMD_DRAW_TEXT = 13,
    HHS179_CMD_DRAW_POINTS = 14,
    HHS179_CMD_DRAW_LINES = 15,
    HHS179_CMD_DRAW_MESHES = 16,
    HHS179_CMD_DRAW_INSTANCES = 17,
    HHS179_CMD_DISPATCH_PARTICLE_UPDATE_PROJECTION = 18,
    HHS179_CMD_BEGIN_COMPOSITE_PASS = 19,
    HHS179_CMD_APPLY_EFFECT = 20,
    HHS179_CMD_END_COMPOSITE_PASS = 21,
    HHS179_CMD_COPY_OR_RESOLVE = 22,
    HHS179_CMD_READBACK_CAPTURE = 23,
    HHS179_CMD_END_FRAME = 24
} HHS179RenderOpcodeV1;

typedef struct HHS179RenderPacketInitV1 {
    uint32_t struct_size;
    uint32_t flags;
    uint32_t projection_profile;
    uint32_t target_width;
    uint32_t target_height;
    uint32_t target_format;
    uint64_t frame_index;
    int64_t exact_time_num;
    uint64_t exact_time_den;
    uint8_t scene_snapshot_hash216[HHS179_RENDER_HASH216_BYTES];
    uint8_t frame_hash216[HHS179_RENDER_HASH216_BYTES];
    uint8_t prior_frame_hash216[HHS179_RENDER_HASH216_BYTES];
    uint8_t resource_manifest_hash216[HHS179_RENDER_HASH216_BYTES];
    uint8_t camera_hash72[HHS179_RENDER_HASH72_BYTES];
    uint8_t software_digest_sha256[HHS179_RENDER_SHA256_BYTES];
    uint8_t backend_evidence_sha256[HHS179_RENDER_SHA256_BYTES];
} HHS179RenderPacketInitV1;

typedef struct HHS179RenderCommandV1 {
    uint16_t opcode;
    uint16_t flags;
    uint32_t byte_length;
    uint64_t resource_id;
    uint64_t arg0;
    uint64_t arg1;
} HHS179RenderCommandV1;

_Static_assert(sizeof(HHS179RenderCommandV1) == HHS179_RENDER_COMMAND_BYTES, "HHS179RenderCommandV1 must remain 32 bytes");

size_t hhs179_render_packet_required_bytes(uint32_t command_count);
HHS179RenderStatusV1 hhs179_render_packet_init(
    uint8_t *buffer,
    size_t capacity,
    const HHS179RenderPacketInitV1 *init,
    uint32_t command_count
);
HHS179RenderStatusV1 hhs179_render_packet_write_command(
    uint8_t *buffer,
    size_t capacity,
    uint32_t index,
    const HHS179RenderCommandV1 *command
);
HHS179RenderStatusV1 hhs179_render_packet_seal(uint8_t *buffer, size_t size);
HHS179RenderStatusV1 hhs179_render_packet_validate(const uint8_t *buffer, size_t size);
uint64_t hhs179_render_packet_projection_fingerprint(const uint8_t *buffer, size_t size);
HHS179RenderStatusV1 hhs179_render_commands_export(
    const uint8_t *sealed_packet,
    size_t sealed_size,
    uint8_t *out_buffer,
    size_t out_capacity,
    size_t *out_size
);

#ifdef __cplusplus
}
#endif

#endif
