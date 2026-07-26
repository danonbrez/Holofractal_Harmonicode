#include "hhs_vm81_game_texture.h"

#include <stdio.h>
#include <string.h>

#define HHS_TEXTURE_PIXEL_INDEX(x, y) \
    ((((size_t)(y) * (size_t)HHS_VM81_GAME_SPRITE_WIDTH) + (size_t)(x)) * HHS_VM81_GAME_SPRITE_CHANNELS)

typedef struct HHSVM81TextureMetrics {
    uint32_t field_writes;
    uint32_t midground_writes;
    uint32_t material_writes;
    uint32_t semantic_writes;
    uint32_t player_writes;
} HHSVM81TextureMetrics;

static int hhs_texture_inside(int x, int y) {
    return x >= 0 && y >= 0 && x < HHS_VM81_GAME_SPRITE_WIDTH && y < HHS_VM81_GAME_SPRITE_HEIGHT;
}

static uint8_t hhs_texture_blend_channel(uint8_t dst, uint8_t src, uint8_t alpha) {
    uint32_t inverse = 255U - (uint32_t)alpha;
    return (uint8_t)(((uint32_t)dst * inverse + (uint32_t)src * (uint32_t)alpha + 127U) / 255U);
}

static void hhs_texture_blend(
    uint8_t* rgba,
    int x,
    int y,
    uint8_t r,
    uint8_t g,
    uint8_t b,
    uint8_t alpha,
    uint32_t* counter
) {
    size_t index;
    if (!rgba || alpha == 0U || !hhs_texture_inside(x, y)) return;
    index = HHS_TEXTURE_PIXEL_INDEX(x, y);
    rgba[index + 0U] = hhs_texture_blend_channel(rgba[index + 0U], r, alpha);
    rgba[index + 1U] = hhs_texture_blend_channel(rgba[index + 1U], g, alpha);
    rgba[index + 2U] = hhs_texture_blend_channel(rgba[index + 2U], b, alpha);
    rgba[index + 3U] = 255U;
    if (counter) (*counter)++;
}

static uint32_t hhs_texture_hash2(uint32_t x, uint32_t y, uint32_t seed) {
    uint32_t value = x * 0x45d9f3bU + y * 0x119de1f3U + seed * 0x27d4eb2dU + 0x9e3779b9U;
    value ^= value >> 16U;
    value *= 0x7feb352dU;
    value ^= value >> 15U;
    value *= 0x846ca68bU;
    value ^= value >> 16U;
    return value;
}

static int hhs_texture_abs_i(int value) {
    return value < 0 ? -value : value;
}

static int hhs_texture_tile_is_hazard(int tile_x, int tile_y) {
    return tile_y == 15 && (tile_x == 17 || tile_x == 44 || tile_x == 58);
}

static int hhs_texture_world_occupied(const HHSVM81GameRelease* release, int screen_x, int screen_y) {
    int world_x;
    int tile_x;
    int tile_y;
    if (!release || screen_x < 0 || screen_y < 0) return 1;
    world_x = screen_x + (int)release->vm.camera_x_px;
    tile_x = world_x / HHS_VM81_GAME_TILE_SIZE;
    tile_y = screen_y / HHS_VM81_GAME_TILE_SIZE;
    if (tile_x < 0 || tile_x >= HHS_VM81_GAME_LEVEL_TILES_X ||
        tile_y < 0 || tile_y >= HHS_VM81_GAME_LEVEL_TILES_Y) return 1;
    return release->vm.level[tile_y][tile_x] != 0U || hhs_texture_tile_is_hazard(tile_x, tile_y);
}

static void hhs_texture_field(
    const HHSVM81GameRelease* release,
    uint8_t* rgba,
    HHSVM81TextureMetrics* metrics
) {
    uint32_t seed = (uint32_t)release->vm.phase * 73U + (uint32_t)release->vm.lo_shu_set * 19U;
    int y;
    for (y = 10; y < HHS_VM81_GAME_SPRITE_HEIGHT; ++y) {
        int x;
        for (x = 0; x < HHS_VM81_GAME_SPRITE_WIDTH; ++x) {
            uint32_t wave_a = ((uint32_t)x * 3U + (uint32_t)y * 5U + seed + release->vm.camera_x_px / 2U) % 72U;
            uint32_t wave_b = ((uint32_t)x * 5U + (uint32_t)(HHS_VM81_GAME_SPRITE_HEIGHT - 1 - y) * 4U + seed * 2U + release->vm.camera_x_px / 3U) % 81U;
            uint32_t distance_a = wave_a > 36U ? wave_a - 36U : 36U - wave_a;
            uint32_t distance_b = wave_b > 40U ? wave_b - 40U : 40U - wave_b;
            uint32_t noise = hhs_texture_hash2((uint32_t)x, (uint32_t)y, seed);
            if (distance_a < 5U || distance_b < 4U) {
                uint8_t alpha = (uint8_t)(4U + (5U - (distance_a < 5U ? distance_a : 5U)) + (4U - (distance_b < 4U ? distance_b : 4U)));
                hhs_texture_blend(
                    rgba,
                    x,
                    y,
                    distance_a < distance_b ? 86U : 174U,
                    distance_a < distance_b ? 216U : 104U,
                    236U,
                    alpha,
                    &metrics->field_writes
                );
            }
            if ((noise & 31U) == 0U && y < 124) {
                hhs_texture_blend(rgba, x, y, 220U, 234U, 246U, 5U, &metrics->field_writes);
            } else if ((noise & 63U) == 1U) {
                hhs_texture_blend(rgba, x, y, 8U, 12U, 34U, 8U, &metrics->field_writes);
            }
        }
    }
}

static void hhs_texture_midground(
    const HHSVM81GameRelease* release,
    uint8_t* rgba,
    HHSVM81TextureMetrics* metrics
) {
    uint32_t slow_camera = release->vm.camera_x_px / 5U;
    uint32_t near_camera = release->vm.camera_x_px / 3U;
    uint8_t r = (uint8_t)(42U + ((uint32_t)release->vm.phase * 3U) % 42U);
    uint8_t g = (uint8_t)(76U + ((uint32_t)release->vm.lo_shu_set * 9U) % 52U);
    uint8_t b = (uint8_t)(126U + ((uint32_t)release->vm.phase * 5U) % 72U);
    int y;
    for (y = 54; y < 120; ++y) {
        int x;
        for (x = 0; x < HHS_VM81_GAME_SPRITE_WIDTH; ++x) {
            uint32_t world_far;
            uint32_t world_near;
            uint32_t arch;
            int arch_distance;
            uint32_t lattice;
            if (hhs_texture_world_occupied(release, x, y)) continue;
            world_far = (uint32_t)x + slow_camera;
            world_near = (uint32_t)x + near_camera;
            arch = world_far % 40U;
            arch_distance = hhs_texture_abs_i((int)arch - 20) + hhs_texture_abs_i(y - 82);
            lattice = (world_near * 3U + (uint32_t)y * 2U + (uint32_t)release->vm.phase * 5U) % 47U;
            if ((arch <= 2U || arch >= 38U) && y >= 76) {
                hhs_texture_blend(rgba, x, y, r, g, b, 23U, &metrics->midground_writes);
            }
            if (arch_distance >= 18 && arch_distance <= 20 && y >= 58 && y <= 101) {
                hhs_texture_blend(rgba, x, y, (uint8_t)(r + 14U), (uint8_t)(g + 16U), (uint8_t)(b + 18U), 28U, &metrics->midground_writes);
            }
            if (lattice == 0U || lattice == 1U) {
                hhs_texture_blend(rgba, x, y, 74U, 134U, 172U, 12U, &metrics->midground_writes);
            }
            if (y >= 104 && ((world_far + (uint32_t)y) % 11U) == 0U) {
                hhs_texture_blend(rgba, x, y, 24U, 48U, 76U, 18U, &metrics->midground_writes);
            }
        }
    }
}

static void hhs_texture_materials(
    const HHSVM81GameRelease* release,
    uint8_t* rgba,
    HHSVM81TextureMetrics* metrics
) {
    int screen_y;
    for (screen_y = 0; screen_y < HHS_VM81_GAME_SPRITE_HEIGHT; ++screen_y) {
        int screen_x;
        for (screen_x = 0; screen_x < HHS_VM81_GAME_SPRITE_WIDTH; ++screen_x) {
            int world_x = screen_x + (int)release->vm.camera_x_px;
            int tile_x = world_x / HHS_VM81_GAME_TILE_SIZE;
            int tile_y = screen_y / HHS_VM81_GAME_TILE_SIZE;
            int local_x = world_x % HHS_VM81_GAME_TILE_SIZE;
            int local_y = screen_y % HHS_VM81_GAME_TILE_SIZE;
            uint32_t seed;
            uint32_t grain;
            if (tile_x < 0 || tile_x >= HHS_VM81_GAME_LEVEL_TILES_X ||
                tile_y < 0 || tile_y >= HHS_VM81_GAME_LEVEL_TILES_Y) continue;
            seed = (uint32_t)(tile_x * 97 + tile_y * 53) + (uint32_t)release->vm.lo_shu_set * 11U;
            grain = hhs_texture_hash2((uint32_t)world_x, (uint32_t)screen_y, seed);
            if (release->vm.level[tile_y][tile_x] != 0U) {
                if (local_y == 2 || local_y == 6) {
                    hhs_texture_blend(rgba, screen_x, screen_y, 28U, 34U, 58U, 28U, &metrics->material_writes);
                }
                if (local_x == 0 && ((tile_x + tile_y) & 1) == 0) {
                    hhs_texture_blend(rgba, screen_x, screen_y, 132U, 154U, 176U, 28U, &metrics->material_writes);
                }
                if ((grain & 15U) == 0U) {
                    hhs_texture_blend(rgba, screen_x, screen_y, 182U, 194U, 214U, 20U, &metrics->material_writes);
                } else if ((grain & 31U) == 1U) {
                    hhs_texture_blend(rgba, screen_x, screen_y, 12U, 16U, 34U, 30U, &metrics->material_writes);
                }
                if (((world_x + screen_y + (int)release->vm.phase) % 29) == 0) {
                    hhs_texture_blend(rgba, screen_x, screen_y, 114U, 86U, 184U, 18U, &metrics->material_writes);
                }
            }
            if (hhs_texture_tile_is_hazard(tile_x, tile_y)) {
                uint32_t pulse = ((uint32_t)local_x * 5U + (uint32_t)local_y * 7U + release->player_frames * 3U + (uint32_t)release->vm.phase) % 18U;
                if (pulse < 5U) {
                    hhs_texture_blend(rgba, screen_x, screen_y, 255U, 236U, 144U, (uint8_t)(38U - pulse * 5U), &metrics->material_writes);
                }
            }
        }
    }
}

static void hhs_texture_ring(
    uint8_t* rgba,
    int center_x,
    int center_y,
    int radius,
    uint8_t r,
    uint8_t g,
    uint8_t b,
    uint8_t alpha,
    uint32_t* counter
) {
    int y;
    int inner = radius * radius - radius;
    int outer = radius * radius + radius;
    for (y = center_y - radius - 1; y <= center_y + radius + 1; ++y) {
        int x;
        for (x = center_x - radius - 1; x <= center_x + radius + 1; ++x) {
            int dx = x - center_x;
            int dy = y - center_y;
            int distance = dx * dx + dy * dy;
            if (distance >= inner && distance <= outer) {
                hhs_texture_blend(rgba, x, y, r, g, b, alpha, counter);
            }
        }
    }
}

static void hhs_texture_semantic(
    const HHSVM81GameRelease* release,
    uint8_t* rgba,
    HHSVM81TextureMetrics* metrics
) {
    static const int checkpoint_world_x[2] = {20 * HHS_VM81_GAME_TILE_SIZE + 4, 40 * HHS_VM81_GAME_TILE_SIZE + 4};
    int i;
    for (i = 0; i < 2; ++i) {
        int screen_x = checkpoint_world_x[i] - (int)release->vm.camera_x_px;
        int active = release->checkpoint > (uint32_t)i;
        int pulse = (int)((release->player_frames + (uint32_t)i * 11U + (uint32_t)release->vm.phase) % 9U);
        if (screen_x > -24 && screen_x < HHS_VM81_GAME_SPRITE_WIDTH + 24) {
            hhs_texture_ring(rgba, screen_x, 112, 10 + pulse / 3, active ? 86U : 68U, active ? 246U : 154U, 226U, active ? 38U : 24U, &metrics->semantic_writes);
            hhs_texture_ring(rgba, screen_x, 112, 15 + pulse / 2, 78U, 148U, 214U, 18U, &metrics->semantic_writes);
        }
    }
    {
        int goal_x = 61 * HHS_VM81_GAME_TILE_SIZE + 4 - (int)release->vm.camera_x_px;
        int pulse = (int)((release->player_frames + (uint32_t)release->vm.phase) % 12U);
        int ray;
        if (goal_x > -32 && goal_x < HHS_VM81_GAME_SPRITE_WIDTH + 32) {
            hhs_texture_ring(rgba, goal_x, 108, 13 + pulse / 3, 255U, 214U, 84U, 44U, &metrics->semantic_writes);
            hhs_texture_ring(rgba, goal_x, 108, 20 + pulse / 2, 244U, 124U, 76U, 24U, &metrics->semantic_writes);
            for (ray = -18; ray <= 18; ++ray) {
                if ((ray + pulse) % 6 == 0) {
                    hhs_texture_blend(rgba, goal_x + ray, 108 - hhs_texture_abs_i(ray) / 2, 255U, 226U, 132U, 26U, &metrics->semantic_writes);
                }
            }
        }
    }
}

static int hhs_texture_player_body_pixel(int x, int y, int walk) {
    if (y <= 1) return x >= 6 && x <= 9;
    if (y <= 5) return x >= 4 && x <= 11;
    if (y <= 10) return x >= 3 && x <= 12;
    if (y <= 13) return x >= 4 && x <= 11;
    if (walk == 0) return (x >= 4 && x <= 7) || (x >= 9 && x <= 12);
    return (x >= 2 && x <= 6) || (x >= 10 && x <= 14);
}

static void hhs_texture_player(
    const HHSVM81GameRelease* release,
    uint8_t* rgba,
    HHSVM81TextureMetrics* metrics
) {
    int base_x = release->vm.player.x_subpx / HHS_VM81_GAME_SUBPIXELS - (int)release->vm.camera_x_px;
    int base_y = release->vm.player.y_subpx / HHS_VM81_GAME_SUBPIXELS;
    int walk = release->vm.player.animation_state == HHS_GAME_ANIM_WALK ? (int)(release->vm.player.animation_frame & 1U) : 0;
    int moving = release->vm.player.vx_subpx != 0 || release->vm.player.vy_subpx != 0;
    int y;
    if (moving) {
        int echo;
        for (echo = 1; echo <= 2; ++echo) {
            int offset_x = release->vm.player.facing_right ? -echo * 3 : echo * 3;
            int offset_y = release->vm.player.vy_subpx < 0 ? echo * 2 : 0;
            for (y = 0; y < HHS_VM81_GAME_PLAYER_HEIGHT; ++y) {
                int x;
                for (x = 0; x < HHS_VM81_GAME_PLAYER_WIDTH; ++x) {
                    if (hhs_texture_player_body_pixel(x, y, walk) && ((x + y + echo) & 1) == 0) {
                        hhs_texture_blend(rgba, base_x + x + offset_x, base_y + y + offset_y, 96U, 132U, 246U, (uint8_t)(22U - echo * 6U), &metrics->player_writes);
                    }
                }
            }
        }
    }
    for (y = 0; y < HHS_VM81_GAME_PLAYER_HEIGHT; ++y) {
        int x;
        for (x = 0; x < HHS_VM81_GAME_PLAYER_WIDTH; ++x) {
            if (!hhs_texture_player_body_pixel(x, y, walk)) continue;
            if (y >= 6 && (x == 3 || x == 12 || y == 6 || y == 11)) {
                hhs_texture_blend(rgba, base_x + x, base_y + y, 216U, 240U, 255U, 54U, &metrics->player_writes);
            }
            if (y >= 7 && ((x * 3 + y + (int)release->vm.phase) % 8) == 0) {
                hhs_texture_blend(rgba, base_x + x, base_y + y, 118U, 78U, 224U, 72U, &metrics->player_writes);
            }
        }
    }
}

static uint32_t hhs_texture_count_unique_buckets(const uint8_t* rgba) {
    uint8_t buckets[4096];
    uint32_t count = 0U;
    int y;
    memset(buckets, 0, sizeof(buckets));
    for (y = 0; y < HHS_VM81_GAME_SPRITE_HEIGHT; ++y) {
        int x;
        for (x = 0; x < HHS_VM81_GAME_SPRITE_WIDTH; ++x) {
            size_t index = HHS_TEXTURE_PIXEL_INDEX(x, y);
            uint32_t bucket = ((uint32_t)(rgba[index] >> 4U) << 8U) |
                              ((uint32_t)(rgba[index + 1U] >> 4U) << 4U) |
                              (uint32_t)(rgba[index + 2U] >> 4U);
            if (buckets[bucket] == 0U) {
                buckets[bucket] = 1U;
                count++;
            }
        }
    }
    return count;
}

HHSVM81GameStatus hhs_vm81_game_texture_render_rgba(
    const HHSVM81GameRelease* release,
    uint32_t texture_flags,
    uint8_t* out_rgba,
    size_t out_capacity,
    HHSVM81GameTextureReport* report
) {
    HHSVM81GameRelease before;
    HHSVM81GameSpriteReport inherited;
    HHSVM81TextureMetrics metrics;
    HHSVM81GameStatus status;
    if (!release || !out_rgba || !report) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if ((texture_flags & ~HHS_VM81_TEXTURE_ALL) != 0U) return HHS_GAME_STATUS_INVALID_OPERAND;
    if (out_capacity < HHS_VM81_TEXTURE_RGBA_BYTES) return HHS_GAME_STATUS_OUTPUT_CAPACITY;
    before = *release;
    memset(report, 0, sizeof(*report));
    memset(&metrics, 0, sizeof(metrics));
    status = hhs_vm81_game_sprite_render_rgba(
        release,
        HHS_VM81_SPRITE_OVERLAY_ALL,
        out_rgba,
        out_capacity,
        &inherited
    );
    if (status != HHS_GAME_STATUS_OK || inherited.state_unchanged == 0U) return status;
    report->inherited_frame_hash72 = inherited.frame_hash72;
    report->inherited_frame_hash216 = inherited.frame_hash216;
    if ((texture_flags & HHS_VM81_TEXTURE_FIELD) != 0U) hhs_texture_field(release, out_rgba, &metrics);
    if ((texture_flags & HHS_VM81_TEXTURE_MIDGROUND) != 0U) hhs_texture_midground(release, out_rgba, &metrics);
    if ((texture_flags & HHS_VM81_TEXTURE_MATERIALS) != 0U) hhs_texture_materials(release, out_rgba, &metrics);
    if ((texture_flags & HHS_VM81_TEXTURE_SEMANTIC) != 0U) hhs_texture_semantic(release, out_rgba, &metrics);
    if ((texture_flags & HHS_VM81_TEXTURE_PLAYER) != 0U) hhs_texture_player(release, out_rgba, &metrics);
    report->width = HHS_VM81_GAME_SPRITE_WIDTH;
    report->height = HHS_VM81_GAME_SPRITE_HEIGHT;
    report->texture_flags = texture_flags;
    report->unique_color_buckets = hhs_texture_count_unique_buckets(out_rgba);
    report->nontransparent_pixels = HHS_VM81_GAME_SPRITE_WIDTH * HHS_VM81_GAME_SPRITE_HEIGHT;
    report->field_writes = metrics.field_writes;
    report->midground_writes = metrics.midground_writes;
    report->material_writes = metrics.material_writes;
    report->semantic_writes = metrics.semantic_writes;
    report->player_writes = metrics.player_writes;
    report->base_projection_unchanged = (uint32_t)(hhs_hash216_equal(&inherited.frame_hash216, &report->inherited_frame_hash216));
    report->state_unchanged = (uint32_t)(memcmp(release, &before, sizeof(before)) == 0);
    hhs_hash72_compute(out_rgba, HHS_VM81_TEXTURE_RGBA_BYTES, &report->frame_hash72);
    hhs_hash216_compute(out_rgba, HHS_VM81_TEXTURE_RGBA_BYTES, &report->frame_hash216);
    report->source_state_hash216 = release->vm.latest_state_identity_hash216;
    return report->state_unchanged != 0U ? HHS_GAME_STATUS_OK : HHS_GAME_STATUS_STATE_INVARIANT_FAILURE;
}

HHSVM81GameStatus hhs_vm81_game_texture_write_ppm(
    const HHSVM81GameRelease* release,
    uint32_t texture_flags,
    const char* path,
    HHSVM81GameTextureReport* report
) {
    uint8_t rgba[HHS_VM81_TEXTURE_RGBA_BYTES];
    HHSVM81GameStatus status;
    FILE* file;
    int y;
    if (!path) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    status = hhs_vm81_game_texture_render_rgba(release, texture_flags, rgba, sizeof(rgba), report);
    if (status != HHS_GAME_STATUS_OK) return status;
    file = fopen(path, "wb");
    if (!file) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if (fprintf(file, "P6\n%d %d\n255\n", HHS_VM81_GAME_SPRITE_WIDTH, HHS_VM81_GAME_SPRITE_HEIGHT) < 0) {
        (void)fclose(file);
        return HHS_GAME_STATUS_INVALID_ARGUMENT;
    }
    for (y = 0; y < HHS_VM81_GAME_SPRITE_HEIGHT; ++y) {
        int x;
        for (x = 0; x < HHS_VM81_GAME_SPRITE_WIDTH; ++x) {
            size_t index = HHS_TEXTURE_PIXEL_INDEX(x, y);
            if (fwrite(rgba + index, 1U, 3U, file) != 3U) {
                (void)fclose(file);
                return HHS_GAME_STATUS_INVALID_ARGUMENT;
            }
        }
    }
    if (fclose(file) != 0) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    return HHS_GAME_STATUS_OK;
}
