#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "HARMONICODE_VM_RUNTIME.h"

#define HHS_IR_MAX_LINE 512
#define HHS_IR_MAX_NODES 4096

static HHS_IROp hhs_parse_opcode(const char *s) {
    if (!strcmp(s, "CONST")) return IR_CONST;
    if (!strcmp(s, "MOVE")) return IR_MOVE;
    if (!strcmp(s, "ADD")) return IR_ADD;
    if (!strcmp(s, "SUB")) return IR_SUB;
    if (!strcmp(s, "MUL")) return IR_MUL;
    if (!strcmp(s, "DIV")) return IR_DIV;
    if (!strcmp(s, "MOD")) return IR_MOD;
    if (!strcmp(s, "QGU")) return IR_QGU;
    if (!strcmp(s, "CONSTRAIN")) return IR_CONSTRAIN;
    if (!strcmp(s, "HASH72")) return IR_HASH72_PROJECT;
    return IR_NOP;
}

int hhs_parse_ir_file(const char *path, HHS_IR_Block *blk) {

    FILE *fp = fopen(path, "r");

    if (!fp)
        return 0;

    HHS_IR_Node *nodes = calloc(HHS_IR_MAX_NODES, sizeof(HHS_IR_Node));

    uint32_t count = 0;

    char line[HHS_IR_MAX_LINE];

    while (fgets(line, sizeof(line), fp)) {

        char op[64] = {0};

        HHS_IR_Node n;
        memset(&n, 0, sizeof(n));

        sscanf(
            line,
            "%63s %u %u %u %llu",
            op,
            &n.dst,
            &n.srcA,
            &n.srcB,
            &n.imm
        );

        n.op = hhs_parse_opcode(op);

        nodes[count++] = n;
    }

    fclose(fp);

    blk->nodes = nodes;
    blk->node_count = count;
    blk->entry_phase = 0;
    blk->parent_block = 0;

    return 1;
}
