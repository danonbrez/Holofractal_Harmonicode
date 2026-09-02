#include "../include/hhs179_graphics.h"

#include <string.h>

uint32_t hhs179_graphics_version(void) {
    return HHS179_GRAPHICS_VERSION;
}

static int hhs179_scene_valid(const HHS179Scene *scene) {
    return scene != NULL &&
           scene->struct_size == sizeof(*scene) &&
           scene->version == HHS179_GRAPHICS_VERSION &&
           scene->width >= 1U && scene->width <= HHS179_MAX_DIMENSION &&
           scene->height >= 1U && scene->height <= HHS179_MAX_DIMENSION &&
           scene->node_count <= HHS179_MAX_NODES &&
           scene->canonical_mutation_authority == 0U &&
           scene->floating_point_authority == 0U;
}

HHS179Status hhs179_scene_init(
    HHS179Scene *scene,
    uint32_t width,
    uint32_t height,
    HHS179RGBA16 background
) {
    if (scene == NULL)
        return HHS179_INVALID_ARGUMENT;
    if (width < 1U || width > HHS179_MAX_DIMENSION ||
        height < 1U || height > HHS179_MAX_DIMENSION)
        return HHS179_RANGE_ERROR;
    memset(scene, 0, sizeof(*scene));
    scene->struct_size = (uint32_t)sizeof(*scene);
    scene->version = HHS179_GRAPHICS_VERSION;
    scene->width = width;
    scene->height = height;
    scene->background = background;
    return HHS179_OK;
}

HHS179Status hhs179_scene_add_node(HHS179Scene *scene, const HHS179Node *node) {
    uint32_t i;
    if (!hhs179_scene_valid(scene) || node == NULL)
        return HHS179_INVALID_ARGUMENT;
    if (scene->node_count >= HHS179_MAX_NODES)
        return HHS179_CAPACITY_ERROR;
    if (node->kind != HHS179_NODE_RECT && node->kind != HHS179_NODE_POINT)
        return HHS179_RANGE_ERROR;
    if (node->w_q16 < 0 || node->h_q16 < 0)
        return HHS179_RANGE_ERROR;
    for (i = 0U; i < scene->node_count; ++i) {
        if (scene->nodes[i].node_id == node->node_id)
            return HHS179_INVARIANT_ERROR;
    }
    scene->nodes[scene->node_count++] = *node;
    return HHS179_OK;
}

static int hhs179_node_before(const HHS179Node *left, const HHS179Node *right) {
    if (left->layer != right->layer)
        return left->layer < right->layer;
    return left->node_id < right->node_id;
}

HHS179Status hhs179_command_stream_build(
    const HHS179Scene *scene,
    HHS179CommandStream *stream
) {
    HHS179Node ordered[HHS179_MAX_NODES];
    uint32_t i, j;
    if (!hhs179_scene_valid(scene) || stream == NULL)
        return HHS179_INVALID_ARGUMENT;
    memset(stream, 0, sizeof(*stream));
    stream->struct_size = (uint32_t)sizeof(*stream);
    stream->version = HHS179_GRAPHICS_VERSION;
    stream->width = scene->width;
    stream->height = scene->height;
    stream->commands[0].op = HHS179_CMD_CLEAR;
    stream->commands[0].color = scene->background;
    stream->command_count = 1U;
    memcpy(ordered, scene->nodes, sizeof(HHS179Node) * scene->node_count);
    for (i = 1U; i < scene->node_count; ++i) {
        HHS179Node key = ordered[i];
        j = i;
        while (j > 0U && hhs179_node_before(&key, &ordered[j - 1U])) {
            ordered[j] = ordered[j - 1U];
            --j;
        }
        ordered[j] = key;
    }
    for (i = 0U; i < scene->node_count; ++i) {
        HHS179Command *command = &stream->commands[stream->command_count++];
        command->op = ordered[i].kind == HHS179_NODE_RECT
            ? HHS179_CMD_RECT : HHS179_CMD_POINT;
        command->x_q16 = ordered[i].x_q16;
        command->y_q16 = ordered[i].y_q16;
        command->w_q16 = ordered[i].w_q16;
        command->h_q16 = ordered[i].h_q16;
        command->color = ordered[i].color;
    }
    return HHS179_OK;
}

static uint16_t hhs179_blend_channel(
    uint16_t dst_c,
    uint16_t dst_a,
    uint16_t src_c,
    uint16_t src_a,
    uint32_t out_a
) {
    uint64_t inv = UINT64_C(65535) - src_a;
    uint64_t premul =
        (uint64_t)src_c * src_a +
        (((uint64_t)dst_c * dst_a * inv) + UINT64_C(32767)) / UINT64_C(65535);
    if (out_a == 0U)
        return 0U;
    premul = (premul + out_a / 2U) / out_a;
    return (uint16_t)(premul > UINT64_C(65535) ? UINT64_C(65535) : premul);
}

static void hhs179_blend(HHS179RGBA16 *dst, HHS179RGBA16 src) {
    uint64_t inv = UINT64_C(65535) - src.a;
    uint32_t out_a = (uint32_t)src.a +
        (uint32_t)((((uint64_t)dst->a * inv) + UINT64_C(32767)) / UINT64_C(65535));
    if (out_a > 65535U)
        out_a = 65535U;
    dst->r = hhs179_blend_channel(dst->r, dst->a, src.r, src.a, out_a);
    dst->g = hhs179_blend_channel(dst->g, dst->a, src.g, src.a, out_a);
    dst->b = hhs179_blend_channel(dst->b, dst->a, src.b, src.a, out_a);
    dst->a = (uint16_t)out_a;
}

static int32_t hhs179_pixel_floor(int32_t q16) {
    if (q16 >= 0)
        return q16 / HHS179_Q16_ONE;
    return -(((-q16) + HHS179_Q16_ONE - 1) / HHS179_Q16_ONE);
}

HHS179Status hhs179_software_render_rgba16(
    const HHS179CommandStream *stream,
    HHS179RGBA16 *pixels,
    size_t pixel_capacity
) {
    uint32_t i;
    size_t required;
    if (stream == NULL || pixels == NULL)
        return HHS179_INVALID_ARGUMENT;
    if (stream->struct_size != sizeof(*stream) ||
        stream->version != HHS179_GRAPHICS_VERSION ||
        stream->width < 1U || stream->width > HHS179_MAX_DIMENSION ||
        stream->height < 1U || stream->height > HHS179_MAX_DIMENSION ||
        stream->command_count < 1U ||
        stream->command_count > HHS179_MAX_COMMANDS ||
        stream->canonical_mutation_authority != 0U ||
        stream->floating_point_authority != 0U)
        return HHS179_INVARIANT_ERROR;
    required = (size_t)stream->width * (size_t)stream->height;
    if (pixel_capacity < required)
        return HHS179_CAPACITY_ERROR;
    memset(pixels, 0, required * sizeof(*pixels));

    for (i = 0U; i < stream->command_count; ++i) {
        const HHS179Command *command = &stream->commands[i];
        if (command->op == HHS179_CMD_CLEAR) {
            size_t p;
            for (p = 0U; p < required; ++p)
                pixels[p] = command->color;
        } else if (command->op == HHS179_CMD_RECT ||
                   command->op == HHS179_CMD_POINT) {
            int32_t x = hhs179_pixel_floor(command->x_q16);
            int32_t y = hhs179_pixel_floor(command->y_q16);
            int32_t w = command->op == HHS179_CMD_POINT ? 1
                : hhs179_pixel_floor(command->w_q16);
            int32_t h = command->op == HHS179_CMD_POINT ? 1
                : hhs179_pixel_floor(command->h_q16);
            int32_t px, py;
            if (w <= 0 || h <= 0)
                continue;
            for (py = y; py < y + h; ++py) {
                if (py < 0 || py >= (int32_t)stream->height)
                    continue;
                for (px = x; px < x + w; ++px) {
                    size_t p;
                    if (px < 0 || px >= (int32_t)stream->width)
                        continue;
                    p = (size_t)py * stream->width + (size_t)px;
                    hhs179_blend(&pixels[p], command->color);
                }
            }
        } else {
            return HHS179_RANGE_ERROR;
        }
    }
    return HHS179_OK;
}

HHS179Status hhs179_shader_ir_validate(const HHS179ShaderIR *ir) {
    uint32_t i, j;
    if (ir == NULL)
        return HHS179_INVALID_ARGUMENT;
    if (ir->struct_size != sizeof(*ir) ||
        ir->version != HHS179_GRAPHICS_VERSION ||
        ir->node_count < 1U || ir->node_count > 256U ||
        ir->canonical_mutation_authority != 0U)
        return HHS179_INVARIANT_ERROR;
    for (i = 0U; i < ir->node_count; ++i) {
        const HHS179ShaderNode *node = &ir->nodes[i];
        if (node->op < HHS179_SHADER_INPUT_POSITION ||
            node->op > HHS179_SHADER_OUTPUT_COLOR)
            return HHS179_RANGE_ERROR;
        if (node->op == HHS179_SHADER_PHASE_COLOR && node->phase216 > 215U)
            return HHS179_RANGE_ERROR;
        for (j = 0U; j < i; ++j) {
            if (ir->nodes[j].node_id == node->node_id)
                return HHS179_INVARIANT_ERROR;
        }
    }
    return HHS179_OK;
}

uint64_t hhs179_command_stream_fingerprint64(const HHS179CommandStream *stream) {
    const unsigned char *bytes = (const unsigned char *)stream;
    uint64_t hash = UINT64_C(1469598103934665603);
    size_t i;
    size_t length;
    if (stream == NULL || stream->command_count > HHS179_MAX_COMMANDS)
        return 0U;
    length = offsetof(HHS179CommandStream, commands) +
        (size_t)stream->command_count * sizeof(HHS179Command);
    for (i = 0U; i < length; ++i) {
        hash ^= bytes[i];
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}
