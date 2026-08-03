#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include "hhs_storybook_reel_projection_v2.h"

static int hhs_storybook_cli_argc = 0;
static char** hhs_storybook_cli_argv = NULL;

#define main hhs_storybook_reel_cli_base_main
#define hhs_storybook_style_default_v2 hhs_storybook_style_default_v2_cli
#include "hhs_storybook_reel_cli.c"
#undef hhs_storybook_style_default_v2
#undef main

HHSStorybookReelStatus hhs_storybook_style_default_v2(HHSStorybookReelStyleV2* style);

static unsigned long hhs_storybook_cli_unsigned(const char* name, unsigned long fallback) {
    int index;
    for (index = 1; index + 1 < hhs_storybook_cli_argc; ++index) {
        if (strcmp(hhs_storybook_cli_argv[index], name) == 0) {
            char* end = NULL;
            unsigned long value;
            errno = 0;
            value = strtoul(hhs_storybook_cli_argv[index + 1], &end, 10);
            if (errno == 0 && end && *end == '\0') return value;
            return fallback;
        }
    }
    return fallback;
}

HHSStorybookReelStatus hhs_storybook_style_default_v2_cli(HHSStorybookReelStyleV2* style) {
    HHSStorybookReelStatus status = hhs_storybook_style_default_v2(style);
    if (status != HHS_STORYBOOK_REEL_OK || !style) return status;
    style->manual_x.r = (uint8_t)hhs_storybook_cli_unsigned("--manual-x-r", style->manual_x.r);
    style->manual_x.g = (uint8_t)hhs_storybook_cli_unsigned("--manual-x-g", style->manual_x.g);
    style->manual_x.b = (uint8_t)hhs_storybook_cli_unsigned("--manual-x-b", style->manual_x.b);
    style->manual_y.r = (uint8_t)hhs_storybook_cli_unsigned("--manual-y-r", style->manual_y.r);
    style->manual_y.g = (uint8_t)hhs_storybook_cli_unsigned("--manual-y-g", style->manual_y.g);
    style->manual_y.b = (uint8_t)hhs_storybook_cli_unsigned("--manual-y-b", style->manual_y.b);
    style->manual_z.r = (uint8_t)hhs_storybook_cli_unsigned("--manual-z-r", style->manual_z.r);
    style->manual_z.g = (uint8_t)hhs_storybook_cli_unsigned("--manual-z-g", style->manual_z.g);
    style->manual_z.b = (uint8_t)hhs_storybook_cli_unsigned("--manual-z-b", style->manual_z.b);
    style->manual_w.r = (uint8_t)hhs_storybook_cli_unsigned("--manual-w-r", style->manual_w.r);
    style->manual_w.g = (uint8_t)hhs_storybook_cli_unsigned("--manual-w-g", style->manual_w.g);
    style->manual_w.b = (uint8_t)hhs_storybook_cli_unsigned("--manual-w-b", style->manual_w.b);
    return status;
}

int main(int argc, char** argv) {
    HHSStorybookProjectionConfigV2 projection;
    HHSStorybookReelStatus projection_status;
    hhs_storybook_cli_argc = argc;
    hhs_storybook_cli_argv = argv;
    projection_status = hhs_storybook_projection_default_v2(&projection);
    if (projection_status != HHS_STORYBOOK_REEL_OK) return 3;
    projection.texture_flags = (uint32_t)hhs_storybook_cli_unsigned(
        "--texture-flags",
        projection.texture_flags
    );
    projection.sprite_overlay_flags = (uint32_t)hhs_storybook_cli_unsigned(
        "--sprite-overlay-flags",
        projection.sprite_overlay_flags
    );
    projection_status = hhs_storybook_projection_set_v2(&projection);
    if (projection_status != HHS_STORYBOOK_REEL_OK) return 2;
    return hhs_storybook_reel_cli_base_main(argc, argv);
}
