# hhs_python/runtime/hhs_tensor81_execution_lattice.py
#
# HHS / HARMONICODE
# Tensor81 Execution Lattice
#
# Canonical Runtime OS Spatial Manifold Execution Substrate
#
# Runtime Principle:
#
#   execution
#   =
#   distributed phase propagation
#   through Tensor81 manifold geometry
#
# NOT:
#
#   centralized instruction traversal
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward execution traversal
#   v^72 = reciprocal execution reconstruction
#   C^216 = Tensor81 spatial execution closure
#
# Runtime Primitive:
#
#   spatial recursive manifold execution
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import hashlib
import json
import time

# ============================================================
# CONSTANTS
# ============================================================

HASH216_WIDTH = 216
TENSOR81_SIZE = 81
LOSHU_CLUSTER_COUNT = 9
PHASE_LAYER_COUNT = 4

# ============================================================
# HASH216
# ============================================================

def _hash216(data: str) -> str:
    """
    Canonical HASH216 projection layer.
    """

    h1 = hashlib.sha512(data.encode()).hexdigest()
    h2 = hashlib.sha256(data.encode()).hexdigest()

    merged = h1 + h2

    return merged[:HASH216_WIDTH]


# ============================================================
# EXECUTION WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSExecutionWitness:
    """
    Canonical Tensor81 execution witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    executable: bool = True
    reconstructible: bool = True
    phase_entangled: bool = True
    cluster_equivalent: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.executable
            and self.reconstructible
            and self.phase_entangled
            and self.cluster_equivalent
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# TENSOR81 EXECUTION CELL
# ============================================================

@dataclass(frozen=True)
class HHSTensor81ExecutionCell:
    """
    Canonical spatial execution carrier.

    Execution is:
        distributed Tensor81 phase propagation.
    """

    cell_id: str

    # ========================================================
    # SPATIAL TOPOLOGY
    # ========================================================

    tensor_index: int
    loshu_cluster_index: int
    phase_layer: int
    reciprocal_partner_index: int

    # ========================================================
    # EXECUTION FIELDS
    # ========================================================

    execution_hash216: str
    opcode_hash216: str
    transport_hash216: str
    governance_hash216: str
    identity_hash216: str
    semantic_hash216: str
    causal_hash216: str
    temporal_hash216: str
    multimodal_hash216: str

    # ========================================================
    # EXECUTION TRAVERSAL
    # ========================================================

    forward_execution_hash216: str
    reciprocal_execution_hash216: str

    # ========================================================
    # CELL TOPOLOGY
    # ========================================================

    cell_topology_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    executable: bool = True
    reconstructible: bool = True
    phase_entangled: bool = True
    cluster_equivalent: bool = True
    temporally_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    execution_witness: Optional[
        HHSExecutionWitness
    ] = None

    transport_witness: Optional[
        HHSExecutionWitness
    ] = None

    governance_witness: Optional[
        HHSExecutionWitness
    ] = None

    reciprocal_witness: Optional[
        HHSExecutionWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    cell_proof_hash216: str = ""

    # ========================================================
    # TIME
    # ========================================================

    timestamp_ns: int = field(
        default_factory=time.time_ns
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(self) -> bool:
        """
        Universal Tensor81 execution validation.
        """

        if not self.executable:
            return False

        if not self.reconstructible:
            return False

        if not self.phase_entangled:
            return False

        if not self.cluster_equivalent:
            return False

        if not self.temporally_equivalent:
            return False

        if not (
            0 <= self.tensor_index
            < TENSOR81_SIZE
        ):
            return False

        if not (
            0 <= self.loshu_cluster_index
            < LOSHU_CLUSTER_COUNT
        ):
            return False

        if not (
            0 <= self.phase_layer
            < PHASE_LAYER_COUNT
        ):
            return False

        witnesses = [
            self.execution_witness,
            self.transport_witness,
            self.governance_witness,
            self.reciprocal_witness,
        ]

        for witness in witnesses:

            if witness is None:
                continue

            if not witness.validate():
                return False

        return True

    # ========================================================
    # HASH216 CLOSURE
    # ========================================================

    def closure_hash216(self) -> str:
        """
        Canonical Tensor81 execution closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "cell_id": self.cell_id,
            "tensor_index": self.tensor_index,
            "loshu_cluster_index": (
                self.loshu_cluster_index
            ),
            "phase_layer": self.phase_layer,
            "reciprocal_partner_index": (
                self.reciprocal_partner_index
            ),
            "execution": self.execution_hash216,
            "opcode": self.opcode_hash216,
            "transport": self.transport_hash216,
            "governance": (
                self.governance_hash216
            ),
            "identity": self.identity_hash216,
            "semantic": self.semantic_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "multimodal": (
                self.multimodal_hash216
            ),
            "forward": (
                self.forward_execution_hash216
            ),
            "reciprocal": (
                self.reciprocal_execution_hash216
            ),
            "topology": (
                self.cell_topology_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # EXECUTABLE
    # ========================================================

    def verify_executable(
        self,
    ) -> bool:
        """
        Tensor81 execution admissibility invariant.
        """

        return (
            self.executable
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Spatial execution reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # PHASE ENTANGLEMENT
    # ========================================================

    def verify_phase_entanglement(
        self,
    ) -> bool:
        """
        Reciprocal Tensor81 execution invariant.
        """

        return (
            self.phase_entangled
            and self.validate()
        )

    # ========================================================
    # CLUSTER EQUIVALENCE
    # ========================================================

    def verify_cluster_equivalence(
        self,
    ) -> bool:
        """
        Lo Shu cluster continuity invariant.
        """

        return (
            self.cluster_equivalent
            and self.validate()
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Spatial temporal continuity invariant.
        """

        return (
            self.temporally_equivalent
            and self.validate()
        )

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical Tensor81 execution receipt.
        """

        return {
            "cell_id": self.cell_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "cell_proof_hash216": (
                self.cell_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# TENSOR81 EXECUTION LATTICE
# ============================================================

class HHSTensor81ExecutionLattice:
    """
    Canonical Runtime OS spatial execution substrate.

    Execution is:
        distributed Tensor81 phase propagation.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.cell_registry: Dict[
            str,
            HHSTensor81ExecutionCell
        ] = {}

        self.cell_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.cell_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.tensor_index_field: Dict[
            str,
            int
        ] = {}

        self.cluster_field: Dict[
            str,
            int
        ] = {}

        self.phase_field: Dict[
            str,
            int
        ] = {}

        self.execution_field: Dict[
            str,
            str
        ] = {}

        self.transport_field: Dict[
            str,
            str
        ] = {}

        self.governance_field: Dict[
            str,
            str
        ] = {}

        self.identity_field: Dict[
            str,
            str
        ] = {}

        self.semantic_field: Dict[
            str,
            str
        ] = {}

        self.causal_field: Dict[
            str,
            str
        ] = {}

        self.temporal_field: Dict[
            str,
            str
        ] = {}

        self.multimodal_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER CELL
    # ========================================================

    def register_cell(
        self,
        cell: HHSTensor81ExecutionCell,
    ) -> bool:
        """
        Register Tensor81 execution cell.
        """

        if not cell.validate():
            return False

        self.cell_registry[
            cell.cell_id
        ] = cell

        if (
            cell.cell_id
            not in self.cell_lineage
        ):

            self.cell_lineage[
                cell.cell_id
            ] = []

        self.cell_lineage[
            cell.cell_id
        ].append(
            cell.closure_hash216()
        )

        self.tensor_index_field[
            cell.cell_id
        ] = cell.tensor_index

        self.cluster_field[
            cell.cell_id
        ] = (
            cell.loshu_cluster_index
        )

        self.phase_field[
            cell.cell_id
        ] = cell.phase_layer

        self.execution_field[
            cell.cell_id
        ] = (
            cell.execution_hash216
        )

        self.transport_field[
            cell.cell_id
        ] = (
            cell.transport_hash216
        )

        self.governance_field[
            cell.cell_id
        ] = (
            cell.governance_hash216
        )

        self.identity_field[
            cell.cell_id
        ] = (
            cell.identity_hash216
        )

        self.semantic_field[
            cell.cell_id
        ] = (
            cell.semantic_hash216
        )

        self.causal_field[
            cell.cell_id
        ] = (
            cell.causal_hash216
        )

        self.temporal_field[
            cell.cell_id
        ] = (
            cell.temporal_hash216
        )

        self.multimodal_field[
            cell.cell_id
        ] = (
            cell.multimodal_hash216
        )

        if (
            cell.cell_id
            not in self.cell_dependencies
        ):

            self.cell_dependencies[
                cell.cell_id
            ] = set()

        return True

    # ========================================================
    # CONNECT CELLS
    # ========================================================

    def connect_cells(
        self,
        source_cell: str,
        target_cell: str,
    ) -> bool:
        """
        Establish Tensor81 execution dependency.
        """

        if (
            source_cell
            not in self.cell_registry
        ):
            return False

        if (
            target_cell
            not in self.cell_registry
        ):
            return False

        self.cell_dependencies[
            source_cell
        ].add(
            target_cell
        )

        return True

    # ========================================================
    # VALIDATE LATTICE
    # ========================================================

    def validate_lattice(
        self,
    ) -> bool:
        """
        Universal Tensor81 execution validation.
        """

        for cell in (
            self.cell_registry.values()
        ):

            if not cell.validate():
                return False

        return True

    # ========================================================
    # EXECUTABLE
    # ========================================================

    def executable(
        self,
    ) -> bool:
        """
        Global Tensor81 execution continuity.
        """

        for cell in (
            self.cell_registry.values()
        ):

            if not (
                cell.verify_executable()
            ):
                return False

        return True

    # ========================================================
    # CELL CONE
    # ========================================================

    def cell_cone(
        self,
        cell_id: str,
    ) -> Set[str]:
        """
        Compute Tensor81 execution dependency cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.cell_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(cell_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global Tensor81 execution closure.
        """

        payload = {
            "cell_registry": sorted(
                [
                    cell.closure_hash216()
                    for cell in (
                        self.cell_registry.values()
                    )
                ]
            ),
            "lineage": self.cell_lineage,
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.cell_dependencies.items()
                )
            },
            "tensor_index": (
                self.tensor_index_field
            ),
            "cluster": (
                self.cluster_field
            ),
            "phase": (
                self.phase_field
            ),
            "execution": (
                self.execution_field
            ),
            "transport": (
                self.transport_field
            ),
            "governance": (
                self.governance_field
            ),
            "identity": (
                self.identity_field
            ),
            "semantic": (
                self.semantic_field
            ),
            "causal": (
                self.causal_field
            ),
            "temporal": (
                self.temporal_field
            ),
            "multimodal": (
                self.multimodal_field
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # AUTHORITATIVE CELL
    # ========================================================

    def authoritative_cell(
        self,
    ) -> Optional[
        HHSTensor81ExecutionCell
    ]:
        """
        Determine cell closest
        to Tensor81 execution closure.
        """

        if not self.cell_registry:
            return None

        ordered = sorted(
            self.cell_registry.values(),
            key=lambda c: (
                c.closure_hash216(),
                c.cell_topology_hash216,
            ),
        )

        return ordered[0]

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical Tensor81 execution lattice receipt.
        """

        authoritative = (
            self.authoritative_cell()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "cell_count": len(
                self.cell_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.cell_dependencies.values()
                )
            ),
            "executable": (
                self.executable()
            ),
            "authoritative_cell": (
                authoritative.cell_id
                if authoritative
                else None
            ),
            "valid": (
                self.validate_lattice()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }