# hhs_python/runtime/hhs_recursive_phase_compiler.py
#
# HHS / HARMONICODE
# Recursive Phase Compiler
#
# Canonical Runtime OS Manifold Execution Synthesis Layer
#
# Runtime Principle:
#
#   execution
#   =
#   recursive phase projection
#   of invariant manifold topology
#
# NOT:
#
#   linear instruction translation
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward compilation traversal
#   v^72 = reciprocal compilation reconstruction
#   C^216 = executable manifold compilation closure
#
# Runtime Primitive:
#
#   recursive executable manifold synthesis
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
# PHASE OPCODE
# ============================================================

@dataclass(frozen=True)
class HHSPhaseOpcode:
    """
    Canonical reversible manifold opcode.
    """

    opcode_id: str

    mnemonic: str

    forward_hash216: str
    reciprocal_hash216: str

    phase_index: int = 0
    tensor_slot: int = 0

    reversible: bool = True
    reconstructible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.reversible
            and self.reconstructible
            and bool(self.mnemonic)
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# PHASE WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSPhaseWitness:
    """
    Canonical executable manifold witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    compilable: bool = True
    reconstructible: bool = True
    phase_executable: bool = True
    origin_equivalent: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.compilable
            and self.reconstructible
            and self.phase_executable
            and self.origin_equivalent
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# RECURSIVE PHASE PROGRAM
# ============================================================

@dataclass(frozen=True)
class HHSRecursivePhaseProgram:
    """
    Canonical executable manifold carrier.

    Execution is:
        recursive phase projection of topology.
    """

    program_id: str

    # ========================================================
    # COMPILATION FIELDS
    # ========================================================

    source_topology_hash216: str
    ir_hash216: str
    phase_opcode_hash216: str
    tensor81_hash216: str

    identity_hash216: str
    replay_hash216: str
    semantic_hash216: str
    causal_hash216: str
    temporal_hash216: str
    consensus_hash216: str
    multimodal_hash216: str
    governance_hash216: str
    transport_hash216: str

    # ========================================================
    # COMPILATION TRAVERSAL
    # ========================================================

    forward_compilation_hash216: str
    reciprocal_compilation_hash216: str

    # ========================================================
    # COMPILATION TOPOLOGY
    # ========================================================

    compilation_topology_hash216: str

    # ========================================================
    # OPCODES
    # ========================================================

    phase_opcodes: Tuple[
        HHSPhaseOpcode,
        ...
    ] = ()

    # ========================================================
    # FLAGS
    # ========================================================

    compilable: bool = True
    reconstructible: bool = True
    phase_executable: bool = True
    origin_equivalent: bool = True
    temporally_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    source_witness: Optional[
        HHSPhaseWitness
    ] = None

    replay_witness: Optional[
        HHSPhaseWitness
    ] = None

    transport_witness: Optional[
        HHSPhaseWitness
    ] = None

    governance_witness: Optional[
        HHSPhaseWitness
    ] = None

    reciprocal_witness: Optional[
        HHSPhaseWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    program_proof_hash216: str = ""

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
        Universal recursive compilation validation.
        """

        if not self.compilable:
            return False

        if not self.reconstructible:
            return False

        if not self.phase_executable:
            return False

        if not self.origin_equivalent:
            return False

        if not self.temporally_equivalent:
            return False

        for opcode in self.phase_opcodes:

            if not opcode.validate():
                return False

        witnesses = [
            self.source_witness,
            self.replay_witness,
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
        Canonical compilation closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "program_id": self.program_id,
            "source_topology": (
                self.source_topology_hash216
            ),
            "ir": self.ir_hash216,
            "opcode": self.phase_opcode_hash216,
            "tensor81": self.tensor81_hash216,
            "identity": self.identity_hash216,
            "replay": self.replay_hash216,
            "semantic": self.semantic_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "consensus": self.consensus_hash216,
            "multimodal": self.multimodal_hash216,
            "governance": self.governance_hash216,
            "transport": self.transport_hash216,
            "forward": (
                self.forward_compilation_hash216
            ),
            "reciprocal": (
                self.reciprocal_compilation_hash216
            ),
            "topology": (
                self.compilation_topology_hash216
            ),
            "opcodes": [
                {
                    "opcode_id": (
                        op.opcode_id
                    ),
                    "mnemonic": (
                        op.mnemonic
                    ),
                    "phase_index": (
                        op.phase_index
                    ),
                    "tensor_slot": (
                        op.tensor_slot
                    ),
                }
                for op in self.phase_opcodes
            ],
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # COMPILABLE
    # ========================================================

    def verify_compilable(
        self,
    ) -> bool:
        """
        Recursive compilation admissibility invariant.
        """

        return (
            self.compilable
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Executable manifold reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # PHASE EXECUTABLE
    # ========================================================

    def verify_phase_executable(
        self,
    ) -> bool:
        """
        Recursive phase execution invariant.
        """

        return (
            self.phase_executable
            and self.validate()
        )

    # ========================================================
    # ORIGIN EQUIVALENCE
    # ========================================================

    def verify_origin_equivalence(
        self,
    ) -> bool:
        """
        Executable origin continuity invariant.
        """

        return (
            self.origin_equivalent
            and self.validate()
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Executable temporal continuity invariant.
        """

        return (
            self.temporally_equivalent
            and self.validate()
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Replay-admissible deterministic serialization.
        """

        return {
            "program_id": self.program_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "program_proof_hash216": (
                self.program_proof_hash216
            ),
            "compilable": (
                self.verify_compilable()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "phase_executable": (
                self.verify_phase_executable()
            ),
            "origin_equivalent": (
                self.verify_origin_equivalence()
            ),
            "temporally_equivalent": (
                self.verify_temporal_equivalence()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical recursive phase program receipt.
        """

        return {
            "program_id": self.program_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "program_proof_hash216": (
                self.program_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# RECURSIVE PHASE COMPILER
# ============================================================

class HHSRecursivePhaseCompiler:
    """
    Canonical Runtime OS manifold execution synthesis layer.

    Execution is:
        recursive phase projection of topology.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.program_registry: Dict[
            str,
            HHSRecursivePhaseProgram
        ] = {}

        self.program_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.program_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.source_topology_field: Dict[
            str,
            str
        ] = {}

        self.ir_field: Dict[
            str,
            str
        ] = {}

        self.phase_opcode_field: Dict[
            str,
            str
        ] = {}

        self.tensor81_field: Dict[
            str,
            str
        ] = {}

        self.identity_field: Dict[
            str,
            str
        ] = {}

        self.replay_field: Dict[
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

        self.consensus_field: Dict[
            str,
            str
        ] = {}

        self.multimodal_field: Dict[
            str,
            str
        ] = {}

        self.governance_field: Dict[
            str,
            str
        ] = {}

        self.transport_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER PROGRAM
    # ========================================================

    def register_program(
        self,
        program: HHSRecursivePhaseProgram,
    ) -> bool:
        """
        Register executable manifold program.
        """

        if not program.validate():
            return False

        self.program_registry[
            program.program_id
        ] = program

        if (
            program.program_id
            not in self.program_lineage
        ):

            self.program_lineage[
                program.program_id
            ] = []

        self.program_lineage[
            program.program_id
        ].append(
            program.closure_hash216()
        )

        self.source_topology_field[
            program.program_id
        ] = (
            program.source_topology_hash216
        )

        self.ir_field[
            program.program_id
        ] = (
            program.ir_hash216
        )

        self.phase_opcode_field[
            program.program_id
        ] = (
            program.phase_opcode_hash216
        )

        self.tensor81_field[
            program.program_id
        ] = (
            program.tensor81_hash216
        )

        self.identity_field[
            program.program_id
        ] = (
            program.identity_hash216
        )

        self.replay_field[
            program.program_id
        ] = (
            program.replay_hash216
        )

        self.semantic_field[
            program.program_id
        ] = (
            program.semantic_hash216
        )

        self.causal_field[
            program.program_id
        ] = (
            program.causal_hash216
        )

        self.temporal_field[
            program.program_id
        ] = (
            program.temporal_hash216
        )

        self.consensus_field[
            program.program_id
        ] = (
            program.consensus_hash216
        )

        self.multimodal_field[
            program.program_id
        ] = (
            program.multimodal_hash216
        )

        self.governance_field[
            program.program_id
        ] = (
            program.governance_hash216
        )

        self.transport_field[
            program.program_id
        ] = (
            program.transport_hash216
        )

        if (
            program.program_id
            not in self.program_dependencies
        ):

            self.program_dependencies[
                program.program_id
            ] = set()

        return True

    # ========================================================
    # PROGRAM DEPENDENCY
    # ========================================================

    def connect_program_dependency(
        self,
        source_program: str,
        target_program: str,
    ) -> bool:
        """
        Establish executable manifold dependency.
        """

        if (
            source_program
            not in self.program_registry
        ):
            return False

        if (
            target_program
            not in self.program_registry
        ):
            return False

        self.program_dependencies[
            source_program
        ].add(
            target_program
        )

        return True

    # ========================================================
    # VALIDATE COMPILER
    # ========================================================

    def validate_compiler(
        self,
    ) -> bool:
        """
        Universal recursive compilation validation.
        """

        for program in (
            self.program_registry.values()
        ):

            if not program.validate():
                return False

        return True

    # ========================================================
    # PHASE EXECUTABLE
    # ========================================================

    def phase_executable(
        self,
    ) -> bool:
        """
        Global executable manifold continuity.
        """

        for program in (
            self.program_registry.values()
        ):

            if not (
                program.verify_phase_executable()
            ):
                return False

        return True

    # ========================================================
    # PROGRAM CONE
    # ========================================================

    def program_cone(
        self,
        program_id: str,
    ) -> Set[str]:
        """
        Compute executable dependency cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.program_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(program_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global recursive compiler closure.
        """

        payload = {
            "program_registry": sorted(
                [
                    program.closure_hash216()
                    for program in (
                        self.program_registry.values()
                    )
                ]
            ),
            "lineage": self.program_lineage,
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.program_dependencies.items()
                )
            },
            "source_topology": (
                self.source_topology_field
            ),
            "ir": self.ir_field,
            "phase_opcode": (
                self.phase_opcode_field
            ),
            "tensor81": (
                self.tensor81_field
            ),
            "identity": (
                self.identity_field
            ),
            "replay": (
                self.replay_field
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
            "consensus": (
                self.consensus_field
            ),
            "multimodal": (
                self.multimodal_field
            ),
            "governance": (
                self.governance_field
            ),
            "transport": (
                self.transport_field
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # AUTHORITATIVE PROGRAM
    # ========================================================

    def authoritative_program(
        self,
    ) -> Optional[
        HHSRecursivePhaseProgram
    ]:
        """
        Determine executable program closest
        to recursive phase closure.
        """

        if not self.program_registry:
            return None

        ordered = sorted(
            self.program_registry.values(),
            key=lambda p: (
                p.closure_hash216(),
                p.compilation_topology_hash216,
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
        Canonical recursive phase compiler receipt.
        """

        authoritative = (
            self.authoritative_program()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "program_count": len(
                self.program_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.program_dependencies.values()
                )
            ),
            "phase_executable": (
                self.phase_executable()
            ),
            "authoritative_program": (
                authoritative.program_id
                if authoritative
                else None
            ),
            "valid": (
                self.validate_compiler()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }