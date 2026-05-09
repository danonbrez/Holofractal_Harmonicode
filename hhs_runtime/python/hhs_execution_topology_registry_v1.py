# hhs_runtime/python/hhs_execution_topology_registry_v1.py
#
# HARMONICODE / HHS
# Canonical Runtime Topology Registry
#
# PURPOSE:
#
#   Defines authoritative ownership boundaries for:
#
#       execution
#       receipts
#       replay
#       graph insertion
#       multimodal routing
#       closure domains
#       virtual overlays
#
#   Prevents:
#
#       duplicate authorities
#       fragmented routing
#       parallel receipt chains
#       cache divergence
#       replay inconsistencies
#
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

# ============================================================
# DOMAIN TYPES
# ============================================================

DOMAIN_RUNTIME = "runtime"
DOMAIN_RECEIPT = "receipt"
DOMAIN_GRAPH = "graph"
DOMAIN_REPLAY = "replay"
DOMAIN_CONSENSUS = "consensus"
DOMAIN_MEMORY = "memory"
DOMAIN_TRANSPORT = "transport"
DOMAIN_ALIGNMENT = "alignment"
DOMAIN_AGENT = "agent"

# ============================================================
# CLOSURE TYPES
# ============================================================

CLOSURE_TRANSPORT = "transport"
CLOSURE_ORIENTATION = "orientation"
CLOSURE_CONSTRAINT = "constraint"
CLOSURE_IDENTITY = "identity"
CLOSURE_REPLAY = "replay"
CLOSURE_CONSENSUS = "consensus"

# ============================================================
# TOPOLOGY NODE
# ============================================================

@dataclass
class HHSTopologyNode:

    node_id: str

    module_name: str

    authority_path: str

    domain: str

    closure_domains: List[str]

    owns_receipts: bool = False

    owns_graph: bool = False

    owns_replay: bool = False

    owns_memory: bool = False

    owns_transport: bool = False

    owns_agents: bool = False

    dependencies: List[str] = field(
        default_factory=list
    )

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# EXECUTION EDGE
# ============================================================

@dataclass
class HHSTopologyEdge:

    source: str

    target: str

    relation: str

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# REGISTRY
# ============================================================

class HHSExecutionTopologyRegistry:

    def __init__(self):

        self.nodes: Dict[
            str,
            HHSTopologyNode
        ] = {}

        self.edges: List[
            HHSTopologyEdge
        ] = []

        self.domain_owners: Dict[
            str,
            str
        ] = {}

        self.receipt_owner: Optional[
            str
        ] = None

        self.graph_owner: Optional[
            str
        ] = None

        self.replay_owner: Optional[
            str
        ] = None

        self.memory_owner: Optional[
            str
        ] = None

    # ========================================================
    # REGISTER
    # ========================================================

    def register_node(
        self,
        node: HHSTopologyNode,
    ):

        self.validate_authority(node)

        self.nodes[node.node_id] = node

        self.assign_domains(node)

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_authority(
        self,
        node: HHSTopologyNode,
    ):

        existing = self.domain_owners.get(
            node.domain
        )

        if existing:

            old = self.nodes[existing]

            if (
                old.authority_path
                != node.authority_path
            ):
                raise RuntimeError(

                    "Duplicate domain authority:\n"
                    f"domain={node.domain}\n"
                    f"existing={old.module_name}\n"
                    f"new={node.module_name}"
                )

    # ========================================================
    # ASSIGN OWNERSHIP
    # ========================================================

    def assign_domains(
        self,
        node: HHSTopologyNode,
    ):

        self.domain_owners[
            node.domain
        ] = node.node_id

        if node.owns_receipts:

            if (
                self.receipt_owner
                and self.receipt_owner
                != node.node_id
            ):
                raise RuntimeError(
                    "Receipt authority collision"
                )

            self.receipt_owner = node.node_id

        if node.owns_graph:

            if (
                self.graph_owner
                and self.graph_owner
                != node.node_id
            ):
                raise RuntimeError(
                    "Graph authority collision"
                )

            self.graph_owner = node.node_id

        if node.owns_replay:

            if (
                self.replay_owner
                and self.replay_owner
                != node.node_id
            ):
                raise RuntimeError(
                    "Replay authority collision"
                )

            self.replay_owner = node.node_id

        if node.owns_memory:

            if (
                self.memory_owner
                and self.memory_owner
                != node.node_id
            ):
                raise RuntimeError(
                    "Memory authority collision"
                )

            self.memory_owner = node.node_id

    # ========================================================
    # CONNECT
    # ========================================================

    def connect(
        self,
        source: str,
        target: str,
        relation: str,
        metadata: Optional[Dict] = None,
    ):

        if source not in self.nodes:
            raise KeyError(source)

        if target not in self.nodes:
            raise KeyError(target)

        edge = HHSTopologyEdge(

            source=source,

            target=target,

            relation=relation,

            metadata=metadata or {},
        )

        self.edges.append(edge)

    # ========================================================
    # LOOKUPS
    # ========================================================

    def get_node(
        self,
        node_id: str,
    ) -> HHSTopologyNode:

        return self.nodes[node_id]

    def get_domain_owner(
        self,
        domain: str,
    ) -> Optional[HHSTopologyNode]:

        node_id = self.domain_owners.get(
            domain
        )

        if not node_id:
            return None

        return self.nodes[node_id]

    # ========================================================
    # EXECUTION ROUTE
    # ========================================================

    def execution_route(
        self,
        start: str,
    ) -> List[str]:

        visited = set()

        route = []

        def dfs(node_id):

            if node_id in visited:
                return

            visited.add(node_id)

            route.append(node_id)

            for edge in self.edges:

                if edge.source == node_id:
                    dfs(edge.target)

        dfs(start)

        return route

    # ========================================================
    # RECEIPT ROUTE
    # ========================================================

    def receipt_route(self) -> List[str]:

        if not self.receipt_owner:
            return []

        return self.execution_route(
            self.receipt_owner
        )

    # ========================================================
    # GRAPH ROUTE
    # ========================================================

    def graph_route(self) -> List[str]:

        if not self.graph_owner:
            return []

        return self.execution_route(
            self.graph_owner
        )

    # ========================================================
    # VERIFY
    # ========================================================

    def verify_integrity(self):

        if not self.receipt_owner:
            raise RuntimeError(
                "Missing receipt owner"
            )

        if not self.graph_owner:
            raise RuntimeError(
                "Missing graph owner"
            )

        if not self.replay_owner:
            raise RuntimeError(
                "Missing replay owner"
            )

    # ========================================================
    # EXPORT
    # ========================================================

    def export_json(self):

        return {

            "nodes": {

                node_id: {

                    "module":
                        node.module_name,

                    "authority":
                        node.authority_path,

                    "domain":
                        node.domain,

                    "closure_domains":
                        node.closure_domains,

                    "dependencies":
                        node.dependencies,
                }

                for node_id, node
                in self.nodes.items()
            },

            "edges": [

                {

                    "source":
                        edge.source,

                    "target":
                        edge.target,

                    "relation":
                        edge.relation,
                }

                for edge in self.edges
            ],

            "owners": {

                "receipt":
                    self.receipt_owner,

                "graph":
                    self.graph_owner,

                "replay":
                    self.replay_owner,

                "memory":
                    self.memory_owner,
            }
        }

# ============================================================
# DEFAULT TOPOLOGY
# ============================================================

def build_default_topology():

    reg = HHSExecutionTopologyRegistry()

    # ========================================================
    # VM RUNTIME
    # ========================================================

    reg.register_node(

        HHSTopologyNode(

            node_id="vm81_runtime",

            module_name=
                "HARMONICODE_VM_RUNTIME",

            authority_path=
                "hhs_runtime/HARMONICODE_VM_RUNTIME.c",

            domain=DOMAIN_RUNTIME,

            closure_domains=[

                CLOSURE_TRANSPORT,
                CLOSURE_ORIENTATION,
                CLOSURE_CONSTRAINT,
            ],

            owns_transport=True,
        )
    )

    # ========================================================
    # RECEIPT CACHE
    # ========================================================

    reg.register_node(

        HHSTopologyNode(

            node_id="receipt_cache",

            module_name=
                "hhs_receipt_vector_cache_v1",

            authority_path=
                "hhs_runtime/python/hhs_receipt_vector_cache_v1.py",

            domain=DOMAIN_RECEIPT,

            closure_domains=[
                CLOSURE_TRANSPORT
            ],

            owns_receipts=True,
            owns_memory=True,
        )
    )

    # ========================================================
    # GRAPH KERNEL
    # ========================================================

    reg.register_node(

        HHSTopologyNode(

            node_id="graph_kernel",

            module_name=
                "hhs_multimodal_graph_kernel_v1",

            authority_path=
                "hhs_runtime/python/hhs_multimodal_graph_kernel_v1.py",

            domain=DOMAIN_GRAPH,

            closure_domains=[
                CLOSURE_REPLAY
            ],

            owns_graph=True,
        )
    )

    # ========================================================
    # REPLAY ENGINE
    # ========================================================

    reg.register_node(

        HHSTopologyNode(

            node_id="replay_engine",

            module_name=
                "hhs_predictive_replay_engine_v1",

            authority_path=
                "hhs_runtime/python/hhs_predictive_replay_engine_v1.py",

            domain=DOMAIN_REPLAY,

            closure_domains=[
                CLOSURE_REPLAY
            ],

            owns_replay=True,
        )
    )

    # ========================================================
    # CONSENSUS
    # ========================================================

    reg.register_node(

        HHSTopologyNode(

            node_id="consensus_engine",

            module_name=
                "hhs_trace_consensus_engine_v1",

            authority_path=
                "hhs_runtime/python/hhs_trace_consensus_engine_v1.py",

            domain=DOMAIN_CONSENSUS,

            closure_domains=[
                CLOSURE_CONSENSUS
            ],
        )
    )

    # ========================================================
    # ROUTES
    # ========================================================

    reg.connect(
        "vm81_runtime",
        "receipt_cache",
        "commits",
    )

    reg.connect(
        "receipt_cache",
        "graph_kernel",
        "indexes",
    )

    reg.connect(
        "graph_kernel",
        "replay_engine",
        "predicts",
    )

    reg.connect(
        "replay_engine",
        "consensus_engine",
        "votes",
    )

    reg.verify_integrity()

    return reg

# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    topology = build_default_topology()

    print("\n=== TOPOLOGY NODES ===\n")

    for node_id, node in topology.nodes.items():

        print(
            node_id,
            "->",
            node.module_name,
        )

    print("\n=== EXECUTION ROUTE ===\n")

    route = topology.execution_route(
        "vm81_runtime"
    )

    for r in route:
        print(r)

    print("\n=== RECEIPT ROUTE ===\n")

    print(
        topology.receipt_route()
    )

    print("\n=== GRAPH ROUTE ===\n")

    print(
        topology.graph_route()
    )

    print("\n=== EXPORT ===\n")

    import json

    print(
        json.dumps(
            topology.export_json(),
            indent=2,
        )
    )