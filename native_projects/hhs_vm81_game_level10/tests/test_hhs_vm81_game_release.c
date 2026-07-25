#include "hhs_vm81_game_release.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void test_release_lifecycle(void) {
    HHSVM81GameRelease release;
    uint64_t step_before;
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    assert(release.phase == HHS_GAME_RELEASE_TITLE);
    assert(release.lives == HHS_VM81_GAME_RELEASE_INITIAL_LIVES);
    assert(hhs_vm81_game_release_start(&release) == HHS_GAME_STATUS_OK);
    assert(release.phase == HHS_GAME_RELEASE_RUNNING);
    assert(hhs_vm81_game_release_step(&release, HHS_VM81_GAME_INPUT_RIGHT) == HHS_GAME_STATUS_OK);
    assert(release.player_frames == 1U);
    assert(release.vm.frame == 1U);
    assert(release.vm.receipt_count > 0U);
    step_before = release.vm.step;
    assert(hhs_vm81_game_release_pause_toggle(&release) == HHS_GAME_STATUS_OK);
    assert(release.phase == HHS_GAME_RELEASE_PAUSED);
    assert(hhs_vm81_game_release_step(&release, 0U) == HHS_GAME_STATUS_INVALID_OPERAND);
    assert(release.vm.step == step_before);
    assert(hhs_vm81_game_release_pause_toggle(&release) == HHS_GAME_STATUS_OK);
    assert(release.phase == HHS_GAME_RELEASE_RUNNING);
    assert(hhs_vm81_game_release_restart(&release) == HHS_GAME_STATUS_OK);
    assert(release.phase == HHS_GAME_RELEASE_RUNNING);
    assert(release.player_frames == 0U);
    assert(release.lives == HHS_VM81_GAME_RELEASE_INITIAL_LIVES);
}

static void test_hazard_and_game_over(void) {
    HHSVM81GameRelease release;
    uint32_t guard = 0U;
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_release_start(&release) == HHS_GAME_STATUS_OK);
    while (release.phase == HHS_GAME_RELEASE_RUNNING && release.deaths == 0U && guard < 160U) {
        assert(hhs_vm81_game_release_step(&release, HHS_VM81_GAME_INPUT_RIGHT) == HHS_GAME_STATUS_OK);
        guard++;
    }
    assert(release.deaths >= 1U);
    assert(release.lives < HHS_VM81_GAME_RELEASE_INITIAL_LIVES);
}

static void test_complete_playthrough_and_replay(void) {
    HHSVM81GameRelease release;
    HHSVM81GameReleaseReport report;
    HHSVM81GameReleaseReport replay;
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    assert(hhs_vm81_game_release_run_headless(&release, &report) == HHS_GAME_STATUS_OK);
    assert(release.phase == HHS_GAME_RELEASE_VICTORY);
    assert(report.phase == HHS_GAME_RELEASE_VICTORY);
    assert(report.checkpoint == HHS_VM81_GAME_RELEASE_CHECKPOINTS);
    assert(report.opcode_coverage == ((1U << 19U) - 1U));
    assert(report.receipts_emitted > 0U);
    assert(report.final_player.x_subpx / HHS_VM81_GAME_SUBPIXELS >= (int32_t)HHS_VM81_GAME_RELEASE_GOAL_X_PX);
    assert(hhs_vm81_game_release_replay_verify(&release, &replay) == HHS_GAME_STATUS_OK);
    assert(replay.phase == report.phase);
    assert(replay.player_frames == report.player_frames);
    assert(hhs_hash72_equal(&replay.final_receipt_hash72, &report.final_receipt_hash72));
    assert(hhs_hash216_equal(&replay.final_state_identity_hash216, &report.final_state_identity_hash216));
}

static void test_ascii_renderer(void) {
    HHSVM81GameRelease release;
    char rendered[HHS_VM81_GAME_RELEASE_MAX_RENDER_BYTES];
    size_t count;
    assert(hhs_vm81_game_release_init(&release) == HHS_GAME_STATUS_OK);
    count = hhs_vm81_game_release_render_ascii(&release, rendered, sizeof(rendered));
    assert(count > 0U);
    assert(strstr(rendered, "HHS VM81 PLATFORMER") != NULL);
    assert(strchr(rendered, '@') != NULL);
    assert(strchr(rendered, '^') != NULL);
}

int main(void) {
    test_release_lifecycle();
    test_hazard_and_game_over();
    test_complete_playthrough_and_replay();
    test_ascii_renderer();
    puts("VM81_PLAYABLE_GAME_RELEASE_VERIFIED");
    return 0;
}
