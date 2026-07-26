#ifndef HHS_VM81_GAME_TEXTURE_H
#define HHS_VM81_GAME_TEXTURE_H

#include "hhs_vm81_game_sprite.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_VM81_TEXTURE_FIELD       (1U << 0)
#define HHS_VM81_TEXTURE_MIDGROUND   (1U << 1)
#define HHS_VM81_TEXTURE_MATERIALS   (1U << 2)
#define HHS_VM81_TEXTURE_SEMANTIC    (1U << 3)
#define HHS_VM81_TEXTURE_PLAYER      (1U << 4)
#define HHS_VM81_TEXTURE_ALL         \
    (HHS_VM81_TEXTURE_FIELD | HHS_VM81_TEXTURE_MIDGROUND | \
     HHS_VM81_TEXTURE_MATERIALS | HHS_VM81_TEXTURE_SEMANTIC | \
     HHS_VM81_TEXTURE_PLAYER)

#define HHS_VM81_TEXTURE_RGBA_BYTES HHS_VM81_GAME_SPRITE_RGBA_BYTES

typedef struct HHSVM81GameTextureReport {
    uint32_t width;
    uint32_t height;
    uint32_t texture_flags;
    uint32_t unique_color_buckets;
    uint32_t nontransparent_pixels;
    uint32_t field_writes;
    uint32_t midground_writes;
    uint32_t material_writes;
    uint32_t semantic_writes;
    uint32_t player_writes;
    uint32_t base_projection_unchanged;
    uint32_t state_unchanged;
    HHSHash72 inherited_frame_hash72;
    HHSHash216 inherited_frame_hash216;
    HHSHash72 frame_hash72;
    HHSHash216 frame_hash216;
    HHSHash216 source_state_hash216;
} HHSVM81GameTextureReport;

HHSVM81GameStatus hhs_vm81_game_texture_render_rgba(
    const HHSVM81GameRelease* release,
    uint32_t texture_flags,
    uint8_t* out_rgba,
    size_t out_capacity,
    HHSVM81GameTextureReport* report
);

HHSVM81GameStatus hhs_vm81_game_texture_write_ppm(
    const HHSVM81GameRelease* release,
    uint32_t texture_flags,
    const char* path,
    HHSVM81GameTextureReport* report
);

#ifdef __cplusplus
}
#endif

#endif
