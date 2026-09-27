#include "hhs_pass179_render_command_v1.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void fill(uint8_t *p, size_t n, uint8_t c) {
    size_t i;
    for (i = 0U; i < n; ++i) p[i] = (uint8_t)(c + (uint8_t)(i % 7U));
}

static HHS179RenderCommandV1 cmd(uint16_t opcode, uint64_t resource_id, uint64_t arg0, uint64_t arg1) {
    HHS179RenderCommandV1 out;
    out.opcode = opcode;
    out.flags = 0U;
    out.byte_length = HHS179_RENDER_COMMAND_BYTES;
    out.resource_id = resource_id;
    out.arg0 = arg0;
    out.arg1 = arg1;
    return out;
}

int main(void) {
    enum { COMMAND_COUNT = 14 };
    const size_t bytes = hhs179_render_packet_required_bytes(COMMAND_COUNT);
    uint8_t *packet = (uint8_t *)calloc(bytes, 1U);
    HHS179RenderPacketInitV1 init;
    HHS179RenderCommandV1 commands[COMMAND_COUNT];
    HHS179RenderCommandV1 replacement;
    uint64_t fingerprint;
    uint8_t *exported = (uint8_t *)calloc(bytes, 1U);
    size_t exported_size = 0U;
    unsigned i;

    assert(packet != NULL);
    assert(exported != NULL);
    assert(bytes == HHS179_RENDER_PACKET_HEADER_BYTES + COMMAND_COUNT * HHS179_RENDER_COMMAND_BYTES);
    memset(&init, 0, sizeof(init));
    init.struct_size = (uint32_t)sizeof(init);
    init.flags = 0U;
    init.projection_profile = 1U;
    init.target_width = 1920U;
    init.target_height = 1080U;
    init.target_format = 1U;
    init.frame_index = UINT64_C(0x0102030405060708);
    init.exact_time_num = 17;
    init.exact_time_den = 60U;
    fill(init.scene_snapshot_hash216, sizeof(init.scene_snapshot_hash216), (uint8_t)'A');
    fill(init.frame_hash216, sizeof(init.frame_hash216), (uint8_t)'H');
    fill(init.prior_frame_hash216, sizeof(init.prior_frame_hash216), (uint8_t)'P');
    fill(init.resource_manifest_hash216, sizeof(init.resource_manifest_hash216), (uint8_t)'R');
    fill(init.camera_hash72, sizeof(init.camera_hash72), (uint8_t)'C');

    assert(hhs179_render_packet_init(packet, bytes, &init, COMMAND_COUNT) == HHS179_RENDER_OK);
    assert(packet[56] == 0x08U && packet[63] == 0x01U);

    commands[0] = cmd(HHS179_CMD_BEGIN_FRAME, 0U, 0U, 0U);
    commands[1] = cmd(HHS179_CMD_SET_VIEWPORT, 0U, 1920U, 1080U);
    commands[2] = cmd(HHS179_CMD_SET_CAMERA, 1U, 0U, 0U);
    commands[3] = cmd(HHS179_CMD_SET_TARGET, 2U, 0U, 0U);
    commands[4] = cmd(HHS179_CMD_CLEAR, 0U, 3U, 0U);
    commands[5] = cmd(HHS179_CMD_BIND_PIPELINE, 10U, 0U, 0U);
    commands[6] = cmd(HHS179_CMD_DRAW_POINTS, 3U, 0U, 0U);
    commands[7] = cmd(HHS179_CMD_DRAW_POINTS, 4U, 0U, 0U);
    commands[8] = cmd(HHS179_CMD_BEGIN_COMPOSITE_PASS, 0U, 0U, 0U);
    commands[9] = cmd(HHS179_CMD_SET_CAMERA, 5U, 0U, 0U);
    commands[10] = cmd(HHS179_CMD_SET_TARGET, 0U, 0U, 0U);
    commands[11] = cmd(HHS179_CMD_DRAW_MESHES, 6U, 0U, 0U);
    commands[12] = cmd(HHS179_CMD_END_COMPOSITE_PASS, 0U, 0U, 0U);
    commands[13] = cmd(HHS179_CMD_END_FRAME, 0U, 0U, 0U);

    for (i = 0U; i < COMMAND_COUNT; ++i) {
        assert(hhs179_render_packet_write_command(packet, bytes, i, &commands[i]) == HHS179_RENDER_OK);
    }
    assert(hhs179_render_packet_seal(packet, bytes) == HHS179_RENDER_OK);
    assert(hhs179_render_packet_validate(packet, bytes) == HHS179_RENDER_OK);
    fingerprint = hhs179_render_packet_projection_fingerprint(packet, bytes);
    assert(fingerprint != 0U);
    assert(hhs179_render_commands_export(packet, bytes, exported, bytes, &exported_size) == HHS179_RENDER_OK);
    assert(exported_size == bytes);
    assert(memcmp(packet, exported, bytes) == 0);

    replacement = cmd(HHS179_CMD_CLEAR, 0U, 0U, 0U);
    assert(hhs179_render_packet_write_command(packet, bytes, 4U, &replacement) == HHS179_RENDER_ERR_SEALED);

    packet[HHS179_RENDER_PACKET_HEADER_BYTES + 6U * HHS179_RENDER_COMMAND_BYTES + 16U] ^= 1U;
    assert(hhs179_render_packet_validate(packet, bytes) == HHS179_RENDER_ERR_FINGERPRINT);

    free(exported);
    free(packet);
    puts("PASS hhs_pass179_render_command_v1");
    return 0;
}
