# ============================================================================
# hhs_backend/runtime/runtime_graph_projection.py
# ============================================================================
#
# Canonical Runtime Graph Projection Engine
#
# Responsibilities:
#
#   - runtime event graph projection
#   - replay lineage projection
#   - event ancestry traversal
#   - receipt linkage
#   - graph serialization
#   - topology normalization
#
# IMPORTANT
# ----------------------------------------------------------------------------
#
# Graphs are PROJECTIONS of runtime state.
#
# Graphs are NOT runtime authority.
#
# Runtime authority belongs to:
#
#   - runtime_event_schema.py
#   - replay lineage
#   - receipt continuity
#
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from hhs_backend.runtime.runtime_event_schema import (
    HHSRuntimeEventEnvelope,
)

# ============================================================================
# Runtime Graph Node
# ============================================================================

@dataclass
class RuntimeGraphNode:

    id: str

    parent: Optional[str] = None

    runtime_id: Optional[str] = None

    branch_id: Optional[str] = None

    receipt_hash72: Optional[str] = None

    event_type: Optional[str] = None

    timestamp_ns: Optional[int] = None

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# Runtime Graph Edge
# ============================================================================

@dataclass
class RuntimeGraphEdge:

    source: str

    target: str

    edge_type: str = "lineage"

# ============================================================================
# RuntimeGraphProjectionEngine
# ============================================================================

class RuntimeGraphProjectionEngine:

    """
    Canonical runtime graph projection engine.
    """

    # =====================================================================
    # Constructor
    # =====================================================================

    def __init__(self):

        self.nodes: Dict[
            str,
            RuntimeGraphNode
        ] = {}

        self.edges: List[
            RuntimeGraphEdge
        ] = []

        self.children_index: Dict[
            str,
            List[str]
        ] = {}

        self.runtime_index: Dict[
            str,
            List[str]
        ] = {}

        self.branch_index: Dict[
            str,
            List[str]
        ] = {}

    # =====================================================================
    # Ingest Event
    # =====================================================================

    def ingest_event(

        self,

        event:
            HHSRuntimeEventEnvelope

    ):

        node = RuntimeGraphNode(

            id=event.event_hash72,

            parent=event.parent_event_hash72,

            runtime_id=event.runtime_id,

            branch_id=event.branch_id,

            receipt_hash72=event.receipt_hash72,

            event_type=event.event_type,

            timestamp_ns=event.created_at_ns,

            payload=event.payload
        )

        # -------------------------------------------------------------
        # Node
        # -------------------------------------------------------------

        self.nodes[
            node.id
        ] = node

        # -------------------------------------------------------------
        # Edge
        # -------------------------------------------------------------

        if node.parent:

            self.edges.append(

                RuntimeGraphEdge(

                    source=node.parent,

                    target=node.id,

                    edge_type="lineage"
                )
            )

            if (
                node.parent
                not in self.children_index
            ):

                self.children_index[
                    node.parent
                ] = []

            self.children_index[
                node.parent
            ].append(node.id)

        # -------------------------------------------------------------
        # Runtime Index
        # -------------------------------------------------------------

        if node.runtime_id:

            if (
                node.runtime_id
                not in self.runtime_index
            ):

                self.runtime_index[
                    node.runtime_id
                ] = []

            self.runtime_index[
                node.runtime_id
            ].append(node.id)

        # -------------------------------------------------------------
        # Branch Index
        # -------------------------------------------------------------

        if node.branch_id:

            if (
                node.branch_id
                not in self.branch_index
            ):

                self.branch_index[
                    node.branch_id
                ] = []

            self.branch_index[
                node.branch_id
            ].append(node.id)

    # =====================================================================
    # Node
    # =====================================================================

    def get_node(
        self,
        node_id: str
    ):

        return self.nodes.get(
            node_id
        )

    # =====================================================================
    # Children
    # =====================================================================

    def get_children(
        self,
        node_id: str
    ) -> List[RuntimeGraphNode]:

        child_ids = (

            self.children_index.get(
                node_id,
                []
            )
        )

        return [

            self.nodes[child_id]

            for child_id in child_ids

            if child_id in self.nodes
        ]

    # =====================================================================
    # Lineage
    # =====================================================================

    def get_lineage(
        self,
        node_id: str
    ) -> List[RuntimeGraphNode]:

        lineage = []

        current = self.nodes.get(
            node_id
        )

        visited: Set[str] = set()

        while current:

            if current.id in visited:

                break

            visited.add(current.id)

            lineage.append(current)

            if not current.parent:

                break

            current = self.nodes.get(
                current.parent
            )

        return lineage

    # =====================================================================
    # Runtime Nodes
    # =====================================================================

    def get_runtime_nodes(
        self,
        runtime_id: str
    ) -> List[RuntimeGraphNode]:

        ids = self.runtime_index.get(
            runtime_id,
            []
        )

        return [

            self.nodes[node_id]

            for node_id in ids

            if node_id in self.nodes
        ]

    # =====================================================================
    # Branch Nodes
    # =====================================================================

    def get_branch_nodes(
        self,
        branch_id: str
    ) -> List[RuntimeGraphNode]:

        ids = self.branch_index.get(
            branch_id,
            []
        )

        return [

            self.nodes[node_id]

            for node_id in ids

            if node_id in self.nodes
        ]

    # =====================================================================
    # Graph Projection
    # =====================================================================

    def project_graph(self):

        return {

            "nodes": [

                self.serialize_node(node)

                for node in self.nodes.values()
            ],

            "edges": [

                self.serialize_edge(edge)

                for edge in self.edges
            ],

            "metrics": {

                "nodes":
                    len(self.nodes),

                "edges":
                    len(self.edges),

                "runtimes":
                    len(self.runtime_index),

                "branches":
                    len(self.branch_index)
            }
        }

    # =====================================================================
    # Serialize Node
    # =====================================================================

    def serialize_node(
        self,
        node: RuntimeGraphNode
    ):

        return {

            "id":
                node.id,

            "parent":
                node.parent,

            "runtime_id":
                node.runtime_id,

            "branch_id":
                node.branch_id,

            "receipt_hash72":
                node.receipt_hash72,

            "event_type":
                node.event_type,

            "timestamp_ns":
                node.timestamp_ns,

            "payload":
                node.payload
        }

    # =====================================================================
    # Serialize Edge
    # =====================================================================

    def serialize_edge(
        self,
        edge: RuntimeGraphEdge
    ):

        return {

            "source":
                edge.source,

            "target":
                edge.target,

            "edge_type":
                edge.edge_type
        }

    # =====================================================================
    # Reset
    # =====================================================================

    def reset(self):

        self.nodes.clear()

        self.edges.clear()

        self.children_index.clear()

        self.runtime_index.clear()

        self.branch_index.clear()

# ============================================================================
# Global Projection Engine
# ============================================================================

runtime_graph_projection_engine = (
    RuntimeGraphProjectionEngine()
)