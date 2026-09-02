#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

int main(void) {
    uint8_t source[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t replay[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t copied[HHS_EXACT_VM81_FRAME_BYTES];
    char bits[HHS_EXACT_VM81_FRAME_BITS];
    HHSExactVM81Frame frame;
    HHSExactVM81Frame bit_frame;
    HHSExactPass219GlobalRaw5184DescriptorV1 descriptor;
    size_t length = 0U;
    uint32_t i;

    assert(hhs_exact_pass219_global_raw5184_descriptor(&descriptor) ==
           HHS_EXACT_STATUS_OK);
    assert(descriptor.raw_bits == 5184U);
    assert(descriptor.raw_bytes == 648U);
    assert(descriptor.vm81_cells == 81U);
    assert(descriptor.pcm64_samples == 81U);
    assert(descriptor.mandatory_public_frame_ingress == 1U);
    assert(descriptor.mandatory_public_frame_egress == 1U);
    assert(descriptor.mandatory_raw_bitstring == 1U);
    assert(descriptor.mandatory_648_byte_bytecode_copy == 1U);
    assert(descriptor.exact_bit_identity == 1U);
    assert(descriptor.dual_stereo_hydration_required == 1U);
    assert(descriptor.ternary_pcm64_required == 1U);
    assert(descriptor.center_u0_closure_required == 1U);
    assert(descriptor.scalar_projection_runtime_authority == 0U);
    assert(descriptor.floating_point_authority == 0U);
    assert(descriptor.vm81_mutation_authority == 0U);
    assert(descriptor.hash72_commit_authority == 0U);
    assert(descriptor.hash216_commit_authority == 0U);

    for (i = 0U; i < HHS_EXACT_VM81_FRAME_BYTES; ++i)
        source[i] = (uint8_t)((i * 37U + 11U) & 0xFFU);

    assert(hhs_exact_vm81_frame_import_le(source, sizeof(source), &frame) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_global_raw5184_validate_frame(&frame) ==
           HHS_EXACT_STATUS_OK);

    assert(hhs_exact_vm81_frame_export_le(
               &frame, replay, sizeof(replay), &length) ==
           HHS_EXACT_STATUS_OK);
    assert(length == sizeof(source));
    assert(memcmp(source, replay, sizeof(source)) == 0);

    assert(hhs_exact_pass219_global_raw5184_bitstring_export(
               &frame, bits, sizeof(bits), &length) ==
           HHS_EXACT_STATUS_OK);
    assert(length == HHS_EXACT_VM81_FRAME_BITS);
    assert(hhs_exact_pass219_global_raw5184_bitstring_import(
               bits, sizeof(bits), &bit_frame) ==
           HHS_EXACT_STATUS_OK);
    assert(memcmp(&frame, &bit_frame, sizeof(frame)) == 0);

    assert(hhs_exact_pass219_global_raw5184_bytecode_copy(
               source, sizeof(source), copied, sizeof(copied), &length) ==
           HHS_EXACT_STATUS_OK);
    assert(length == sizeof(source));
    assert(memcmp(source, copied, sizeof(source)) == 0);

    memset(copied, 0, sizeof(copied));
    assert(hhs_x86_64_bytecode_copy_exact(
               source, sizeof(source), copied, sizeof(copied), &length) ==
           HHS_EXACT_STATUS_OK);
    assert(length == sizeof(source));
    assert(memcmp(source, copied, sizeof(source)) == 0);

    bits[77] = '2';
    memset(&bit_frame, 0xA5, sizeof(bit_frame));
    assert(hhs_exact_pass219_global_raw5184_bitstring_import(
               bits, sizeof(bits), &bit_frame) ==
           HHS_EXACT_STATUS_RANGE_ERROR);
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        assert(bit_frame.words[i] == UINT64_C(0));

    return 0;
}
