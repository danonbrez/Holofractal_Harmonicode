# ============================================================
# hhs_execution_geometry_v1.py
# HARMONICODE / HHS EXECUTION GEOMETRY
#
# Canonical execution manifold geometry.
#
# Defines:
#   - node classes
#   - edge classes
#   - canonical execution flow
#   - receipt-spine invariants
#   - sandbox projection rules
#   - replay / prediction graph hooks
#
# IMPORTANT:
#   No canonical state mutation may bypass:
#
#       IR → VM → Witness → Receipt
#
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import time

# ============================================================
# NODE TYPES
# ============================================================

class NodeType(str, Enum):

    INPUT                       = "InputNode"
    NORMALIZED                  = "NormalizedSignalNode"
    TOKEN                       = "TokenTensorNode"
    OPERATOR                    = "OperatorCandidateNode"
    IR                          = "IRBlockNode"
    VM                          = "VMExecutionNode"
    WITNESS                     = "ClosureWitnessNode"
    RECEIPT                     = "Hash72ReceiptNode"
    MEMORY                      = "VectorGraphMemoryNode"
    REPLAY                      = "ReplayPredictionNode"
    CONSENSUS                   = "ConsensusSandboxNode"

# ============================================================
# EDGE TYPES
# ============================================================

class EdgeType(str, Enum):

    NORMALIZES                  = "E_NORMALIZES"
    TOKENIZES                   = "E_TOKENIZES"
    SELECTS_OPERATOR            = "E_SELECTS_OPERATOR"
    LOWERS_TO_IR                = "E_LOWERS_TO_IR"
    EXECUTES_ON_VM              = "E_EXECUTES_ON_VM"
    EMITS_WITNESS               = "E_EMITS_WITNESS"
    COMMITS_RECEIPT             = "E_COMMITS_RECEIPT"
    INDEXES_MEMORY              = "E_INDEXES_MEMORY"
    PREDICTS_NEXT               = "E_PREDICTS_NEXT"
    PROJECTS_SANDBOX            = "E_PROJECTS_SANDBOX"
    REENTERS_CONTEXT            = "E_REENTERS_CONTEXT"

# ============================================================
# EXECUTION NODE
# ============================================================

@dataclass
class ExecutionNode:

    node_id: str
    node_type: NodeType

    timestamp: float

    payload: Dict[str, Any] = field(default_factory=dict)

    receipt_hash72: Optional[str] = None

    canonical: bool = False
    sandboxed: bool = False

# ============================================================
# EXECUTION EDGE
# ============================================================

@dataclass
class ExecutionEdge:

    edge_id: str

    edge_type: EdgeType

    src: str
    dst: str

    timestamp: float

    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================
# GEOMETRY MANIFOLD
# ============================================================

class HHSExecutionGeometry:

    """
    Canonical execution manifold graph.
    """

    def __init__(self):

        self.nodes: Dict[str, ExecutionNode] = {}
        self.edges: List[ExecutionEdge] = []

        self.receipt_spine: List[str] = []

    # ========================================================
    # NODE CREATION
    # ========================================================

    def create_node(
        self,
        node_type: NodeType,
        payload: Optional[Dict[str, Any]] = None,
        canonical: bool = False,
        sandboxed: bool = False,
        receipt_hash72: Optional[str] = None
    ) -> str:

        node_id = str(uuid.uuid4())

        node = ExecutionNode(
            node_id=node_id,
            node_type=node_type,
            timestamp=time.time(),
            payload=payload or {},
            canonical=canonical,
            sandboxed=sandboxed,
            receipt_hash72=receipt_hash72
        )

        self.nodes[node_id] = node

        if node_type == NodeType.RECEIPT:
            self.receipt_spine.append(node_id)

        return node_id

    # ========================================================
    # EDGE CREATION
    # ========================================================

    def connect(
        self,
        src: str,
        dst: str,
        edge_type: EdgeType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:

        edge_id = str(uuid.uuid4())

        edge = ExecutionEdge(
            edge_id=edge_id,
            edge_type=edge_type,
            src=src,
            dst=dst,
            timestamp=time.time(),
            metadata=metadata or {}
        )

        self.edges.append(edge)

        return edge_id

    # ========================================================
    # RECEIPT SPINE VALIDATION
    # ========================================================

    def validate_receipt_spine(self) -> bool:

        """
        Ensures canonical mutations pass through:

            IR
              → VM
              → WITNESS
              → RECEIPT
        """

        for i in range(len(self.receipt_spine)):

            receipt_id = self.receipt_spine[i]

            receipt_node = self.nodes[receipt_id]

            if receipt_node.node_type != NodeType.RECEIPT:
                return False

            witness_ok = False
            vm_ok = False
            ir_ok = False

            witness_nodes = []

            for e in self.edges:

                if e.dst == receipt_id and \
                   e.edge_type == EdgeType.COMMITS_RECEIPT:

                    src_node = self.nodes[e.src]

                    if src_node.node_type == NodeType.WITNESS:
                        witness_ok = True
                        witness_nodes.append(src_node.node_id)

            for witness_id in witness_nodes:

                for e in self.edges:

                    if e.dst == witness_id and \
                       e.edge_type == EdgeType.EMITS_WITNESS:

                        src_node = self.nodes[e.src]

                        if src_node.node_type == NodeType.VM:
                            vm_ok = True

                            vm_id = src_node.node_id

                            for e2 in self.edges:

                                if e2.dst == vm_id and \
                                   e2.edge_type == EdgeType.EXECUTES_ON_VM:

                                    ir_node = self.nodes[e2.src]

                                    if ir_node.node_type == NodeType.IR:
                                        ir_ok = True

            if not (witness_ok and vm_ok and ir_ok):
                return False

        return True

    # ========================================================
    # SANDBOX PROJECTION
    # ========================================================

    def project_sandbox(
        self,
        receipt_node_id: str,
        sandbox_payload: Dict[str, Any]
    ) -> str:

        sandbox_node = self.create_node(
            node_type=NodeType.CONSENSUS,
            payload=sandbox_payload,
            canonical=False,
            sandboxed=True
        )

        self.connect(
            receipt_node_id,
            sandbox_node,
            EdgeType.PROJECTS_SANDBOX
        )

        return sandbox_node

    # ========================================================
    # MEMORY INDEX
    # ========================================================

    def index_memory(
        self,
        receipt_node_id: str,
        memory_payload: Dict[str, Any]
    ) -> str:

        memory_node = self.create_node(
            node_type=NodeType.MEMORY,
            payload=memory_payload,
            canonical=True
        )

        self.connect(
            receipt_node_id,
            memory_node,
            EdgeType.INDEXES_MEMORY
        )

        return memory_node

    # ========================================================
    # REPLAY PREDICTION
    # ========================================================

    def replay_prediction(
        self,
        memory_node_id: str,
        replay_payload: Dict[str, Any]
    ) -> str:

        replay_node = self.create_node(
            node_type=NodeType.REPLAY,
            payload=replay_payload
        )

        self.connect(
            memory_node_id,
            replay_node,
            EdgeType.PREDICTS_NEXT
        )

        return replay_node

    # ========================================================
    # GEOMETRY SUMMARY
    # ========================================================

    def summary(self) -> Dict[str, Any]:

        node_counts: Dict[str, int] = {}

        for n in self.nodes.values():

            key = n.node_type.value

            node_counts[key] = \
                node_counts.get(key, 0) + 1

        return {

            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),

            "receipt_spine_length":
                len(self.receipt_spine),

            "receipt_spine_valid":
                self.validate_receipt_spine(),

            "node_counts":
                node_counts
        }

# ============================================================
# CANONICAL FLOW BUILDER
# ============================================================

def build_canonical_execution_flow(
    geom: HHSExecutionGeometry,
    input_payload: Dict[str, Any],
    normalized_payload: Dict[str, Any],
    token_payload: Dict[str, Any],
    operator_payload: Dict[str, Any],
    ir_payload: Dict[str, Any],
    vm_payload: Dict[str, Any],
    witness_payload: Dict[str, Any],
    receipt_payload: Dict[str, Any]
):

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    n_input = geom.create_node(
        NodeType.INPUT,
        input_payload
    )

    # --------------------------------------------------------
    # NORMALIZED
    # --------------------------------------------------------

    n_norm = geom.create_node(
        NodeType.NORMALIZED,
        normalized_payload
    )

    geom.connect(
        n_input,
        n_norm,
        EdgeType.NORMALIZES
    )

    # --------------------------------------------------------
    # TOKEN
    # --------------------------------------------------------

    n_tok = geom.create_node(
        NodeType.TOKEN,
        token_payload
    )

    geom.connect(
        n_norm,
        n_tok,
        EdgeType.TOKENIZES
    )

    # --------------------------------------------------------
    # OPERATOR
    # --------------------------------------------------------

    n_op = geom.create_node(
        NodeType.OPERATOR,
        operator_payload
    )

    geom.connect(
        n_tok,
        n_op,
        EdgeType.SELECTS_OPERATOR
    )

    # --------------------------------------------------------
    # IR
    # --------------------------------------------------------

    n_ir = geom.create_node(
        NodeType.IR,
        ir_payload
    )

    geom.connect(
        n_op,
        n_ir,
        EdgeType.LOWERS_TO_IR
    )

    # --------------------------------------------------------
    # VM
    # --------------------------------------------------------

    n_vm = geom.create_node(
        NodeType.VM,
        vm_payload
    )

    geom.connect(
        n_ir,
        n_vm,
        EdgeType.EXECUTES_ON_VM
    )

    # --------------------------------------------------------
    # WITNESS
    # --------------------------------------------------------

    n_w = geom.create_node(
        NodeType.WITNESS,
        witness_payload
    )

    geom.connect(
        n_vm,
        n_w,
        EdgeType.EMITS_WITNESS
    )

    # --------------------------------------------------------
    # RECEIPT
    # --------------------------------------------------------

    n_r = geom.create_node(
        NodeType.RECEIPT,
        receipt_payload,
        canonical=True,
        receipt_hash72=receipt_payload.get(
            "receipt_hash72"
        )
    )

    geom.connect(
        n_w,
        n_r,
        EdgeType.COMMITS_RECEIPT
    )

    return n_r

# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    geom = HHSExecutionGeometry()

    receipt_id = build_canonical_execution_flow(

        geom,

        input_payload={
            "text": "x*y"
        },

        normalized_payload={
            "normalized": "x*y"
        },

        token_payload={
            "tokens": ["x", "*", "y"]
        },

        operator_payload={
            "operator": "MULXY"
        },

        ir_payload={
            "ir": "MULXY R1,R2,R3"
        },

        vm_payload={
            "vm_step": 1
        },

        witness_payload={
            "closure": "orientation"
        },

        receipt_payload={
            "receipt_hash72":
                "ABCDEF0123456789"
        }
    )

    geom.index_memory(
        receipt_id,
        {
            "embedding_id": "mem001"
        }
    )

    print(geom.summary())