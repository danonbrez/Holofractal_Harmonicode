#include "hhs_vm81_game_sprite.h"

#include <stdio.h>
#include <string.h>

#define HHS_SPRITE_PIXEL_INDEX(x, y) \
    ((((size_t)(y) * (size_t)HHS_VM81_GAME_SPRITE_WIDTH) + (size_t)(x)) * HHS_VM81_GAME_SPRITE_CHANNELS)

static uint8_t hhs_sprite_lerp_u8(uint8_t a, uint8_t b, uint32_t position, uint32_t maximum) {
    int32_t delta;
    int32_t value;
    if (maximum == 0U) return a;
    delta = (int32_t)b - (int32_t)a;
    value = (int32_t)a + (delta * (int32_t)position + (int32_t)(maximum / 2U)) / (int32_t)maximum;
    if (value < 0) value = 0;
    if (value > 255) value = 255;
    return (uint8_t)value;
}

static uint8_t hhs_sprite_blend_channel(uint8_t dst, uint8_t src, uint8_t alpha) {
    uint32_t inverse = 255U - (uint32_t)alpha;
    return (uint8_t)(((uint32_t)dst * inverse + (uint32_t)src * (uint32_t)alpha + 127U) / 255U);
}

static void hhs_sprite_put(uint8_t* rgba, int x, int y, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    size_t index;
    if (!rgba || x < 0 || y < 0 || x >= HHS_VM81_GAME_SPRITE_WIDTH || y >= HHS_VM81_GAME_SPRITE_HEIGHT) return;
    index = HHS_SPRITE_PIXEL_INDEX(x, y);
    rgba[index + 0U] = r;
    rgba[index + 1U] = g;
    rgba[index + 2U] = b;
    rgba[index + 3U] = a;
}

static void hhs_sprite_blend(uint8_t* rgba, int x, int y, uint8_t r, uint8_t g, uint8_t b, uint8_t alpha) {
    size_t index;
    if (!rgba || alpha == 0U || x < 0 || y < 0 || x >= HHS_VM81_GAME_SPRITE_WIDTH || y >= HHS_VM81_GAME_SPRITE_HEIGHT) return;
    index = HHS_SPRITE_PIXEL_INDEX(x, y);
    rgba[index + 0U] = hhs_sprite_blend_channel(rgba[index + 0U], r, alpha);
    rgba[index + 1U] = hhs_sprite_blend_channel(rgba[index + 1U], g, alpha);
    rgba[index + 2U] = hhs_sprite_blend_channel(rgba[index + 2U], b, alpha);
    rgba[index + 3U] = 255U;
}

static int hhs_sprite_tile_is_hazard(int tile_x, int tile_y) {
    if (tile_y != 15) return 0;
    return tile_x == 17 || tile_x == 44 || tile_x == 58;
}

static void hhs_sprite_background(const HHSVM81GameRelease* release, uint32_t flags, uint8_t* rgba) {
    int y;
    for (y = 0; y < HHS_VM81_GAME_SPRITE_HEIGHT; ++y) {
        uint8_t r = hhs_sprite_lerp_u8(10U, 64U, (uint32_t)y, HHS_VM81_GAME_SPRITE_HEIGHT - 1U);
        uint8_t g = hhs_sprite_lerp_u8(18U, 104U, (uint32_t)y, HHS_VM81_GAME_SPRITE_HEIGHT - 1U);
        uint8_t b = hhs_sprite_lerp_u8(48U, 132U, (uint32_t)y, HHS_VM81_GAME_SPRITE_HEIGHT - 1U);
        int x;
        for (x = 0; x < HHS_VM81_GAME_SPRITE_WIDTH; ++x) {
            uint8_t rr = r;
            uint8_t gg = g;
            uint8_t bb = b;
            if ((flags & HHS_VM81_SPRITE_OVERLAY_ATMOSPHERE) != 0U) {
                uint32_t cloud = (uint32_t)((x + (int)(release->vm.camera_x_px / 3U) + y * 2) & 63);
                uint32_t star = (uint32_t)((x * 13 + y * 29 + (int)release->vm.phase * 7) % 173);
                if (y < 70 && cloud > 50U && cloud < 61U && ((y / 5) & 1) == 0) {
                    rr = hhs_sprite_blend_channel(rr, 126U, 30U);
                    gg = hhs_sprite_blend_channel(gg, 164U, 30U);
                    bb = hhs_sprite_blend_channel(bb, 190U, 30U);
                }
                if (y < 54 && star == 0U) {
                    rr = 214U;
                    gg = 230U;
                    bb = 242U;
                }
            }
            hhs_sprite_put(rgba, x, y, rr, gg, bb, 255U);
        }
    }
}

static void hhs_sprite_phase_overlay(const HHSVM81GameRelease* release, uint8_t* rgba) {
    uint8_t phase_r = (uint8_t)(56U + (uint32_t)release->vm.phase * 2U % 160U);
    uint8_t phase_g = (uint8_t)(90U + (uint32_t)release->vm.lo_shu_set * 3U % 120U);
    uint8_t phase_b = (uint8_t)(180U + (uint32_t)release->vm.phase % 72U);
    int y;
    for (y = 0; y < HHS_VM81_GAME_SPRITE_HEIGHT; ++y) {
        int x;
        for (x = 0; x < HHS_VM81_GAME_SPRITE_WIDTH; ++x) {
            uint32_t lane = (uint32_t)(x + y + (int)release->vm.phase * 3) % 72U;
            uint32_t distance = lane > 36U ? lane - 36U : 36U - lane;
            uint8_t alpha = distance < 10U ? (uint8_t)(18U - distance) : 0U;
            if (alpha != 0U) hhs_sprite_blend(rgba, x, y, phase_r, phase_g, phase_b, alpha);
        }
    }
}

static void hhs_sprite_draw_solid_tile(uint8_t* rgba, int screen_x, int screen_y, int tile_x, int tile_y) {
    int py;
    for (py = 0; py < HHS_VM81_GAME_TILE_SIZE; ++py) {
        int px;
        for (px = 0; px < HHS_VM81_GAME_TILE_SIZE; ++px) {
            uint8_t r;
            uint8_t g;
            uint8_t b;
            if (py < 2) {
                r = hhs_sprite_lerp_u8(44U, 82U, (uint32_t)px, 7U);
                g = hhs_sprite_lerp_u8(142U, 202U, (uint32_t)px, 7U);
                b = hhs_sprite_lerp_u8(98U, 136U, (uint32_t)px, 7U);
            } else {
                uint32_t depth = (uint32_t)(py - 2);
                r = hhs_sprite_lerp_u8(66U, 32U, depth, 5U);
                g = hhs_sprite_lerp_u8(78U, 48U, depth, 5U);
                b = hhs_sprite_lerp_u8(104U, 72U, depth, 5U);
                if (((px + py + tile_x + tile_y) & 3) == 0) {
                    r = (uint8_t)(r + 12U);
                    g = (uint8_t)(g + 12U);
                    b = (uint8_t)(b + 14U);
                }
            }
            hhs_sprite_put(rgba, screen_x + px, screen_y + py, r, g, b, 255U);
        }
    }
}

static void hhs_sprite_draw_hazard(uint8_t* rgba, int screen_x, int screen_y) {
    int py;
    for (py = 0; py < HHS_VM81_GAME_TILE_SIZE; ++py) {
        int px;
        for (px = 0; px < HHS_VM81_GAME_TILE_SIZE; ++px) {
            int center = px < 4 ? 2 : 6;
            int local = px < 4 ? px : px - 4;
            int threshold = 7 - (local <= 2 ? local * 3 : (4 - local) * 3);
            if (py >= threshold || (py >= 4 && (px == center || px == center - 1))) {
                uint8_t r = hhs_sprite_lerp_u8(255U, 168U, (uint32_t)py, 7U);
                uint8_t g = hhs_sprite_lerp_u8(226U, 42U, (uint32_t)py, 7U);
                uint8_t b = hhs_sprite_lerp_u8(92U, 38U, (uint32_t)py, 7U);
                hhs_sprite_put(rgba, screen_x + px, screen_y + py, r, g, b, 255U);
            }
        }
    }
}

static void hhs_sprite_draw_checkpoint(uint8_t* rgba, int screen_x, int screen_y, int active) {
    int py;
    for (py = 0; py < 16; ++py) {
        int px;
        for (px = 0; px < 8; ++px) {
            int draw = 0;
            uint8_t r = active ? 78U : 52U;
            uint8_t g = active ? 236U : 146U;
            uint8_t b = active ? 224U : 184U;
            if (px == 3 || px == 4) draw = 1;
            if (py < 7 && (px + py == 5 || px - py == 2 || py - px == 2 || px + py == 9)) draw = 1;
            if (draw) {
                uint8_t shade = hhs_sprite_lerp_u8(255U, 118U, (uint32_t)py, 15U);
                hhs_sprite_put(
                    rgba,
                    screen_x + px,
                    screen_y + py,
                    hhs_sprite_blend_channel(r, shade, 72U),
                    hhs_sprite_blend_channel(g, shade, 72U),
                    hhs_sprite_blend_channel(b, shade, 72U),
                    255U
                );
            }
        }
    }
}

static void hhs_sprite_draw_goal(uint8_t* rgba, int screen_x, int screen_y) {
    int py;
    for (py = 0; py < 20; ++py) {
        int px;
        for (px = 0; px < 12; ++px) {
            int draw = 0;
            uint8_t r = 248U;
            uint8_t g = 206U;
            uint8_t b = 72U;
            if (px == 2 || px == 3) draw = 1;
            if (py < 8 && px >= 3 && px <= 10 - py / 2) draw = 1;
            if (draw) {
                uint8_t shade = hhs_sprite_lerp_u8(255U, 128U, (uint32_t)py, 19U);
                hhs_sprite_put(
                    rgba,
                    screen_x + px,
                    screen_y + py,
                    hhs_sprite_blend_channel(r, shade, 48U),
                    hhs_sprite_blend_channel(g, shade, 48U),
                    hhs_sprite_blend_channel(b, shade, 48U),
                    255U
                );
            }
        }
    }
}

static void hhs_sprite_draw_world(const HHSVM81GameRelease* release, uint8_t* rgba) {
    int tile_y;
    uint32_t camera_tile = release->vm.camera_x_px / HHS_VM81_GAME_TILE_SIZE;
    int camera_offset = (int)(release->vm.camera_x_px % HHS_VM81_GAME_TILE_SIZE);
    for (tile_y = 0; tile_y < HHS_VM81_GAME_LEVEL_TILES_Y; ++tile_y) {
        int view_tile_x;
        for (view_tile_x = -1; view_tile_x <= HHS_VM81_GAME_VIEW_TILES_X; ++view_tile_x) {
            int tile_x = (int)camera_tile + view_tile_x;
            int screen_x = view_tile_x * HHS_VM81_GAME_TILE_SIZE - camera_offset;
            int screen_y = tile_y * HHS_VM81_GAME_TILE_SIZE;
            if (tile_x < 0 || tile_x >= HHS_VM81_GAME_LEVEL_TILES_X) continue;
            if (release->vm.level[tile_y][tile_x] != 0U) {
                hhs_sprite_draw_solid_tile(rgba, screen_x, screen_y, tile_x, tile_y);
            }
            if (hhs_sprite_tile_is_hazard(tile_x, tile_y)) {
                hhs_sprite_draw_hazard(rgba, screen_x, screen_y);
            }
            if (tile_y == 14 && tile_x == 20) {
                hhs_sprite_draw_checkpoint(rgba, screen_x, screen_y - 8, release->checkpoint >= 1U);
            }
            if (tile_y == 14 && tile_x == 40) {
                hhs_sprite_draw_checkpoint(rgba, screen_x, screen_y - 8, release->checkpoint >= 2U);
            }
            if (tile_y == 14 && tile_x == 61) {
                hhs_sprite_draw_goal(rgba, screen_x, screen_y - 12);
            }
        }
    }
}

static void hhs_sprite_radial_glow(
    uint8_t* rgba,
    int center_x,
    int center_y,
    int radius,
    uint8_t r,
    uint8_t g,
    uint8_t b,
    uint8_t maximum_alpha
) {
    int y;
    for (y = center_y - radius; y <= center_y + radius; ++y) {
        int x;
        for (x = center_x - radius; x <= center_x + radius; ++x) {
            int dx = x - center_x;
            int dy = y - center_y;
            int distance = dx < 0 ? -dx : dx;
            int abs_dy = dy < 0 ? -dy : dy;
            uint8_t alpha;
            distance += abs_dy;
            if (distance > radius) continue;
            alpha = (uint8_t)(((uint32_t)(radius - distance) * (uint32_t)maximum_alpha) / (uint32_t)radius);
            hhs_sprite_blend(rgba, x, y, r, g, b, alpha);
        }
    }
}

static void hhs_sprite_glows(const HHSVM81GameRelease* release, uint8_t* rgba) {
    int checkpoint_one_x = 20 * HHS_VM81_GAME_TILE_SIZE - (int)release->vm.camera_x_px + 4;
    int checkpoint_two_x = 40 * HHS_VM81_GAME_TILE_SIZE - (int)release->vm.camera_x_px + 4;
    int goal_x = 61 * HHS_VM81_GAME_TILE_SIZE - (int)release->vm.camera_x_px + 4;
    hhs_sprite_radial_glow(rgba, checkpoint_one_x, 112, 22, 48U, 236U, 222U, release->checkpoint >= 1U ? 68U : 34U);
    hhs_sprite_radial_glow(rgba, checkpoint_two_x, 112, 22, 48U, 236U, 222U, release->checkpoint >= 2U ? 68U : 34U);
    hhs_sprite_radial_glow(rgba, goal_x, 102, 28, 255U, 198U, 56U, 62U);
}

static void hhs_sprite_draw_player(const HHSVM81GameRelease* release, uint8_t* rgba) {
    int base_x = release->vm.player.x_subpx / HHS_VM81_GAME_SUBPIXELS - (int)release->vm.camera_x_px;
    int base_y = release->vm.player.y_subpx / HHS_VM81_GAME_SUBPIXELS;
    int walk = release->vm.player.animation_state == HHS_GAME_ANIM_WALK ? (int)(release->vm.player.animation_frame & 1U) : 0;
    int y;
    for (y = 0; y < HHS_VM81_GAME_PLAYER_HEIGHT; ++y) {
        int x;
        for (x = 0; x < HHS_VM81_GAME_PLAYER_WIDTH; ++x) {
            int draw = 0;
            uint8_t r = 62U;
            uint8_t g = 220U;
            uint8_t b = 246U;
            if (y >= 1 && y <= 5 && x >= 5 && x <= 10) draw = 1;
            if (y >= 5 && y <= 11 && x >= 3 && x <= 12) draw = 1;
            if (y >= 11 && y <= 15) {
                int left_leg = x >= 4 - walk && x <= 6 - walk;
                int right_leg = x >= 9 + walk && x <= 11 + walk;
                if (left_leg || right_leg) draw = 1;
            }
            if (draw) {
                if (y < 6) {
                    r = 246U;
                    g = 188U;
                    b = 128U;
                } else if ((x + y + (int)release->vm.phase) % 7 == 0) {
                    r = 176U;
                    g = 92U;
                    b = 238U;
                }
                if (release->vm.player.facing_right && y == 3 && x == 9) {
                    r = 18U; g = 24U; b = 42U;
                } else if (!release->vm.player.facing_right && y == 3 && x == 6) {
                    r = 18U; g = 24U; b = 42U;
                }
                hhs_sprite_put(rgba, base_x + x, base_y + y, r, g, b, 255U);
            }
        }
    }
    hhs_sprite_radial_glow(rgba, base_x + 8, base_y + 8, 14, 92U, 174U, 255U, 24U);
}

static void hhs_sprite_hud(const HHSVM81GameRelease* release, uint8_t* rgba) {
    int y;
    for (y = 0; y < 10; ++y) {
        int x;
        uint8_t alpha = hhs_sprite_lerp_u8(154U, 42U, (uint32_t)y, 9U);
        for (x = 0; x < HHS_VM81_GAME_SPRITE_WIDTH; ++x) hhs_sprite_blend(rgba, x, y, 6U, 10U, 26U, alpha);
    }
    {
        uint32_t life;
        for (life = 0U; life < release->lives; ++life) {
            int ox = 4 + (int)life * 8;
            hhs_sprite_put(rgba, ox + 2, 3, 255U, 94U, 124U, 255U);
            hhs_sprite_put(rgba, ox + 4, 3, 255U, 94U, 124U, 255U);
            hhs_sprite_put(rgba, ox + 1, 4, 255U, 94U, 124U, 255U);
            hhs_sprite_put(rgba, ox + 2, 5, 255U, 94U, 124U, 255U);
            hhs_sprite_put(rgba, ox + 3, 6, 255U, 94U, 124U, 255U);
            hhs_sprite_put(rgba, ox + 4, 5, 255U, 94U, 124U, 255U);
            hhs_sprite_put(rgba, ox + 5, 4, 255U, 94U, 124U, 255U);
        }
    }
    {
        int cp;
        for (cp = 0; cp < 2; ++cp) {
            uint8_t active = release->checkpoint > (uint32_t)cp ? 255U : 72U;
            int ox = 128 + cp * 12;
            int px;
            for (px = 0; px < 8; ++px) hhs_sprite_put(rgba, ox + px, 4, 66U, 236U, 218U, active);
        }
    }
    {
        int x;
        uint32_t progress = (uint32_t)(release->vm.player.x_subpx / HHS_VM81_GAME_SUBPIXELS);
        uint32_t filled = progress >= HHS_VM81_GAME_RELEASE_GOAL_X_PX ? 20U : progress * 20U / HHS_VM81_GAME_RELEASE_GOAL_X_PX;
        for (x = 0; x < 20; ++x) {
            uint8_t r = (uint32_t)x < filled ? 250U : 66U;
            uint8_t g = (uint32_t)x < filled ? 202U : 72U;
            uint8_t b = (uint32_t)x < filled ? 78U : 96U;
            hhs_sprite_put(rgba, 102 + x, 4, r, g, b, 255U);
        }
    }
}

static void hhs_sprite_vignette(uint8_t* rgba) {
    int y;
    for (y = 0; y < HHS_VM81_GAME_SPRITE_HEIGHT; ++y) {
        int x;
        for (x = 0; x < HHS_VM81_GAME_SPRITE_WIDTH; ++x) {
            int edge_x = x < HHS_VM81_GAME_SPRITE_WIDTH - 1 - x ? x : HHS_VM81_GAME_SPRITE_WIDTH - 1 - x;
            int edge_y = y < HHS_VM81_GAME_SPRITE_HEIGHT - 1 - y ? y : HHS_VM81_GAME_SPRITE_HEIGHT - 1 - y;
            int edge = edge_x < edge_y ? edge_x : edge_y;
            uint8_t alpha = edge < 18 ? (uint8_t)((18 - edge) * 3) : 0U;
            if (alpha != 0U) hhs_sprite_blend(rgba, x, y, 4U, 6U, 18U, alpha);
        }
    }
}

static uint32_t hhs_sprite_count_unique_buckets(const uint8_t* rgba) {
    uint8_t buckets[4096];
    uint32_t count = 0U;
    int y;
    memset(buckets, 0, sizeof(buckets));
    for (y = 0; y < HHS_VM81_GAME_SPRITE_HEIGHT; ++y) {
        int x;
        for (x = 0; x < HHS_VM81_GAME_SPRITE_WIDTH; ++x) {
            size_t index = HHS_SPRITE_PIXEL_INDEX(x, y);
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

HHSVM81GameStatus hhs_vm81_game_sprite_render_rgba(
    const HHSVM81GameRelease* release,
    uint32_t overlay_flags,
    uint8_t* out_rgba,
    size_t out_capacity,
    HHSVM81GameSpriteReport* report
) {
    HHSVM81GameRelease before;
    if (!release || !out_rgba || !report) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if ((overlay_flags & ~HHS_VM81_SPRITE_OVERLAY_ALL) != 0U) return HHS_GAME_STATUS_INVALID_OPERAND;
    if (out_capacity < HHS_VM81_GAME_SPRITE_RGBA_BYTES) return HHS_GAME_STATUS_OUTPUT_CAPACITY;
    before = *release;
    memset(report, 0, sizeof(*report));
    hhs_sprite_background(release, overlay_flags, out_rgba);
    if ((overlay_flags & HHS_VM81_SPRITE_OVERLAY_PHASE) != 0U) hhs_sprite_phase_overlay(release, out_rgba);
    hhs_sprite_draw_world(release, out_rgba);
    if ((overlay_flags & HHS_VM81_SPRITE_OVERLAY_GLOWS) != 0U) hhs_sprite_glows(release, out_rgba);
    hhs_sprite_draw_player(release, out_rgba);
    if ((overlay_flags & HHS_VM81_SPRITE_OVERLAY_HUD) != 0U) hhs_sprite_hud(release, out_rgba);
    if ((overlay_flags & HHS_VM81_SPRITE_OVERLAY_VIGNETTE) != 0U) hhs_sprite_vignette(out_rgba);
    report->width = HHS_VM81_GAME_SPRITE_WIDTH;
    report->height = HHS_VM81_GAME_SPRITE_HEIGHT;
    report->overlay_flags = overlay_flags;
    report->unique_color_buckets = hhs_sprite_count_unique_buckets(out_rgba);
    report->nontransparent_pixels = HHS_VM81_GAME_SPRITE_WIDTH * HHS_VM81_GAME_SPRITE_HEIGHT;
    report->state_unchanged = (uint32_t)(memcmp(release, &before, sizeof(before)) == 0);
    hhs_hash72_compute(out_rgba, HHS_VM81_GAME_SPRITE_RGBA_BYTES, &report->frame_hash72);
    hhs_hash216_compute(out_rgba, HHS_VM81_GAME_SPRITE_RGBA_BYTES, &report->frame_hash216);
    report->source_state_hash216 = release->vm.latest_state_identity_hash216;
    return report->state_unchanged != 0U ? HHS_GAME_STATUS_OK : HHS_GAME_STATUS_STATE_INVARIANT_FAILURE;
}

HHSVM81GameStatus hhs_vm81_game_sprite_write_ppm(
    const HHSVM81GameRelease* release,
    uint32_t overlay_flags,
    const char* path,
    HHSVM81GameSpriteReport* report
) {
    uint8_t rgba[HHS_VM81_GAME_SPRITE_RGBA_BYTES];
    HHSVM81GameStatus status;
    FILE* file;
    int y;
    if (!path) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    status = hhs_vm81_game_sprite_render_rgba(release, overlay_flags, rgba, sizeof(rgba), report);
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
            size_t index = HHS_SPRITE_PIXEL_INDEX(x, y);
            if (fwrite(rgba + index, 1U, 3U, file) != 3U) {
                (void)fclose(file);
                return HHS_GAME_STATUS_INVALID_ARGUMENT;
            }
        }
    }
    if (fclose(file) != 0) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    return HHS_GAME_STATUS_OK;
}
