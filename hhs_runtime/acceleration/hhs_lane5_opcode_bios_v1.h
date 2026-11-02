#ifndef HHS_LANE5_OPCODE_BIOS_V1_H
#define HHS_LANE5_OPCODE_BIOS_V1_H
/* Candidate-only acceleration ABI. Pass219+ C++ owns admission and lifetime.
 * Neither this ABI nor its buffers mint Hash72/Hash216 or commit VM81 state. */
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
#define HHS_BIOS_ABI_VERSION 1u
#define HHS_BIOS_HASH216_BYTES 216u
#define HHS_BIOS_FRAME_BYTES 648u
enum hhs_bios_status { HHS_BIOS_OK=0, HHS_BIOS_BAD_ARGUMENT=-1,
    HHS_BIOS_STALE=-2, HHS_BIOS_OVERFLOW=-3, HHS_BIOS_BAD_OPCODE=-4 };
enum hhs_bios_opcode { HHS_BIOS_COPY=1, HHS_BIOS_ADD_U64=2,
    HHS_BIOS_SUB_U64=3, HHS_BIOS_XOR_U64=4, HHS_BIOS_MOD72=5,
    HHS_BIOS_PHASE_PAIR=6 };
typedef struct {
    uint32_t opcode;
    uint8_t left_basis, right_basis;
    uint16_t reserved;
    uint64_t left, right;
} hhs_bios_instruction;
typedef struct {
    uint64_t value;
    uint8_t phase, orientation, closure, reserved[5];
} hhs_bios_result;
typedef struct {
    const uint8_t *hash216_snapshot; /* owner-held, immutable, 216 bytes */
    const uint8_t *frame_snapshot;   /* owner-held, immutable, 648 bytes */
    uint64_t generation;
} hhs_bios_view;
/* Bind and invalidate are called by authorized Pass219+ controller only.
 * The capability is a process-local pointer bound to a C++-owned view,
 * not an authorization token for VM81 mutation. */
typedef struct {
    hhs_bios_view view;
    uint64_t bound_generation;
    uint8_t bound;
} hhs_bios_cache;
int hhs_bios_bind(hhs_bios_cache *cache, const hhs_bios_view *owner_view);
int hhs_bios_read216(const hhs_bios_cache *cache, uint64_t generation,
                     uint16_t offset, uint8_t *value);
int hhs_bios_read_frame(const hhs_bios_cache *cache, uint64_t generation,
                        uint16_t offset, uint8_t *value);
void hhs_bios_invalidate(hhs_bios_cache *cache);
int hhs_bios_dispatch(const hhs_bios_cache *cache, uint64_t generation,
                      const hhs_bios_instruction *ops, size_t count,
                      hhs_bios_result *out);
#ifdef __cplusplus
}
#endif
#endif
