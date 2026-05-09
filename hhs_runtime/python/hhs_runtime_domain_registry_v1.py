# hhs_runtime/python/hhs_runtime_domain_registry_v1.py
#
# HARMONICODE / HHS
# Runtime Domain Registry
#
# PURPOSE:
#
#   Canonical runtime-domain ownership registry.
#
#   Defines:
#
#       runtime domains
#       closure authorities
#       graph ownership
#       receipt lineage ownership
#       execution routing permissions
#       replay domains
#       adaptive execution permissions
#
#   Prevents:
#
#       duplicate runtime authorities
#       fragmented execution surfaces
#       parallel replay chains
#       receipt divergence
#       graph ownership conflicts
#
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

# ============================================================
# DOMAIN CONSTANTS
# ============================================================

DOMAIN_VM_RUNTIME = "vm_runtime"
DOMAIN_RECEIPT_CACHE = "receipt_cache"
DOMAIN_GRAPH_KERNEL = "graph_kernel"
DOMAIN_REPLAY_ENGINE = "replay_engine"
DOMAIN_CONSENSUS_ENGINE = "consensus_engine"
DOMAIN_MEMORY_OVERLAY = "memory_overlay"
DOMAIN_AGENT_RUNTIME = "agent_runtime"
DOMAIN_ALIGNMENT_GATE = "alignment_gate"
DOMAIN_API_RUNTIME = "api_runtime"
DOMAIN_TRANSPORT = "transport"

# ============================================================
# PERMISSION TYPES
# ============================================================

PERMISSION_READ = "read"
PERMISSION_WRITE = "write"
PERMISSION_EXECUTE = "execute"
PERMISSION_REPLAY = "replay"
PERMISSION_ROUTE = "route"
PERMISSION_VERIFY = "verify"

# ============================================================
# RUNTIME DOMAIN
# ============================================================

@dataclass
class HHSRuntimeDomain:

    domain_id: str

    module_name: str

    authority_path: str

    owner: str

    permissions: Set[str]

    dependencies: Set[str] = field(
        default_factory=set
    )

    receipt_domains: Set[str] = field(
        default_factory=set
    )

    graph_domains: Set[str] = field(
        default_factory=set
    )

    replay_domains: Set[str] = field(
        default_factory=set
    )

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# ROUTE
# ============================================================

@dataclass
class HHSRuntimeRoute:

    source: str

    target: str

    route_type: str

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# REGISTRY
# ============================================================

class HHSRuntimeDomainRegistry:

    def __init__(self):

        self.domains: Dict[
            str,
            HHSRuntimeDomain
        ] = {}

        self.routes: List[
            HHSRuntimeRoute
        ] = []

        self.authority_map: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER DOMAIN
    # ========================================================

    def register_domain(
        self,
        domain: HHSRuntimeDomain,
    ):

        self.validate_domain(domain)

        self.domains[
            domain.domain_id
        ] = domain

        self.authority_map[
            domain.domain_id
        ] = domain.owner

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_domain(
        self,
        domain: HHSRuntimeDomain,
    ):

        if domain.domain_id in self.domains:

            existing = self.domains[
                domain.domain_id
            ]

            if (
                existing.authority_path
                != domain.authority_path
            ):
                raise RuntimeError(

                    "Domain authority conflict:\n"
                    f"domain={domain.domain_id}\n"
                    f"existing={existing.authority_path}\n"
                    f"new={domain.authority_path}"
                )

    # ========================================================
    # CONNECT ROUTE
    # ========================================================

    def connect(
        self,
        source: str,
        target: str,
        route_type: str,
        metadata: Optional[Dict] = None,
    ):

        if source not in self.domains:
            raise KeyError(source)

        if target not in self.domains:
            raise KeyError(target)

        self.routes.append(

            HHSRuntimeRoute(

                source=source,

                target=target,

                route_type=route_type,

                metadata=metadata or {},
            )
        )

    # ========================================================
    # LOOKUPS
    # ========================================================

    def get_domain(
        self,
        domain_id: str,
    ) -> HHSRuntimeDomain:

        return self.domains[domain_id]

    def get_owner(
        self,
        domain_id: str,
    ) -> Optional[str]:

        return self.authority_map.get(
            domain_id
        )

    # ========================================================
    # ROUTE SEARCH
    # ========================================================

    def route_chain(
        self,
        start: str,
    ) -> List[str]:

        visited = set()

        chain = []

        def dfs(domain_id):

            if domain_id in visited:
                return

            visited.add(domain_id)

            chain.append(domain_id)

            for route in self.routes:

                if route.source == domain_id:
                    dfs(route.target)

        dfs(start)

        return chain

    # ========================================================
    # RECEIPT ROUTE
    # ========================================================

    def receipt_route(self):

        return self.route_chain(
            DOMAIN_RECEIPT_CACHE
        )

    # ========================================================
    # REPLAY ROUTE
    # ========================================================

    def replay_route(self):

        return self.route_chain(
            DOMAIN_REPLAY_ENGINE
        )

    # ========================================================
    # EXECUTION ROUTE
    # ========================================================

    def execution_route(self):

        return self.route_chain(
            DOMAIN_VM_RUNTIME
        )

    # ========================================================
    # VERIFY TOPOLOGY
    # ========================================================

    def verify_topology(self):

        required = [

            DOMAIN_VM_RUNTIME,
            DOMAIN_RECEIPT_CACHE,
            DOMAIN_GRAPH_KERNEL,
            DOMAIN_REPLAY_ENGINE,
        ]

        for r in required:

            if r not in self.domains:

                raise RuntimeError(
                    f"Missing domain: {r}"
                )

    # ========================================================
    # EXPORT
    # ========================================================

    def export_json(self):

        return {

            "domains": {

                k: {

                    "module":
                        v.module_name,

                    "authority":
                        v.authority_path,

                    "owner":
                        v.owner,

                    "permissions":
                        sorted(
                            list(v.permissions)
                        ),

                    "dependencies":
                        sorted(
                            list(v.dependencies)
                        ),

                    "receipt_domains":
                        sorted(
                            list(v.receipt_domains)
                        ),

                    "graph_domains":
                        sorted(
                            list(v.graph_domains)
                        ),

                    "replay_domains":
                        sorted(
                            list(v.replay_domains)
                        ),
                }

                for k, v
                in self.domains.items()
            },

            "routes": [

                {

                    "source":
                        r.source,

                    "target":
                        r.target,

                    "type":
                        r.route_type,
                }

                for r in self.routes
            ]
        }

# ============================================================
# DEFAULT REGISTRY
# ============================================================

def build_default_registry():

    reg = HHSRuntimeDomainRegistry()

    # ========================================================
    # VM RUNTIME
    # ========================================================

    reg.register_domain(

        HHSRuntimeDomain(

            domain_id=
                DOMAIN_VM_RUNTIME,

            module_name=
                "HARMONICODE_VM_RUNTIME",

            authority_path=
                "hhs_runtime/HARMONICODE_VM_RUNTIME.c",

            owner=
                "vm81",

            permissions={

                PERMISSION_EXECUTE,
                PERMISSION_ROUTE,
                PERMISSION_VERIFY,
            },

            receipt_domains={
                "hash72_runtime"
            },
        )
    )

    # ========================================================
    # RECEIPT CACHE
    # ========================================================

    reg.register_domain(

        HHSRuntimeDomain(

            domain_id=
                DOMAIN_RECEIPT_CACHE,

            module_name=
                "hhs_receipt_vector_cache_v1",

            authority_path=
                "hhs_runtime/python/hhs_receipt_vector_cache_v1.py",

            owner=
                "receipt_cache",

            permissions={

                PERMISSION_READ,
                PERMISSION_WRITE,
                PERMISSION_VERIFY,
            },

            receipt_domains={
                "hash72_runtime"
            },
        )
    )

    # ========================================================
    # GRAPH KERNEL
    # ========================================================

    reg.register_domain(

        HHSRuntimeDomain(

            domain_id=
                DOMAIN_GRAPH_KERNEL,

            module_name=
                "hhs_multimodal_graph_kernel_v1",

            authority_path=
                "hhs_runtime/python/hhs_multimodal_graph_kernel_v1.py",

            owner=
                "graph_kernel",

            permissions={

                PERMISSION_READ,
                PERMISSION_WRITE,
                PERMISSION_ROUTE,
            },

            graph_domains={
                "multimodal_graph"
            },
        )
    )

    # ========================================================
    # REPLAY
    # ========================================================

    reg.register_domain(

        HHSRuntimeDomain(

            domain_id=
                DOMAIN_REPLAY_ENGINE,

            module_name=
                "hhs_predictive_replay_engine_v1",

            authority_path=
                "hhs_runtime/python/hhs_predictive_replay_engine_v1.py",

            owner=
                "replay_engine",

            permissions={

                PERMISSION_REPLAY,
                PERMISSION_READ,
            },

            replay_domains={
                "predictive_execution"
            },
        )
    )

    # ========================================================
    # CONSENSUS
    # ========================================================

    reg.register_domain(

        HHSRuntimeDomain(

            domain_id=
                DOMAIN_CONSENSUS_ENGINE,

            module_name=
                "hhs_trace_consensus_engine_v1",

            authority_path=
                "hhs_runtime/python/hhs_trace_consensus_engine_v1.py",

            owner=
                "consensus_engine",

            permissions={

                PERMISSION_VERIFY,
                PERMISSION_ROUTE,
            },
        )
    )

    # ========================================================
    # MEMORY
    # ========================================================

    reg.register_domain(

        HHSRuntimeDomain(

            domain_id=
                DOMAIN_MEMORY_OVERLAY,

            module_name=
                "hhs_virtual_memory_overlay_v1",

            authority_path=
                "hhs_runtime/python/hhs_virtual_memory_overlay_v1.py",

            owner=
                "memory_overlay",

            permissions={

                PERMISSION_READ,
                PERMISSION_WRITE,
                PERMISSION_ROUTE,
            },
        )
    )

    # ========================================================
    # ROUTES
    # ========================================================

    reg.connect(

        DOMAIN_VM_RUNTIME,

        DOMAIN_RECEIPT_CACHE,

        "commit_receipt",
    )

    reg.connect(

        DOMAIN_RECEIPT_CACHE,

        DOMAIN_GRAPH_KERNEL,

        "index_receipt",
    )

    reg.connect(

        DOMAIN_GRAPH_KERNEL,

        DOMAIN_REPLAY_ENGINE,

        "predict_execution",
    )

    reg.connect(

        DOMAIN_REPLAY_ENGINE,

        DOMAIN_CONSENSUS_ENGINE,

        "consensus_vote",
    )

    reg.connect(

        DOMAIN_GRAPH_KERNEL,

        DOMAIN_MEMORY_OVERLAY,

        "virtual_projection",
    )

    reg.verify_topology()

    return reg

# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    import json

    registry = build_default_registry()

    print("\n=== EXECUTION ROUTE ===\n")

    for r in registry.execution_route():

        print(r)

    print("\n=== RECEIPT ROUTE ===\n")

    for r in registry.receipt_route():

        print(r)

    print("\n=== REPLAY ROUTE ===\n")

    for r in registry.replay_route():

        print(r)

    print("\n=== EXPORT ===\n")

    print(

        json.dumps(
            registry.export_json(),
            indent=2,
        )
    )