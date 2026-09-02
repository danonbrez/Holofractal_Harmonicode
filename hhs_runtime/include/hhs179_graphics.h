#ifndef HHS179_GRAPHICS_H
#define HHS179_GRAPHICS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS179_GRAPHICS_VERSION UINT32_C(0x00010000)
#define HHS179_MAX_NODES 8192U
#define HHS179_MAX_COMMANDS 8193U
#define HHS179_MAX_DIMENSION 1024U
#define HHS179_Q16_ONE INT32_C(65536)

typedef enum HHS179Status {
    HHS179_OK = 0,
    HHS179_INVALID_ARGUMENT = 1,
    HHS179_RANGE_ERROR = 2,
    HHS179_CAPACITY_ERROR = 3,
    HHS179_INVARIANT_ERROR = 4,
    HHS179_VERSION_ERROR = 5
} HHS179Status;

typedef enum HHS179NodeKind {
    HHS179_NODE_RECT = 1,
    HHS179_NODE_POINT = 2
} HHS179NodeKind;

typedef enum HHS179CommandOp {
    HHS179_CMD_CLEAR = 1,
    HHS179_CMD_RECT = 2,
    HHS179_CMD_POINT = 3
} HHS179CommandOp;

typedef struct HHS179RGBA16 {
    uint16_t r, g, b, a;
} HHS179RGBA16;

typedef struct HHS179Node {
    uint32_t node_id;
    uint32_t kind;
    int32_t x_q16;
    int32_t y_q16;
    int32_t w_q16;
    int32_t h_q16;
    int32_t layer;
    HHS179RGBA16 color;
} HHS179Node;

typedef struct HHS179Scene {
    uint32_t struct_size;
    uint32_t version;
    uint32_t width;
    uint32_t height;
    uint64_t frame_index;
    HHS179RGBA16 background;
    uint32_t node_count;
    uint32_t canonical_mutation_authority;
    uint32_t floating_point_authority;
    HHS179Node nodes[HHS179_MAX_NODES];
} HHS179Scene;

typedef struct HHS179Command {
    uint32_t op;
    int32_t x_q16;
    int32_t y_q16;
    int32_t w_q16;
    int32_t h_q16;
    HHS179RGBA16 color;
} HHS179Command;

typedef struct HHS179CommandStream {
    uint32_t struct_size;
    uint32_t version;
    uint32_t width;
    uint32_t height;
    uint32_t command_count;
    uint32_t canonical_mutation_authority;
    uint32_t floating_point_authority;
    HHS179Command commands[HHS179_MAX_COMMANDS];
} HHS179CommandStream;

typedef enum HHS179ShaderOp {
    HHS179_SHADER_INPUT_POSITION = 1,
    HHS179_SHADER_CONST_RGBA16 = 2,
    HHS179_SHADER_PHASE_COLOR = 3,
    HHS179_SHADER_ADD = 4,
    HHS179_SHADER_MUL = 5,
    HHS179_SHADER_OUTPUT_COLOR = 6
} HHS179ShaderOp;

typedef struct HHS179ShaderNode {
    uint32_t node_id;
    uint32_t op;
    uint32_t input_a;
    uint32_t input_b;
    uint32_t phase216;
    HHS179RGBA16 rgba16;
} HHS179ShaderNode;

typedef struct HHS179ShaderIR {
    uint32_t struct_size;
    uint32_t version;
    uint32_t node_count;
    uint32_t output_node_id;
    uint32_t canonical_mutation_authority;
    HHS179ShaderNode nodes[256];
} HHS179ShaderIR;

uint32_t hhs179_graphics_version(void);
HHS179Status hhs179_scene_init(
    HHS179Scene *scene,
    uint32_t width,
    uint32_t height,
    HHS179RGBA16 background
);
HHS179Status hhs179_scene_add_node(HHS179Scene *scene, const HHS179Node *node);
HHS179Status hhs179_command_stream_build(
    const HHS179Scene *scene,
    HHS179CommandStream *stream
);
HHS179Status hhs179_software_render_rgba16(
    const HHS179CommandStream *stream,
    HHS179RGBA16 *pixels,
    size_t pixel_capacity
);
HHS179Status hhs179_shader_ir_validate(const HHS179ShaderIR *ir);
uint64_t hhs179_command_stream_fingerprint64(const HHS179CommandStream *stream);

#ifdef __cplusplus
}
#endif
#endif
