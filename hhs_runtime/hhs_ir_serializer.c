// hhs_runtime/hhs_ir_serializer.c
//
// HARMONICODE deterministic IR serializer
//
// Purpose:
//   Canonical binary serialization layer for:
//
//     HHS IR blocks
//     receipt transport
//     replay verification
//     parent-chain linkage
//     Hash72 sealing
//
// Properties:
//   - deterministic encoding
//   - endian-stable
//   - replay-safe
//   - receipt-chain compatible
//   - Hash72-integrated
//

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "HARMONICODE_VM_RUNTIME.h"

#define HHS_IR_MAGIC        0x48525331u
#define HHS_IR_VERSION      1

#define HHS_RECEIPT_MAGIC   0x48525231u

#define HHS_HASH72_LEN      72


// ============================================================
// HEADER
// ============================================================

typedef struct {

    uint32_t magic;
    uint32_t version;

    uint64_t node_count;

    uint32_t entry_phase;

    uint64_t parent_block;

} HHS_IR_Header;


// ============================================================
// RECEIPT PACKET
// ============================================================

typedef struct {

    uint32_t magic;

    uint64_t step;

    uint32_t witness;

    uint64_t orbit_period;

    uint8_t xyzw[4];

    uint8_t genomic[4];

    char prev_hash72[73];
    char state_hash72[73];
    char receipt_hash72[73];

} HHS_ReceiptPacket;


// ============================================================
// LITTLE-ENDIAN WRITERS
// ============================================================

static void hhs_write_u32(FILE *fp, uint32_t v) {

    uint8_t b[4];

    b[0] = (uint8_t)(v);
    b[1] = (uint8_t)(v >> 8);
    b[2] = (uint8_t)(v >> 16);
    b[3] = (uint8_t)(v >> 24);

    fwrite(b, 1, 4, fp);
}

static void hhs_write_u64(FILE *fp, uint64_t v) {

    uint8_t b[8];

    for (int i = 0; i < 8; i++)
        b[i] = (uint8_t)(v >> (8 * i));

    fwrite(b, 1, 8, fp);
}

static uint32_t hhs_read_u32(FILE *fp) {

    uint8_t b[4];

    fread(b, 1, 4, fp);

    return
        ((uint32_t)b[0])       |
        ((uint32_t)b[1] << 8)  |
        ((uint32_t)b[2] << 16) |
        ((uint32_t)b[3] << 24);
}

static uint64_t hhs_read_u64(FILE *fp) {

    uint8_t b[8];

    fread(b, 1, 8, fp);

    uint64_t v = 0;

    for (int i = 0; i < 8; i++)
        v |= ((uint64_t)b[i]) << (8 * i);

    return v;
}


// ============================================================
// NODE SERIALIZATION
// ============================================================

static void hhs_write_ir_node(
    FILE *fp,
    HHS_IR_Node *n
) {

    hhs_write_u32(fp, (uint32_t)n->op);

    hhs_write_u32(fp, n->dst);
    hhs_write_u32(fp, n->srcA);
    hhs_write_u32(fp, n->srcB);

    hhs_write_u64(fp, n->imm);
}

static int hhs_read_ir_node(
    FILE *fp,
    HHS_IR_Node *n
) {

    if (feof(fp))
        return 0;

    n->op   = (HHS_IROp)hhs_read_u32(fp);

    n->dst  = hhs_read_u32(fp);
    n->srcA = hhs_read_u32(fp);
    n->srcB = hhs_read_u32(fp);

    n->imm  = hhs_read_u64(fp);

    return 1;
}


// ============================================================
// BLOCK SERIALIZATION
// ============================================================

int hhs_ir_serialize_block(
    const char *path,
    HHS_IR_Block *blk
) {

    if (!blk)
        return 0;

    FILE *fp = fopen(path, "wb");

    if (!fp)
        return 0;

    HHS_IR_Header hdr;

    hdr.magic        = HHS_IR_MAGIC;
    hdr.version      = HHS_IR_VERSION;

    hdr.node_count   = blk->node_count;

    hdr.entry_phase  = blk->entry_phase;
    hdr.parent_block = blk->parent_block;

    hhs_write_u32(fp, hdr.magic);
    hhs_write_u32(fp, hdr.version);

    hhs_write_u64(fp, hdr.node_count);

    hhs_write_u32(fp, hdr.entry_phase);

    hhs_write_u64(fp, hdr.parent_block);

    for (uint32_t i = 0; i < blk->node_count; i++) {

        hhs_write_ir_node(
            fp,
            &blk->nodes[i]
        );
    }

    fclose(fp);

    return 1;
}


// ============================================================
// BLOCK DESERIALIZATION
// ============================================================

int hhs_ir_deserialize_block(
    const char *path,
    HHS_IR_Block *blk
) {

    if (!blk)
        return 0;

    FILE *fp = fopen(path, "rb");

    if (!fp)
        return 0;

    HHS_IR_Header hdr;

    hdr.magic   = hhs_read_u32(fp);
    hdr.version = hhs_read_u32(fp);

    if (hdr.magic != HHS_IR_MAGIC) {

        fclose(fp);
        return 0;
    }

    hdr.node_count = hhs_read_u64(fp);

    hdr.entry_phase = hhs_read_u32(fp);

    hdr.parent_block = hhs_read_u64(fp);

    blk->node_count  = (uint32_t)hdr.node_count;

    blk->entry_phase = hdr.entry_phase;
    blk->parent_block = hdr.parent_block;

    blk->nodes = calloc(
        blk->node_count,
        sizeof(HHS_IR_Node)
    );

    for (uint32_t i = 0; i < blk->node_count; i++) {

        hhs_read_ir_node(
            fp,
            &blk->nodes[i]
        );
    }

    fclose(fp);

    return 1;
}


// ============================================================
// RECEIPT SERIALIZATION
// ============================================================

int hhs_write_receipt_packet(
    const char *path,
    VM81 *vm
) {

    if (!vm)
        return 0;

    FILE *fp = fopen(path, "wb");

    if (!fp)
        return 0;

    HHS_ReceiptPacket pkt;

    memset(&pkt, 0, sizeof(pkt));

    pkt.magic = HHS_RECEIPT_MAGIC;

    pkt.step          = vm->last_receipt.step;
    pkt.witness       = vm->last_receipt.witness;
    pkt.orbit_period  = vm->last_receipt.orbit_period;

    memcpy(pkt.xyzw, vm->xyzw, 4);
    memcpy(pkt.genomic, vm->genomic, 4);

    strncpy(
        pkt.prev_hash72,
        vm->last_receipt.prev_h72,
        72
    );

    strncpy(
        pkt.state_hash72,
        vm->last_receipt.state_h72,
        72
    );

    strncpy(
        pkt.receipt_hash72,
        vm->last_receipt.receipt_h72,
        72
    );

    hhs_write_u32(fp, pkt.magic);

    hhs_write_u64(fp, pkt.step);

    hhs_write_u32(fp, pkt.witness);

    hhs_write_u64(fp, pkt.orbit_period);

    fwrite(pkt.xyzw,    1, 4, fp);
    fwrite(pkt.genomic, 1, 4, fp);

    fwrite(pkt.prev_hash72,    1, 73, fp);
    fwrite(pkt.state_hash72,   1, 73, fp);
    fwrite(pkt.receipt_hash72, 1, 73, fp);

    fclose(fp);

    return 1;
}


// ============================================================
// HASH72 SEAL
// ============================================================

int hhs_ir_hash72_seal(
    HHS_IR_Block *blk,
    char out[73]
) {

    if (!blk || !out)
        return 0;

    uint8_t accum[72];

    memset(accum, 0, sizeof(accum));

    for (uint32_t i = 0; i < blk->node_count; i++) {

        HHS_IR_Node *n = &blk->nodes[i];

        accum[i % 72] =
            wrap72(
                accum[i % 72]
                + n->op
                + n->dst
                + n->srcA
                + n->srcB
                + (uint32_t)n->imm
            );
    }

    for (int i = 0; i < 72; i++)
        out[i] = HASH72[accum[i] % 72];

    out[72] = 0;

    return 1;
}


// ============================================================
// RECEIPT CHAIN LINK
// ============================================================

int hhs_ir_chain_blocks(
    HHS_IR_Block *parent,
    HHS_IR_Block *child
) {

    if (!parent || !child)
        return 0;

    char seal[73];

    if (!hhs_ir_hash72_seal(parent, seal))
        return 0;

    uint64_t parent_hash = 0;

    for (int i = 0; i < 16; i++) {

        parent_hash <<= 4;

        parent_hash ^= hash72_index(seal[i]);
    }

    child->parent_block = parent_hash;

    return 1;
}


// ============================================================
// DEBUG
// ============================================================

void hhs_ir_debug_dump(
    HHS_IR_Block *blk
) {

    if (!blk)
        return;

    printf(
        "[HHS IR] nodes=%u entry=%u parent=%llu\n",
        blk->node_count,
        blk->entry_phase,
        (unsigned long long)blk->parent_block
    );

    for (uint32_t i = 0; i < blk->node_count; i++) {

        HHS_IR_Node *n = &blk->nodes[i];

        printf(
            "[%u] op=%u dst=%u A=%u B=%u imm=%llu\n",
            i,
            n->op,
            n->dst,
            n->srcA,
            n->srcB,
            (unsigned long long)n->imm
        );
    }
}