/* Pass 220: exact ordered 4x4 source to typed VM81 frame, candidate only. */
#include "../include/hhs_pass220_ordered4x4_neg4_1_0.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <string.h>

static const char HHS220_ORDERED4X4_SOURCE[] = "NcalcMatrixPower((MatrixTimes(-List(List(1,1,1,1),List((-1),1,1,1),List((-1),(-1),1,1),List((-1),(-1),(-1),1)),-List(List((-1),(-1),(-1),(-1)),List(1,(-1),(-1),(-1)),List(1,1,(-1),(-1)),List(1,1,1,(-1))))/MatrixTimes(List(List(2,2,2,2),List(4,2,2,2),List(4,4,2,2),List(4,4,4,2)),s)),(-4))==MatrixTimes(v,List(List(0,0,0,0),List(1,0,0,0),List(1,1,0,0),List(1,1,1,0)))";
static const uint8_t HHS220_ORDERED4X4_SOURCE_SHA256[32] = {0xa3,0xba,0x5c,0xa5,0xf3,0x1e,0xe7,0x62,0x61,0xe5,0xdf,0x75,0xc7,0xe9,0xf4,0x3a,0x78,0x21,0x9d,0x59,0xdf,0x36,0xa0,0x95,0xa0,0x7c,0x0a,0xcd,0xf9,0x0d,0xbd,0x19};
static const int8_t HHS220_ORDERED4X4_CELLS[4][16] = {
    { 1,1,1,1, -1,1,1,1, -1,-1,1,1, -1,-1,-1,1 },
    { -1,-1,-1,-1, 1,-1,-1,-1, 1,1,-1,-1, 1,1,1,-1 },
    { 2,2,2,2, 4,2,2,2, 4,4,2,2, 4,4,4,2 },
    { 0,0,0,0, 1,0,0,0, 1,1,0,0, 1,1,1,0 }
};
_Static_assert(sizeof(HHS220_ORDERED4X4_SOURCE)-1U == HHS220_ORDERED4X4_SOURCE_BYTES, "Verbatim source drift");
_Static_assert(sizeof(HHS220_ORDERED4X4_CELLS) == HHS220_ORDERED4X4_CELL_COUNT, "Ordered topology drift");

static uint64_t hhs220_ordered4x4_word(const uint8_t *bytes) {
    uint64_t word = 0U;
    size_t i;
    for (i=0U;i<8U;++i) word |= ((uint64_t)bytes[i]) << (i*8U);
    return word;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_lower(
    const uint8_t *source,
    size_t source_size,
    HHSExactVM81Frame *out_candidate,
    HHS220Ordered4x4HIRWitnessV1 *out_witness
) {
    uint8_t source_digest[32];
    uint8_t topology_material[70];
    uint8_t topology_digest[32];
    size_t matrix_index, cell_index;
    if (source==NULL || out_candidate==NULL || out_witness==NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_candidate,0,sizeof(*out_candidate));
    memset(out_witness,0,sizeof(*out_witness));
    out_witness->struct_size=(uint32_t)sizeof(*out_witness);
    out_witness->version=UINT32_C(0x00010000);
    if (source_size!=HHS220_ORDERED4X4_SOURCE_BYTES ||
        memcmp(source,HHS220_ORDERED4X4_SOURCE,HHS220_ORDERED4X4_SOURCE_BYTES)!=0 ||
        SHA256(source,source_size,source_digest)==NULL ||
        memcmp(source_digest,HHS220_ORDERED4X4_SOURCE_SHA256,32U)!=0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for(matrix_index=0U;matrix_index<4U;++matrix_index)
        for(cell_index=0U;cell_index<16U;++cell_index)
            topology_material[matrix_index*16U+cell_index] =
                (uint8_t)HHS220_ORDERED4X4_CELLS[matrix_index][cell_index];
    topology_material[64]='s';
    topology_material[65]='v';
    topology_material[66]=2U;  /* two ordered negated numerator operands */
    topology_material[67]=4U;  /* negative fourth-power magnitude */
    topology_material[68]=1U;  /* quotient gate */
    topology_material[69]=1U;  /* ordered outer equality gate */
    if (SHA256(topology_material,sizeof(topology_material),topology_digest)==NULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_candidate->words[0]=UINT64_C(0x483232304e344d50); /* H220N4MP */
    out_candidate->words[1]=UINT64_C(0x00040004);         /* 4 x 4 */
    out_candidate->words[2]=UINT64_C(0x2d34);             /* literal -4 */
    out_candidate->words[3]=UINT64_C(2);                  /* negative operands */
    for(matrix_index=0U;matrix_index<4U;++matrix_index)
        for(cell_index=0U;cell_index<16U;++cell_index) {
            size_t index=matrix_index*16U+cell_index;
            out_candidate->words[4U+index] =
                ((uint64_t)matrix_index<<16U) |
                ((uint64_t)cell_index<<8U) |
                ((uint64_t)(uint8_t)HHS220_ORDERED4X4_CELLS[matrix_index][cell_index]);
        }
    for(cell_index=0U;cell_index<4U;++cell_index) {
        out_candidate->words[68U+cell_index]=hhs220_ordered4x4_word(source_digest+8U*cell_index);
        out_candidate->words[72U+cell_index]=hhs220_ordered4x4_word(topology_digest+8U*cell_index);
    }
    out_candidate->words[76]=3U;      /* three ordered MatrixTimes nodes */
    out_candidate->words[77]=1U;      /* typed quotient node */
    out_candidate->words[78]=1U;      /* exact symbolic negative fourth power */
    out_candidate->words[79]=1U;      /* ordered equality node */
    out_candidate->words[80]=UINT64_C(0x7673);  /* s, v unresolved */

    out_witness->rows=4U;
    out_witness->columns=4U;
    out_witness->matrix_occurrences=4U;
    out_witness->literal_cells=64U;
    out_witness->exponent_magnitude=4U;
    out_witness->exponent_negative=1U;
    out_witness->numerator_negative_operand_count=2U;
    out_witness->source_identity_verified=1U;
    out_witness->ordered_topology_verified=1U;
    out_witness->typed_s_unresolved=1U;
    out_witness->typed_v_unresolved=1U;
    memcpy(out_witness->source_sha256,source_digest,32U);
    memcpy(out_witness->topology_sha256,topology_digest,32U);
    /* All authority and value flags remain explicitly zero. */
    return HHS_EXACT_STATUS_OK;
}
