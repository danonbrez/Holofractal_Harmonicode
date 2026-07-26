#define _POSIX_C_SOURCE 200809L

#include "hhs_vm81_game_sprite.h"

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

static int hhs_sprite_make_directory(const char* path) {
    if (!path || path[0] == '\0') return 0;
    if (mkdir(path, 0777) == 0 || errno == EEXIST) return 1;
    return 0;
}

static int hhs_sprite_write_text(const char* path, const char* text, size_t size) {
    FILE* file;
    if (!path || !text) return 0;
    file = fopen(path, "wb");
    if (!file) return 0;
    if (fwrite(text, 1U, size, file) != size) {
        (void)fclose(file);
        return 0;
    }
    return fclose(file) == 0;
}

static void hhs_sprite_chain_frame(
    HHSHash72* chain72,
    HHSHash216* chain216,
    const HHSVM81GameSpriteReport* report,
    uint32_t frame_index
) {
    uint8_t payload[HHS_HASH72_LEN * 2U + 8U];
    size_t offset = 0U;
    size_t i;
    memcpy(payload + offset, chain72->value, HHS_HASH72_LEN);
    offset += HHS_HASH72_LEN;
    memcpy(payload + offset, report->frame_hash72.value, HHS_HASH72_LEN);
    offset += HHS_HASH72_LEN;
    for (i = 0U; i < 4U; ++i) payload[offset++] = (uint8_t)((frame_index >> (8U * i)) & 0xffU);
    payload[offset++] = (uint8_t)(report->overlay_flags & 0xffU);
    payload[offset++] = (uint8_t)((report->overlay_flags >> 8U) & 0xffU);
    payload[offset++] = (uint8_t)(report->unique_color_buckets & 0xffU);
    payload[offset++] = (uint8_t)((report->unique_color_buckets >> 8U) & 0xffU);
    hhs_hash72_compute(payload, offset, chain72);
    hhs_hash216_compute(payload, offset, chain216);
}

static int hhs_sprite_capture_frame(
    const char* directory,
    uint32_t frame_index,
    const HHSVM81GameRelease* release,
    HHSHash72* chain72,
    HHSHash216* chain216,
    uint32_t* minimum_colors,
    uint32_t* maximum_colors
) {
    char path[512];
    int length;
    HHSVM81GameSpriteReport report;
    HHSVM81GameStatus status;
    length = snprintf(path, sizeof(path), "%s/frame_%06u.ppm", directory, frame_index);
    if (length < 0 || (size_t)length >= sizeof(path)) return 0;
    status = hhs_vm81_game_sprite_write_ppm(
        release,
        HHS_VM81_SPRITE_OVERLAY_ALL,
        path,
        &report
    );
    if (status != HHS_GAME_STATUS_OK || report.state_unchanged == 0U) return 0;
    if (report.unique_color_buckets < *minimum_colors) *minimum_colors = report.unique_color_buckets;
    if (report.unique_color_buckets > *maximum_colors) *maximum_colors = report.unique_color_buckets;
    hhs_sprite_chain_frame(chain72, chain216, &report, frame_index);
    return 1;
}

static int hhs_sprite_write_layer_comparison(const char* directory, const HHSVM81GameRelease* release) {
    static const uint32_t flags[] = {
        0U,
        HHS_VM81_SPRITE_OVERLAY_ATMOSPHERE,
        HHS_VM81_SPRITE_OVERLAY_ATMOSPHERE | HHS_VM81_SPRITE_OVERLAY_PHASE,
        HHS_VM81_SPRITE_OVERLAY_ATMOSPHERE | HHS_VM81_SPRITE_OVERLAY_PHASE | HHS_VM81_SPRITE_OVERLAY_GLOWS,
        HHS_VM81_SPRITE_OVERLAY_ALL
    };
    static const char* const names[] = {
        "00-base.ppm",
        "01-atmosphere.ppm",
        "02-phase.ppm",
        "03-glows.ppm",
        "04-full.ppm"
    };
    HHSVM81GameSpriteReport reports[5];
    char layer_directory[512];
    char path[512];
    char manifest_path[512];
    char manifest[8192];
    size_t i;
    int length;
    if (snprintf(layer_directory, sizeof(layer_directory), "%s/layers", directory) < 0) return 0;
    if (!hhs_sprite_make_directory(layer_directory)) return 0;
    for (i = 0U; i < 5U; ++i) {
        if (snprintf(path, sizeof(path), "%s/%s", layer_directory, names[i]) < 0) return 0;
        if (hhs_vm81_game_sprite_write_ppm(release, flags[i], path, &reports[i]) != HHS_GAME_STATUS_OK) return 0;
    }
    length = snprintf(
        manifest,
        sizeof(manifest),
        "{\n"
        "  \"classification\": \"VM81_SPRITE_OVERLAY_LAYER_COMPARISON_CAPTURED\",\n"
        "  \"source_frame\": %u,\n"
        "  \"source_state_hash216\": \"%s\",\n"
        "  \"layers\": [\n"
        "    {\"name\": \"BASE_SPRITE_MAP\", \"flags\": %u, \"hash72\": \"%s\", \"hash216\": \"%s\"},\n"
        "    {\"name\": \"ATMOSPHERE_GRADIENT\", \"flags\": %u, \"hash72\": \"%s\", \"hash216\": \"%s\"},\n"
        "    {\"name\": \"PHASE_OVERLAY\", \"flags\": %u, \"hash72\": \"%s\", \"hash216\": \"%s\"},\n"
        "    {\"name\": \"CHECKPOINT_GOAL_GLOWS\", \"flags\": %u, \"hash72\": \"%s\", \"hash216\": \"%s\"},\n"
        "    {\"name\": \"FULL_COMPOSITE\", \"flags\": %u, \"hash72\": \"%s\", \"hash216\": \"%s\"}\n"
        "  ]\n"
        "}\n",
        release->player_frames,
        release->vm.latest_state_identity_hash216.value,
        flags[0], reports[0].frame_hash72.value, reports[0].frame_hash216.value,
        flags[1], reports[1].frame_hash72.value, reports[1].frame_hash216.value,
        flags[2], reports[2].frame_hash72.value, reports[2].frame_hash216.value,
        flags[3], reports[3].frame_hash72.value, reports[3].frame_hash216.value,
        flags[4], reports[4].frame_hash72.value, reports[4].frame_hash216.value
    );
    if (length < 0 || (size_t)length >= sizeof(manifest)) return 0;
    if (snprintf(manifest_path, sizeof(manifest_path), "%s/layer-manifest.json", layer_directory) < 0) return 0;
    return hhs_sprite_write_text(manifest_path, manifest, (size_t)length);
}

int main(int argc, char** argv) {
    HHSVM81GameRelease release;
    HHSVM81GameReleaseReport replay;
    HHSVM81GameStatus status;
    HHSHash72 stream_hash72;
    HHSHash216 stream_hash216;
    const char* directory;
    char trace_path[512];
    char trace[8192];
    uint32_t frame_index = 0U;
    uint32_t checkpoint_one_frame = 0U;
    uint32_t checkpoint_two_frame = 0U;
    uint32_t victory_frame = 0U;
    uint32_t guard = 0U;
    uint32_t minimum_colors = UINT32_MAX;
    uint32_t maximum_colors = 0U;
    int layer_comparison_written = 0;
    int length;
    if (argc != 2) {
        fprintf(stderr, "Usage: %s OUTPUT_DIRECTORY\n", argv[0]);
        return 64;
    }
    directory = argv[1];
    if (!hhs_sprite_make_directory(directory)) return 1;
    status = hhs_vm81_game_release_init(&release);
    if (status != HHS_GAME_STATUS_OK) return 2;
    hhs_hash72_compute("HHS_VM81_SPRITE_FRAME_STREAM_V1", 31U, &stream_hash72);
    hhs_hash216_compute("HHS_VM81_SPRITE_FRAME_STREAM_V1", 31U, &stream_hash216);
    if (!hhs_sprite_capture_frame(
        directory,
        frame_index,
        &release,
        &stream_hash72,
        &stream_hash216,
        &minimum_colors,
        &maximum_colors
    )) return 3;
    status = hhs_vm81_game_release_start(&release);
    if (status != HHS_GAME_STATUS_OK) return 4;
    while (release.phase == HHS_GAME_RELEASE_RUNNING && guard < HHS_VM81_GAME_MAX_INPUT_FRAMES) {
        uint32_t previous_checkpoint = release.checkpoint;
        status = hhs_vm81_game_release_step(
            &release,
            (uint8_t)(HHS_VM81_GAME_INPUT_RIGHT | HHS_VM81_GAME_INPUT_JUMP)
        );
        if (status != HHS_GAME_STATUS_OK) return 5;
        frame_index++;
        if (!hhs_sprite_capture_frame(
            directory,
            frame_index,
            &release,
            &stream_hash72,
            &stream_hash216,
            &minimum_colors,
            &maximum_colors
        )) return 6;
        if (release.checkpoint > previous_checkpoint) {
            if (release.checkpoint == 1U) {
                checkpoint_one_frame = frame_index;
                if (!hhs_sprite_write_layer_comparison(directory, &release)) return 12;
                layer_comparison_written = 1;
            }
            if (release.checkpoint == 2U) checkpoint_two_frame = frame_index;
        }
        if (release.phase == HHS_GAME_RELEASE_VICTORY) victory_frame = frame_index;
        guard++;
    }
    if (release.phase != HHS_GAME_RELEASE_VICTORY || checkpoint_one_frame == 0U ||
        checkpoint_two_frame == 0U || victory_frame == 0U || !layer_comparison_written) return 7;
    status = hhs_vm81_game_release_replay_verify(&release, &replay);
    if (status != HHS_GAME_STATUS_OK) return 8;
    length = snprintf(
        trace,
        sizeof(trace),
        "{\n"
        "  \"contract\": \"HHS-VM81-SPRITE-MAP-OVERLAY-GRADIENTS-V1\",\n"
        "  \"capture_classification\": \"VM81_SPRITE_MAP_OVERLAY_GRADIENTS_CAPTURED\",\n"
        "  \"authoritative_state\": \"HHSVM81GameRelease\",\n"
        "  \"mutation_authority\": \"hhs_vm81_game_execute\",\n"
        "  \"projection_authority\": \"hhs_vm81_game_sprite_render_rgba\",\n"
        "  \"logical_resolution\": \"160x144\",\n"
        "  \"pixel_format\": \"RGBA8888\",\n"
        "  \"atlas_tile_size\": \"8x8\",\n"
        "  \"player_sprite_size\": \"16x16\",\n"
        "  \"overlay_flags\": %u,\n"
        "  \"overlay_layers\": [\"ATMOSPHERE\", \"PHASE\", \"CHECKPOINT_GOAL_GLOWS\", \"VIGNETTE\", \"HUD\"],\n"
        "  \"ticks_per_second\": %u,\n"
        "  \"frame_count\": %u,\n"
        "  \"title_frame\": 0,\n"
        "  \"checkpoint_one_frame\": %u,\n"
        "  \"checkpoint_two_frame\": %u,\n"
        "  \"victory_frame\": %u,\n"
        "  \"minimum_unique_color_buckets\": %u,\n"
        "  \"maximum_unique_color_buckets\": %u,\n"
        "  \"overlay_layer_comparison\": \"layers/layer-manifest.json\",\n"
        "  \"state_projection_non_mutating\": \"VERIFIED\",\n"
        "  \"phase\": \"%s\",\n"
        "  \"opcode_coverage\": \"%u/19\",\n"
        "  \"checkpoints_reached\": %u,\n"
        "  \"replay\": \"MATCH\",\n"
        "  \"frame_stream_hash72\": \"%s\",\n"
        "  \"frame_stream_hash216\": \"%s\",\n"
        "  \"final_hash72\": \"%s\",\n"
        "  \"final_hash216\": \"%s\"\n"
        "}\n",
        HHS_VM81_SPRITE_OVERLAY_ALL,
        HHS_VM81_GAME_TICKS_PER_SECOND,
        frame_index + 1U,
        checkpoint_one_frame,
        checkpoint_two_frame,
        victory_frame,
        minimum_colors,
        maximum_colors,
        hhs_vm81_game_release_phase_name(release.phase),
        release.vm.opcode_coverage == ((1U << 19U) - 1U) ? 19U : 0U,
        release.checkpoint,
        stream_hash72.value,
        stream_hash216.value,
        release.vm.latest_receipt_hash72.value,
        release.vm.latest_state_identity_hash216.value
    );
    if (length < 0 || (size_t)length >= sizeof(trace)) return 9;
    if (snprintf(trace_path, sizeof(trace_path), "%s/sprite-capture-trace.json", directory) < 0) return 10;
    if (!hhs_sprite_write_text(trace_path, trace, (size_t)length)) return 11;
    printf("{\n");
    printf("  \"capture_classification\": \"VM81_SPRITE_MAP_OVERLAY_GRADIENTS_CAPTURED\",\n");
    printf("  \"frame_count\": %u,\n", frame_index + 1U);
    printf("  \"capture_trace\": \"%s\"\n", trace_path);
    printf("}\n");
    return 0;
}
