#include "hhs179_graphics.h"
#include <assert.h>
#include <stdlib.h>

int main(void) {
    HHS179Scene *scene = calloc(1, sizeof(*scene));
    HHS179CommandStream *stream = calloc(1, sizeof(*stream));
    HHS179RGBA16 bg = {0, 0, 0, 65535};
    HHS179Node node = {1U, HHS179_NODE_RECT, 2 * HHS179_Q16_ONE, 3 * HHS179_Q16_ONE, 4 * HHS179_Q16_ONE, 2 * HHS179_Q16_ONE, 1, {65535, 0, 0, 65535}};
    HHS179RGBA16 *pixels;
    uint64_t fingerprint;
    assert(scene && stream);
    assert(hhs179_scene_init(scene, 16U, 12U, bg) == HHS179_OK);
    assert(hhs179_scene_add_node(scene, &node) == HHS179_OK);
    assert(hhs179_command_stream_build(scene, stream) == HHS179_OK);
    assert(stream->command_count == 2U);
    assert(stream->canonical_mutation_authority == 0U);
    assert(stream->floating_point_authority == 0U);
    fingerprint = hhs179_command_stream_fingerprint64(stream);
    assert(fingerprint != 0U);
    pixels = calloc(16U * 12U, sizeof(*pixels));
    assert(pixels);
    assert(hhs179_software_render_rgba16(stream, pixels, 16U * 12U) == HHS179_OK);
    assert(pixels[3U * 16U + 2U].r == 65535U);
    free(pixels);
    free(stream);
    free(scene);
    return 0;
}
