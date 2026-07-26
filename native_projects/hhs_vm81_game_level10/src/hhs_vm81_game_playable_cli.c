#define _POSIX_C_SOURCE 200809L

#include "hhs_vm81_game_release.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

typedef struct HHSTerminalState {
    struct termios original;
    int original_flags;
    int active;
} HHSTerminalState;

static int hhs_terminal_enter(HHSTerminalState* terminal) {
    struct termios raw;
    int flags;
    if (!terminal || !isatty(STDIN_FILENO) || !isatty(STDOUT_FILENO)) return 0;
    if (tcgetattr(STDIN_FILENO, &terminal->original) != 0) return 0;
    raw = terminal->original;
    raw.c_lflag &= (tcflag_t)~(ICANON | ECHO);
    raw.c_cc[VMIN] = 0;
    raw.c_cc[VTIME] = 0;
    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) != 0) return 0;
    flags = fcntl(STDIN_FILENO, F_GETFL, 0);
    if (flags < 0 || fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK) != 0) {
        (void)tcsetattr(STDIN_FILENO, TCSAFLUSH, &terminal->original);
        return 0;
    }
    terminal->original_flags = flags;
    terminal->active = 1;
    fputs("\033[?25l", stdout);
    fflush(stdout);
    return 1;
}

static void hhs_terminal_leave(HHSTerminalState* terminal) {
    if (!terminal || !terminal->active) return;
    (void)fcntl(STDIN_FILENO, F_SETFL, terminal->original_flags);
    (void)tcsetattr(STDIN_FILENO, TCSAFLUSH, &terminal->original);
    fputs("\033[?25h\033[0m\n", stdout);
    fflush(stdout);
    terminal->active = 0;
}

static int hhs_read_key(void) {
    unsigned char ch;
    ssize_t count = read(STDIN_FILENO, &ch, 1U);
    if (count == 1) return (int)ch;
    if (count < 0 && errno != EAGAIN && errno != EWOULDBLOCK) return -2;
    return -1;
}

static void hhs_sleep_tick(void) {
    struct timespec delay;
    delay.tv_sec = 0;
    delay.tv_nsec = 1000000000L / HHS_VM81_GAME_TICKS_PER_SECOND;
    while (nanosleep(&delay, &delay) != 0 && errno == EINTR) {
    }
}

static size_t hhs_render_terminal_frame(const HHSVM81GameRelease* release, char* out, size_t capacity) {
    const char* message = NULL;
    size_t used;
    int written;
    if (!release || !out || capacity == 0U) return 0U;
    used = hhs_vm81_game_release_render_ascii(release, out, capacity);
    if (used == 0U || used >= capacity) return 0U;
    if (release->phase == HHS_GAME_RELEASE_TITLE) {
        message = "Press ENTER to start. Reach G, avoid ^, and activate both C checkpoints.\n";
    } else if (release->phase == HHS_GAME_RELEASE_PAUSED) {
        message = "PAUSED - press P to resume.\n";
    } else if (release->phase == HHS_GAME_RELEASE_VICTORY) {
        message = "VICTORY - press ENTER to restart or Q to quit.\n";
    } else if (release->phase == HHS_GAME_RELEASE_GAME_OVER) {
        message = "GAME OVER - press ENTER to restart or Q to quit.\n";
    }
    if (!message) return used;
    written = snprintf(out + used, capacity - used, "%s", message);
    if (written < 0 || (size_t)written >= capacity - used) return 0U;
    return used + (size_t)written;
}

static int hhs_write_text_file(const char* path, const char* content, size_t length) {
    FILE* file;
    if (!path || !content) return 0;
    file = fopen(path, "wb");
    if (!file) return 0;
    if (fwrite(content, 1U, length, file) != length) {
        (void)fclose(file);
        return 0;
    }
    return fclose(file) == 0;
}

static int hhs_write_capture_frame(
    const char* directory,
    uint32_t frame_index,
    const HHSVM81GameRelease* release,
    char* screen,
    size_t capacity
) {
    char path[512];
    int path_length;
    size_t rendered;
    rendered = hhs_render_terminal_frame(release, screen, capacity);
    if (rendered == 0U) return 0;
    path_length = snprintf(path, sizeof(path), "%s/frame_%06u.txt", directory, frame_index);
    if (path_length < 0 || (size_t)path_length >= sizeof(path)) return 0;
    return hhs_write_text_file(path, screen, rendered);
}

static int hhs_capture_frames(const char* directory) {
    HHSVM81GameRelease release;
    HHSVM81GameReleaseReport replay;
    HHSVM81GameStatus status;
    char screen[HHS_VM81_GAME_RELEASE_MAX_RENDER_BYTES];
    char trace[4096];
    char trace_path[512];
    uint32_t frame_index = 0U;
    uint32_t checkpoint_one_frame = 0U;
    uint32_t checkpoint_two_frame = 0U;
    uint32_t victory_frame = 0U;
    uint32_t guard = 0U;
    int trace_length;
    int trace_path_length;
    if (!directory || directory[0] == '\0') return 64;
    if (mkdir(directory, 0777) != 0 && errno != EEXIST) {
        fprintf(stderr, "Unable to create capture directory: %s\n", directory);
        return 1;
    }
    status = hhs_vm81_game_release_init(&release);
    if (status != HHS_GAME_STATUS_OK) return 2;
    if (!hhs_write_capture_frame(directory, frame_index, &release, screen, sizeof(screen))) return 3;
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
        if (!hhs_write_capture_frame(directory, frame_index, &release, screen, sizeof(screen))) return 6;
        if (release.checkpoint > previous_checkpoint) {
            if (release.checkpoint == 1U) checkpoint_one_frame = frame_index;
            if (release.checkpoint == 2U) checkpoint_two_frame = frame_index;
        }
        if (release.phase == HHS_GAME_RELEASE_VICTORY) victory_frame = frame_index;
        guard++;
    }
    if (release.phase != HHS_GAME_RELEASE_VICTORY || checkpoint_one_frame == 0U ||
        checkpoint_two_frame == 0U || victory_frame == 0U) return 7;
    status = hhs_vm81_game_release_replay_verify(&release, &replay);
    if (status != HHS_GAME_STATUS_OK) return 8;
    trace_length = snprintf(
        trace,
        sizeof(trace),
        "{\n"
        "  \"contract\": \"HHS-VM81-USER-MODALITY-EVIDENCE-V1\",\n"
        "  \"capture_classification\": \"VM81_TERMINAL_FRAME_STREAM_CAPTURED\",\n"
        "  \"input_modality\": \"DETERMINISTIC_VM81_INPUT_TRACE\",\n"
        "  \"output_modality\": \"ANSI_TERMINAL_TEXT\",\n"
        "  \"ticks_per_second\": %u,\n"
        "  \"frame_count\": %u,\n"
        "  \"title_frame\": 0,\n"
        "  \"checkpoint_one_frame\": %u,\n"
        "  \"checkpoint_two_frame\": %u,\n"
        "  \"victory_frame\": %u,\n"
        "  \"phase\": \"%s\",\n"
        "  \"opcode_coverage\": \"%u/19\",\n"
        "  \"checkpoints_reached\": %u,\n"
        "  \"replay\": \"MATCH\",\n"
        "  \"final_hash72\": \"%s\",\n"
        "  \"final_hash216\": \"%s\"\n"
        "}\n",
        HHS_VM81_GAME_TICKS_PER_SECOND,
        frame_index + 1U,
        checkpoint_one_frame,
        checkpoint_two_frame,
        victory_frame,
        hhs_vm81_game_release_phase_name(release.phase),
        release.vm.opcode_coverage == ((1U << 19U) - 1U) ? 19U : 0U,
        release.checkpoint,
        release.vm.latest_receipt_hash72.value,
        release.vm.latest_state_identity_hash216.value
    );
    if (trace_length < 0 || (size_t)trace_length >= sizeof(trace)) return 9;
    trace_path_length = snprintf(trace_path, sizeof(trace_path), "%s/capture-trace.json", directory);
    if (trace_path_length < 0 || (size_t)trace_path_length >= sizeof(trace_path)) return 10;
    if (!hhs_write_text_file(trace_path, trace, (size_t)trace_length)) return 11;
    printf("{\n");
    printf("  \"capture_classification\": \"VM81_TERMINAL_FRAME_STREAM_CAPTURED\",\n");
    printf("  \"frame_count\": %u,\n", frame_index + 1U);
    printf("  \"capture_trace\": \"%s\"\n", trace_path);
    printf("}\n");
    return 0;
}

static int hhs_print_headless(void) {
    HHSVM81GameRelease release;
    HHSVM81GameReleaseReport report;
    HHSVM81GameReleaseReport replay;
    HHSVM81GameStatus status;
    status = hhs_vm81_game_release_init(&release);
    if (status != HHS_GAME_STATUS_OK) return 1;
    status = hhs_vm81_game_release_run_headless(&release, &report);
    if (status != HHS_GAME_STATUS_OK) return 2;
    status = hhs_vm81_game_release_replay_verify(&release, &replay);
    if (status != HHS_GAME_STATUS_OK) return 3;
    printf("{\n");
    printf("  \"contract\": \"HHS-VM81-PLAYABLE-GAME-RELEASE-V1\",\n");
    printf("  \"terminal_classification\": \"VM81_PLAYABLE_GAME_RELEASE_VERIFIED\",\n");
    printf("  \"status\": \"VERIFIED\",\n");
    printf("  \"phase\": \"%s\",\n", hhs_vm81_game_release_phase_name(report.phase));
    printf("  \"frames\": %u,\n", report.player_frames);
    printf("  \"instructions\": %u,\n", report.instructions_executed);
    printf("  \"opcode_coverage\": \"%u/19\",\n", report.opcode_coverage == ((1U << 19U) - 1U) ? 19U : 0U);
    printf("  \"lives_remaining\": %u,\n", report.lives);
    printf("  \"deaths\": %u,\n", report.deaths);
    printf("  \"checkpoints_reached\": %u,\n", report.checkpoint);
    printf("  \"replay\": \"MATCH\",\n");
    printf("  \"final_hash72\": \"%s\",\n", report.final_receipt_hash72.value);
    printf("  \"final_hash216\": \"%s\"\n", report.final_state_identity_hash216.value);
    printf("}\n");
    return 0;
}

static int hhs_run_interactive(void) {
    HHSVM81GameRelease release;
    HHSTerminalState terminal;
    char screen[HHS_VM81_GAME_RELEASE_MAX_RENDER_BYTES];
    uint8_t horizontal = 0U;
    uint32_t horizontal_ticks = 0U;
    int started = 0;
    HHSVM81GameStatus status;
    memset(&terminal, 0, sizeof(terminal));
    status = hhs_vm81_game_release_init(&release);
    if (status != HHS_GAME_STATUS_OK) return 1;
    if (!hhs_terminal_enter(&terminal)) {
        fputs("Interactive mode requires a POSIX terminal. Use --headless for verification.\n", stderr);
        return 2;
    }
    while (release.phase != HHS_GAME_RELEASE_QUIT) {
        uint8_t input = 0U;
        int key;
        size_t rendered;
        while ((key = hhs_read_key()) >= 0) {
            if (key == 'q' || key == 'Q') {
                (void)hhs_vm81_game_release_quit(&release);
            } else if (key == '\r' || key == '\n') {
                if (release.phase == HHS_GAME_RELEASE_TITLE) {
                    status = hhs_vm81_game_release_start(&release);
                    if (status != HHS_GAME_STATUS_OK) goto fail;
                    started = 1;
                } else if (release.phase == HHS_GAME_RELEASE_VICTORY || release.phase == HHS_GAME_RELEASE_GAME_OVER) {
                    status = hhs_vm81_game_release_restart(&release);
                    if (status != HHS_GAME_STATUS_OK) goto fail;
                    started = 1;
                }
            } else if (key == 'p' || key == 'P') {
                if (release.phase == HHS_GAME_RELEASE_RUNNING || release.phase == HHS_GAME_RELEASE_PAUSED) {
                    status = hhs_vm81_game_release_pause_toggle(&release);
                    if (status != HHS_GAME_STATUS_OK) goto fail;
                }
            } else if (key == 'r' || key == 'R') {
                status = hhs_vm81_game_release_restart(&release);
                if (status != HHS_GAME_STATUS_OK) goto fail;
                started = 1;
            } else if (key == 'a' || key == 'A') {
                horizontal = HHS_VM81_GAME_INPUT_LEFT;
                horizontal_ticks = 8U;
            } else if (key == 'd' || key == 'D') {
                horizontal = HHS_VM81_GAME_INPUT_RIGHT;
                horizontal_ticks = 8U;
            } else if (key == ' ' || key == 'w' || key == 'W') {
                input |= HHS_VM81_GAME_INPUT_JUMP;
            }
        }
        if (key == -2) goto fail;
        if (horizontal_ticks > 0U) {
            input |= horizontal;
            horizontal_ticks--;
        } else {
            horizontal = 0U;
        }
        if (release.phase == HHS_GAME_RELEASE_RUNNING && started) {
            status = hhs_vm81_game_release_step(&release, input);
            if (status != HHS_GAME_STATUS_OK) goto fail;
        }
        rendered = hhs_render_terminal_frame(&release, screen, sizeof(screen));
        if (rendered == 0U) goto fail;
        fputs("\033[H\033[2J", stdout);
        fwrite(screen, 1U, rendered, stdout);
        fflush(stdout);
        hhs_sleep_tick();
    }
    hhs_terminal_leave(&terminal);
    return 0;

fail:
    hhs_terminal_leave(&terminal);
    fprintf(stderr, "VM81 playable runtime failed with status %u.\n", (unsigned)status);
    return 3;
}

static void hhs_print_usage(const char* argv0) {
    printf("Usage: %s [--headless|--capture-frames DIRECTORY|--help]\n", argv0);
    puts("  no option                   launch the interactive terminal platformer");
    puts("  --headless                  execute the deterministic complete-level playthrough and replay check");
    puts("  --capture-frames DIRECTORY write the exact deterministic terminal presentation frame stream");
}

int main(int argc, char** argv) {
    if (argc == 3 && strcmp(argv[1], "--capture-frames") == 0) {
        return hhs_capture_frames(argv[2]);
    }
    if (argc == 2) {
        if (strcmp(argv[1], "--headless") == 0) return hhs_print_headless();
        if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) {
            hhs_print_usage(argv[0]);
            return 0;
        }
        hhs_print_usage(argv[0]);
        return 64;
    }
    if (argc > 3) {
        hhs_print_usage(argv[0]);
        return 64;
    }
    return hhs_run_interactive();
}
