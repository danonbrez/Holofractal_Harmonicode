#define _POSIX_C_SOURCE 200809L

#include "hhs_vm81_game_release.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
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
        rendered = hhs_vm81_game_release_render_ascii(&release, screen, sizeof(screen));
        if (rendered == 0U) goto fail;
        fputs("\033[H\033[2J", stdout);
        fwrite(screen, 1U, rendered, stdout);
        if (release.phase == HHS_GAME_RELEASE_TITLE) {
            fputs("Press ENTER to start. Reach G, avoid ^, and activate both C checkpoints.\n", stdout);
        } else if (release.phase == HHS_GAME_RELEASE_PAUSED) {
            fputs("PAUSED — press P to resume.\n", stdout);
        } else if (release.phase == HHS_GAME_RELEASE_VICTORY) {
            fputs("VICTORY — press ENTER to restart or Q to quit.\n", stdout);
        } else if (release.phase == HHS_GAME_RELEASE_GAME_OVER) {
            fputs("GAME OVER — press ENTER to restart or Q to quit.\n", stdout);
        }
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
    printf("Usage: %s [--headless|--help]\n", argv0);
    puts("  no option    launch the interactive terminal platformer");
    puts("  --headless   execute the deterministic complete-level playthrough and replay check");
}

int main(int argc, char** argv) {
    if (argc > 2) {
        hhs_print_usage(argv[0]);
        return 64;
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
    return hhs_run_interactive();
}
