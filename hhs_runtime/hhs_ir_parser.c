#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>

#include "HARMONICODE_VM_RUNTIME.h"

#define HHS_IR_MAX_LINE   512
#define HHS_IR_MAX_NODES  4096

static HHS_IROp hhs_parse_opcode(const char *s)
{
    if (!strcmp(s, "CONST"))      return IR_CONST;
    if (!strcmp(s, "MOVE"))       return IR_MOVE;
    if (!strcmp(s, "ADD"))        return IR_ADD;
    if (!strcmp(s, "SUB"))        return IR_SUB;
    if (!strcmp(s, "MUL"))        return IR_MUL;
    if (!strcmp(s, "DIV"))        return IR_DIV;
    if (!strcmp(s, "MOD"))        return IR_MOD;
    if (!strcmp(s, "QGU"))        return IR_QGU;
    if (!strcmp(s, "CONSTRAIN"))  return IR_CONSTRAIN;
    if (!strcmp(s, "HASH72"))     return IR_HASH72_PROJECT;

    return IR_NOP;
}

static int hhs_line_is_empty(const char *s)
{
    while (*s) {
        if (!isspace((unsigned char)*s))
            return 0;
        ++s;
    }
    return 1;
}

int hhs_parse_ir_file(const char *path, HHS_IR_Block *blk)
{
    if (!path || !blk)
        return 0;

    FILE *fp = fopen(path, "r");

    if (!fp)
        return 0;

    HHS_IR_Node *nodes =
        (HHS_IR_Node *)calloc(HHS_IR_MAX_NODES, sizeof(HHS_IR_Node));

    if (!nodes) {
        fclose(fp);
        return 0;
    }

    uint32_t count = 0;

    char line[HHS_IR_MAX_LINE];

    while (fgets(line, sizeof(line), fp)) {

        if (line[0] == '#')
            continue;

        if (line[0] == ';')
            continue;

        if (hhs_line_is_empty(line))
            continue;

        if (count >= HHS_IR_MAX_NODES) {
            free(nodes);
            fclose(fp);
            return 0;
        }

        char op[64] = {0};

        HHS_IR_Node n;
        memset(&n, 0, sizeof(n));

        int parsed =
            sscanf(
                line,
                "%63s %u %u %u %llu",
                op,
                &n.dst,
                &n.srcA,
                &n.srcB,
                &n.imm
            );

        if (parsed < 1)
            continue;

        n.op = hhs_parse_opcode(op);

        nodes[count++] = n;
    }

    fclose(fp);

    blk->nodes        = nodes;
    blk->node_count   = count;
    blk->entry_phase  = 0;
    blk->parent_block = 0;

    return 1;
}

void hhs_free_ir_block(HHS_IR_Block *blk)
{
    if (!blk)
        return;

    if (blk->nodes) {
        free(blk->nodes);
        blk->nodes = NULL;
    }

    blk->node_count = 0;
}
