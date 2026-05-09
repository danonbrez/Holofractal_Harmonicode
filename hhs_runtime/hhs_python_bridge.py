# hhs_runtime/hhs_python_bridge.py
#
# HARMONICODE Python → HHS IR bridge
#
# Purpose:
#   Deterministically lower Python AST into HHS IR blocks
#   executable by the VM81 runtime.
#
# Flow:
#
#   Python source
#       →
#   Python AST
#       →
#   HHS IR nodes
#       →
#   serialized .hir block
#       →
#   VM81 runtime
#
# Properties:
#   - deterministic lowering
#   - ordered noncommutative preservation
#   - Hash72-compatible execution traces
#   - symbolic execution replay
#   - backend/runtime unification
#

import ast
import json
from dataclasses import dataclass, asdict
from typing import List, Dict


# ============================================================
# IR OPCODES
# ============================================================

IR_NOP              = 0
IR_CONST            = 1
IR_MOVE             = 2
IR_ADD              = 3
IR_SUB              = 4
IR_MUL              = 5
IR_DIV              = 6
IR_MOD              = 7
IR_QGU              = 8
IR_CONSTRAIN        = 9
IR_HASH72_PROJECT   = 10


# ============================================================
# IR NODE
# ============================================================

@dataclass
class HHSIRNode:

    op: int

    dst: int
    srcA: int
    srcB: int

    imm: int


# ============================================================
# IR BLOCK
# ============================================================

@dataclass
class HHSIRBlock:

    nodes: List[HHSIRNode]

    entry_phase: int = 0
    parent_block: int = 0


# ============================================================
# REGISTER ALLOCATOR
# ============================================================

class HHSRegisterAllocator:

    def __init__(self):

        self.next_reg = 0
        self.symbols: Dict[str, int] = {}

    def alloc(self) -> int:

        r = self.next_reg
        self.next_reg += 1

        return r

    def get_symbol(self, name: str) -> int:

        if name not in self.symbols:
            self.symbols[name] = self.alloc()

        return self.symbols[name]


# ============================================================
# PYTHON → IR LOWERING
# ============================================================

class HHSPythonBridge(ast.NodeVisitor):

    def __init__(self):

        self.regs = HHSRegisterAllocator()

        self.nodes: List[HHSIRNode] = []

    # --------------------------------------------------------
    # helpers
    # --------------------------------------------------------

    def emit(
        self,
        op,
        dst=0,
        srcA=0,
        srcB=0,
        imm=0
    ):

        self.nodes.append(
            HHSIRNode(
                op=op,
                dst=dst,
                srcA=srcA,
                srcB=srcB,
                imm=imm
            )
        )

    # --------------------------------------------------------
    # constants
    # --------------------------------------------------------

    def lower_constant(self, value):

        r = self.regs.alloc()

        self.emit(
            IR_CONST,
            dst=r,
            imm=int(value)
        )

        return r

    # --------------------------------------------------------
    # names
    # --------------------------------------------------------

    def visit_Name(self, node):

        return self.regs.get_symbol(node.id)

    # --------------------------------------------------------
    # constants
    # --------------------------------------------------------

    def visit_Constant(self, node):

        return self.lower_constant(node.value)

    # --------------------------------------------------------
    # assignment
    # --------------------------------------------------------

    def visit_Assign(self, node):

        value_reg = self.visit(node.value)

        for target in node.targets:

            if isinstance(target, ast.Name):

                dst = self.regs.get_symbol(target.id)

                self.emit(
                    IR_MOVE,
                    dst=dst,
                    srcA=value_reg
                )

    # --------------------------------------------------------
    # binary operations
    # --------------------------------------------------------

    def visit_BinOp(self, node):

        left = self.visit(node.left)
        right = self.visit(node.right)

        dst = self.regs.alloc()

        if isinstance(node.op, ast.Add):

            self.emit(
                IR_ADD,
                dst=dst,
                srcA=left,
                srcB=right
            )

        elif isinstance(node.op, ast.Sub):

            self.emit(
                IR_SUB,
                dst=dst,
                srcA=left,
                srcB=right
            )

        elif isinstance(node.op, ast.Mult):

            self.emit(
                IR_MUL,
                dst=dst,
                srcA=left,
                srcB=right
            )

        elif isinstance(node.op, ast.Div):

            self.emit(
                IR_DIV,
                dst=dst,
                srcA=left,
                srcB=right
            )

        elif isinstance(node.op, ast.Mod):

            self.emit(
                IR_MOD,
                dst=dst,
                srcA=left,
                srcB=right
            )

        return dst

    # --------------------------------------------------------
    # function calls
    # --------------------------------------------------------

    def visit_Call(self, node):

        if isinstance(node.func, ast.Name):

            fn = node.func.id

            # --------------------------------------------
            # qgu(a,b,c)
            # --------------------------------------------

            if fn == "qgu":

                a = self.visit(node.args[0])
                b = self.visit(node.args[1])

                dst = self.regs.alloc()

                self.emit(
                    IR_QGU,
                    dst=dst,
                    srcA=a,
                    srcB=b
                )

                return dst

            # --------------------------------------------
            # constrain(a,strength)
            # --------------------------------------------

            elif fn == "constrain":

                phase = self.visit(node.args[0])

                strength_node = node.args[1]

                strength = 0

                if isinstance(strength_node, ast.Constant):
                    strength = int(strength_node.value)

                self.emit(
                    IR_CONSTRAIN,
                    dst=0,
                    srcA=phase,
                    imm=strength
                )

                return 0

            # --------------------------------------------
            # hash72()
            # --------------------------------------------

            elif fn == "hash72":

                self.emit(IR_HASH72_PROJECT)

                return 0

        return 0

    # --------------------------------------------------------
    # module
    # --------------------------------------------------------

    def visit_Module(self, node):

        for stmt in node.body:
            self.visit(stmt)

    # --------------------------------------------------------
    # finalize
    # --------------------------------------------------------

    def finalize(self):

        return HHSIRBlock(
            nodes=self.nodes
        )


# ============================================================
# SERIALIZATION
# ============================================================

def hhs_ir_to_json(block: HHSIRBlock):

    return json.dumps(
        {
            "entry_phase": block.entry_phase,
            "parent_block": block.parent_block,
            "nodes": [
                asdict(n)
                for n in block.nodes
            ]
        },
        indent=2
    )


# ============================================================
# BINARY HIR EMIT
# ============================================================

def hhs_write_hir_file(
    path,
    block: HHSIRBlock
):

    with open(path, "w") as f:

        for n in block.nodes:

            f.write(
                f"{n.op} "
                f"{n.dst} "
                f"{n.srcA} "
                f"{n.srcB} "
                f"{n.imm}\n"
            )


# ============================================================
# COMPILE ENTRY
# ============================================================

def hhs_compile_python_source(source: str):

    tree = ast.parse(source)

    bridge = HHSPythonBridge()

    bridge.visit(tree)

    return bridge.finalize()


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("input")
    parser.add_argument("--json")
    parser.add_argument("--hir")

    args = parser.parse_args()

    with open(args.input, "r") as f:
        source = f.read()

    block = hhs_compile_python_source(source)

    if args.json:

        with open(args.json, "w") as f:
            f.write(hhs_ir_to_json(block))

    if args.hir:

        hhs_write_hir_file(args.hir, block)

    print(
        "[HHS] compiled",
        len(block.nodes),
        "IR nodes"
    )