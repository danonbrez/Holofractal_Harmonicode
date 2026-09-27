#include "hhs_pass179_render_command_v1.h"

#include <limits.h>
#include <string.h>

#define OFF_MAGIC 0U
#define OFF_SCHEMA_VERSION 8U
#define OFF_HEADER_BYTES 12U
#define OFF_COMMAND_BYTES 16U
#define OFF_COMMAND_COUNT 20U
#define OFF_TOTAL_BYTES 24U
#define OFF_ENDIAN 28U
#define OFF_FLAGS 32U
#define OFF_PROJECTION_PROFILE 36U
#define OFF_TARGET_WIDTH 40U
#define OFF_TARGET_HEIGHT 44U
#define OFF_TARGET_FORMAT 48U
#define OFF_RESERVED0 52U
#define OFF_FRAME_INDEX 56U
#define OFF_TIME_NUM 64U
#define OFF_TIME_DEN 72U
#define OFF_SCENE_HASH216 80U
#define OFF_FRAME_HASH216 296U
#define OFF_PRIOR_HASH216 512U
#define OFF_RESOURCE_HASH216 728U
#define OFF_CAMERA_HASH72 944U
#define OFF_SOFTWARE_DIGEST 1016U
#define OFF_BACKEND_EVIDENCE 1048U
#define OFF_FINGERPRINT 1080U

static const uint8_t HHS179_MAGIC[8] = {'H','H','S','1','7','9','C','1'};

static void put_u16le(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)(v & 0xffU);
    p[1] = (uint8_t)((v >> 8) & 0xffU);
}

static void put_u32le(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v & 0xffU);
    p[1] = (uint8_t)((v >> 8) & 0xffU);
    p[2] = (uint8_t)((v >> 16) & 0xffU);
    p[3] = (uint8_t)((v >> 24) & 0xffU);
}

static void put_u64le(uint8_t *p, uint64_t v) {
    unsigned i;
    for (i = 0U; i < 8U; ++i) p[i] = (uint8_t)((v >> (i * 8U)) & UINT64_C(0xff));
}

static uint16_t get_u16le(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint32_t get_u32le(const uint8_t *p) {
    return (uint32_t)p[0]
        | ((uint32_t)p[1] << 8)
        | ((uint32_t)p[2] << 16)
        | ((uint32_t)p[3] << 24);
}

static uint64_t get_u64le(const uint8_t *p) {
    uint64_t v = 0U;
    unsigned i;
    for (i = 0U; i < 8U; ++i) v |= ((uint64_t)p[i]) << (i * 8U);
    return v;
}

static int identity_nonzero(const uint8_t *p, size_t n) {
    size_t i;
    for (i = 0U; i < n; ++i) if (p[i] != 0U) return 1;
    return 0;
}

static int known_opcode(uint16_t opcode) {
    return opcode >= (uint16_t)HHS179_CMD_BEGIN_FRAME
        && opcode <= (uint16_t)HHS179_CMD_END_FRAME;
}

static int draw_opcode(uint16_t opcode) {
    return opcode >= (uint16_t)HHS179_CMD_DRAW_SPRITES
        && opcode <= (uint16_t)HHS179_CMD_DRAW_INSTANCES;
}

size_t hhs179_render_packet_required_bytes(uint32_t command_count) {
    if (command_count == 0U || command_count > HHS179_RENDER_MAX_COMMANDS) return 0U;
    return HHS179_RENDER_PACKET_HEADER_BYTES + (size_t)command_count * HHS179_RENDER_COMMAND_BYTES;
}

static HHS179RenderStatusV1 validate_structure(const uint8_t *buffer, size_t size, int require_sealed) {
    uint32_t command_count;
    uint32_t flags;
    uint32_t i;
    uint32_t composite_depth = 0U;
    size_t expected;

    if (buffer == NULL) return HHS179_RENDER_ERR_ARGUMENT;
    if (size < HHS179_RENDER_PACKET_HEADER_BYTES) return HHS179_RENDER_ERR_BOUNDS;
    if (memcmp(buffer + OFF_MAGIC, HHS179_MAGIC, sizeof(HHS179_MAGIC)) != 0) return HHS179_RENDER_ERR_VERSION;
    if (get_u32le(buffer + OFF_SCHEMA_VERSION) != HHS179_RENDER_PACKET_SCHEMA_VERSION) return HHS179_RENDER_ERR_VERSION;
    if (get_u32le(buffer + OFF_HEADER_BYTES) != HHS179_RENDER_PACKET_HEADER_BYTES) return HHS179_RENDER_ERR_VERSION;
    if (get_u32le(buffer + OFF_COMMAND_BYTES) != HHS179_RENDER_COMMAND_BYTES) return HHS179_RENDER_ERR_VERSION;
    if (get_u32le(buffer + OFF_ENDIAN) != HHS179_RENDER_ENDIAN_MARKER) return HHS179_RENDER_ERR_ENDIAN;
    if (get_u32le(buffer + OFF_RESERVED0) != 0U) return HHS179_RENDER_ERR_VERSION;
    if (get_u32le(buffer + OFF_TARGET_WIDTH) == 0U || get_u32le(buffer + OFF_TARGET_HEIGHT) == 0U) return HHS179_RENDER_ERR_BOUNDS;
    if (get_u64le(buffer + OFF_TIME_DEN) == 0U) return HHS179_RENDER_ERR_BOUNDS;

    command_count = get_u32le(buffer + OFF_COMMAND_COUNT);
    expected = hhs179_render_packet_required_bytes(command_count);
    if (expected == 0U || expected != size || get_u32le(buffer + OFF_TOTAL_BYTES) != (uint32_t)expected) return HHS179_RENDER_ERR_BOUNDS;

    flags = get_u32le(buffer + OFF_FLAGS);
    if ((flags & HHS179_RENDER_PACKET_FLAG_PROJECTION_ONLY) == 0U) return HHS179_RENDER_ERR_ARGUMENT;
    if (require_sealed && (flags & HHS179_RENDER_PACKET_FLAG_SEALED) == 0U) return HHS179_RENDER_ERR_SEALED;

    if ((flags & HHS179_RENDER_PACKET_FLAG_COMPATIBILITY_UNADMITTED) == 0U) {
        if (!identity_nonzero(buffer + OFF_SCENE_HASH216, HHS179_RENDER_HASH216_BYTES)
            || !identity_nonzero(buffer + OFF_FRAME_HASH216, HHS179_RENDER_HASH216_BYTES)
            || !identity_nonzero(buffer + OFF_RESOURCE_HASH216, HHS179_RENDER_HASH216_BYTES)
            || !identity_nonzero(buffer + OFF_CAMERA_HASH72, HHS179_RENDER_HASH72_BYTES)) {
            return HHS179_RENDER_ERR_IDENTITY;
        }
    }

    for (i = 0U; i < command_count; ++i) {
        const uint8_t *cmd = buffer + HHS179_RENDER_PACKET_HEADER_BYTES + (size_t)i * HHS179_RENDER_COMMAND_BYTES;
        const uint16_t opcode = get_u16le(cmd);
        const uint64_t resource_id = get_u64le(cmd + 8U);
        if (!known_opcode(opcode)) return HHS179_RENDER_ERR_OPCODE;
        if (get_u32le(cmd + 4U) != HHS179_RENDER_COMMAND_BYTES) return HHS179_RENDER_ERR_BOUNDS;
        if (i == 0U && opcode != HHS179_CMD_BEGIN_FRAME) return HHS179_RENDER_ERR_SEQUENCE;
        if (i + 1U == command_count && opcode != HHS179_CMD_END_FRAME) return HHS179_RENDER_ERR_SEQUENCE;
        if (i != 0U && opcode == HHS179_CMD_BEGIN_FRAME) return HHS179_RENDER_ERR_SEQUENCE;
        if (i + 1U != command_count && opcode == HHS179_CMD_END_FRAME) return HHS179_RENDER_ERR_SEQUENCE;
        if (opcode == HHS179_CMD_BEGIN_COMPOSITE_PASS) {
            if (composite_depth != 0U) return HHS179_RENDER_ERR_SEQUENCE;
            composite_depth = 1U;
        } else if (opcode == HHS179_CMD_END_COMPOSITE_PASS) {
            if (composite_depth != 1U) return HHS179_RENDER_ERR_SEQUENCE;
            composite_depth = 0U;
        }
        if ((draw_opcode(opcode)
             || opcode == HHS179_CMD_SET_CAMERA
             || opcode == HHS179_CMD_BIND_PIPELINE
             || opcode == HHS179_CMD_BIND_MATERIAL
             || opcode == HHS179_CMD_BIND_TEXTURES
             || opcode == HHS179_CMD_APPLY_EFFECT)
            && resource_id == 0U) {
            return HHS179_RENDER_ERR_IDENTITY;
        }
    }
    if (composite_depth != 0U) return HHS179_RENDER_ERR_SEQUENCE;
    return HHS179_RENDER_OK;
}

uint64_t hhs179_render_packet_projection_fingerprint(const uint8_t *buffer, size_t size) {
    uint64_t h = UINT64_C(14695981039346656037);
    size_t i;
    if (buffer == NULL || size < HHS179_RENDER_PACKET_HEADER_BYTES) return 0U;
    for (i = 0U; i < size; ++i) {
        if (i >= OFF_FINGERPRINT && i < OFF_FINGERPRINT + 8U) continue;
        h ^= (uint64_t)buffer[i];
        h *= UINT64_C(1099511628211);
    }
    return h;
}

HHS179RenderStatusV1 hhs179_render_packet_init(
    uint8_t *buffer,
    size_t capacity,
    const HHS179RenderPacketInitV1 *init,
    uint32_t command_count
) {
    const size_t required = hhs179_render_packet_required_bytes(command_count);
    uint32_t flags;
    if (buffer == NULL || init == NULL || init->struct_size != sizeof(*init)) return HHS179_RENDER_ERR_ARGUMENT;
    if (required == 0U || capacity < required || required > UINT32_MAX) return HHS179_RENDER_ERR_CAPACITY;
    if (init->target_width == 0U || init->target_height == 0U || init->exact_time_den == 0U) return HHS179_RENDER_ERR_BOUNDS;
    flags = (init->flags | HHS179_RENDER_PACKET_FLAG_PROJECTION_ONLY) & ~HHS179_RENDER_PACKET_FLAG_SEALED;

    memset(buffer, 0, required);
    memcpy(buffer + OFF_MAGIC, HHS179_MAGIC, sizeof(HHS179_MAGIC));
    put_u32le(buffer + OFF_SCHEMA_VERSION, HHS179_RENDER_PACKET_SCHEMA_VERSION);
    put_u32le(buffer + OFF_HEADER_BYTES, HHS179_RENDER_PACKET_HEADER_BYTES);
    put_u32le(buffer + OFF_COMMAND_BYTES, HHS179_RENDER_COMMAND_BYTES);
    put_u32le(buffer + OFF_COMMAND_COUNT, command_count);
    put_u32le(buffer + OFF_TOTAL_BYTES, (uint32_t)required);
    put_u32le(buffer + OFF_ENDIAN, HHS179_RENDER_ENDIAN_MARKER);
    put_u32le(buffer + OFF_FLAGS, flags);
    put_u32le(buffer + OFF_PROJECTION_PROFILE, init->projection_profile);
    put_u32le(buffer + OFF_TARGET_WIDTH, init->target_width);
    put_u32le(buffer + OFF_TARGET_HEIGHT, init->target_height);
    put_u32le(buffer + OFF_TARGET_FORMAT, init->target_format);
    put_u64le(buffer + OFF_FRAME_INDEX, init->frame_index);
    put_u64le(buffer + OFF_TIME_NUM, (uint64_t)init->exact_time_num);
    put_u64le(buffer + OFF_TIME_DEN, init->exact_time_den);
    memcpy(buffer + OFF_SCENE_HASH216, init->scene_snapshot_hash216, HHS179_RENDER_HASH216_BYTES);
    memcpy(buffer + OFF_FRAME_HASH216, init->frame_hash216, HHS179_RENDER_HASH216_BYTES);
    memcpy(buffer + OFF_PRIOR_HASH216, init->prior_frame_hash216, HHS179_RENDER_HASH216_BYTES);
    memcpy(buffer + OFF_RESOURCE_HASH216, init->resource_manifest_hash216, HHS179_RENDER_HASH216_BYTES);
    memcpy(buffer + OFF_CAMERA_HASH72, init->camera_hash72, HHS179_RENDER_HASH72_BYTES);
    memcpy(buffer + OFF_SOFTWARE_DIGEST, init->software_digest_sha256, HHS179_RENDER_SHA256_BYTES);
    memcpy(buffer + OFF_BACKEND_EVIDENCE, init->backend_evidence_sha256, HHS179_RENDER_SHA256_BYTES);
    return HHS179_RENDER_OK;
}

HHS179RenderStatusV1 hhs179_render_packet_write_command(
    uint8_t *buffer,
    size_t capacity,
    uint32_t index,
    const HHS179RenderCommandV1 *command
) {
    uint32_t count;
    size_t required;
    uint8_t *dst;
    if (buffer == NULL || command == NULL) return HHS179_RENDER_ERR_ARGUMENT;
    if (capacity < HHS179_RENDER_PACKET_HEADER_BYTES) return HHS179_RENDER_ERR_CAPACITY;
    if ((get_u32le(buffer + OFF_FLAGS) & HHS179_RENDER_PACKET_FLAG_SEALED) != 0U) return HHS179_RENDER_ERR_SEALED;
    count = get_u32le(buffer + OFF_COMMAND_COUNT);
    required = hhs179_render_packet_required_bytes(count);
    if (required == 0U || capacity < required || index >= count) return HHS179_RENDER_ERR_BOUNDS;
    if (!known_opcode(command->opcode)) return HHS179_RENDER_ERR_OPCODE;
    if (command->byte_length != HHS179_RENDER_COMMAND_BYTES) return HHS179_RENDER_ERR_BOUNDS;
    dst = buffer + HHS179_RENDER_PACKET_HEADER_BYTES + (size_t)index * HHS179_RENDER_COMMAND_BYTES;
    put_u16le(dst, command->opcode);
    put_u16le(dst + 2U, command->flags);
    put_u32le(dst + 4U, command->byte_length);
    put_u64le(dst + 8U, command->resource_id);
    put_u64le(dst + 16U, command->arg0);
    put_u64le(dst + 24U, command->arg1);
    return HHS179_RENDER_OK;
}

HHS179RenderStatusV1 hhs179_render_packet_seal(uint8_t *buffer, size_t size) {
    HHS179RenderStatusV1 status;
    uint32_t flags;
    uint64_t fingerprint;
    if (buffer == NULL) return HHS179_RENDER_ERR_ARGUMENT;
    if (size < HHS179_RENDER_PACKET_HEADER_BYTES) return HHS179_RENDER_ERR_BOUNDS;
    if ((get_u32le(buffer + OFF_FLAGS) & HHS179_RENDER_PACKET_FLAG_SEALED) != 0U) return HHS179_RENDER_ERR_SEALED;
    status = validate_structure(buffer, size, 0);
    if (status != HHS179_RENDER_OK) return status;
    flags = get_u32le(buffer + OFF_FLAGS) | HHS179_RENDER_PACKET_FLAG_SEALED;
    put_u32le(buffer + OFF_FLAGS, flags);
    put_u64le(buffer + OFF_FINGERPRINT, 0U);
    fingerprint = hhs179_render_packet_projection_fingerprint(buffer, size);
    put_u64le(buffer + OFF_FINGERPRINT, fingerprint);
    return HHS179_RENDER_OK;
}

HHS179RenderStatusV1 hhs179_render_packet_validate(const uint8_t *buffer, size_t size) {
    HHS179RenderStatusV1 status = validate_structure(buffer, size, 1);
    uint64_t stored;
    uint64_t actual;
    if (status != HHS179_RENDER_OK) return status;
    stored = get_u64le(buffer + OFF_FINGERPRINT);
    actual = hhs179_render_packet_projection_fingerprint(buffer, size);
    if (stored == 0U || stored != actual) return HHS179_RENDER_ERR_FINGERPRINT;
    return HHS179_RENDER_OK;
}

HHS179RenderStatusV1 hhs179_render_commands_export(
    const uint8_t *sealed_packet,
    size_t sealed_size,
    uint8_t *out_buffer,
    size_t out_capacity,
    size_t *out_size
) {
    HHS179RenderStatusV1 status;
    if (sealed_packet == NULL || out_size == NULL) return HHS179_RENDER_ERR_ARGUMENT;
    *out_size = sealed_size;
    status = hhs179_render_packet_validate(sealed_packet, sealed_size);
    if (status != HHS179_RENDER_OK) return status;
    if (out_buffer == NULL || out_capacity < sealed_size) return HHS179_RENDER_ERR_CAPACITY;
    memcpy(out_buffer, sealed_packet, sealed_size);
    return HHS179_RENDER_OK;
}
