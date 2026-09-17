"""Pass 219 Lane 5 mandatory optimization dispatcher.

This module is the production composition/search entry point for the proven
Lane 5 optimization lineage.  It deliberately preserves the old
``search_hash216`` protocol so older callers keep working, but it no longer
binds that protocol directly to the 1.37 optimizer.

The dispatcher distinguishes three things that must not be conflated:

* stateless Hash216 ranking (1.37), where no exact parent VM5184 state is
  available and therefore persistent route reuse is not applicable;
* stateful composition routing (1.38 -> 1.42), where exact persistent jumps,
  recursive paths and promoted superedges are searched before any fresh path;
* exact route/composition certificate reuse (RML19), which is a separately
  typed conservation cache and never becomes canonical transition authority.

All optimized results remain candidate-only and still require the inherited
signed environmental VM81 admission boundary for canonical mutation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    Pass219Lane5Hash216GPUPhaseInterlaceOptimizer,
)
from hhs_backend.runtime.hhs_pass219_lane5_automatic_superedge_routing_1_42 import (
    Pass219Lane5AutomaticSuperedgeRouter,
)
from hhs_backend.runtime.hhs_pass219_lane5_executable_capability_self_model_1_43 import (
    build_capability_self_model,
)
from hhs_backend.runtime.hhs_pass219_lane5_repository_capability_reverse_discovery_1_44 import (
    build_repository_capability_reverse_discovery,
)
from hhs_runtime.pass219 import rml19_route_composition_conservation_acceleration as rml19

SCHEMA = "HHS_PASS219_LANE5_MANDATORY_OPTIMIZATION_DISPATCHER_V1"

# Ordered by dependency.  These are not claims that every surface applies to
# every request; they are the proven optimization/capability lineage that must
# remain reachable from the default Lane 5 production dispatcher.
MANDATORY_LANE5_LINEAGE = (
    "LANE5_HASH216_GPU_PHASE_INTERLACE_1_37",
    "LANE5_HASH216_COMPOSITION_JUMP_STORE_1_38",
    "LANE5_PERSISTENT_HASH216_COMPOSITION_MEMORY_1_39",
    "LANE5_RECURSIVE_HASH216_COMPOSITION_GRAPH_1_40",
    "LANE5_SUPEREDGE_HIERARCHY_1_41",
    "LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42",
    "LANE5_EXECUTABLE_CAPABILITY_SELF_MODEL_1_43",
    "LANE5_REPOSITORY_CAPABILITY_REVERSE_DISCOVERY_1_44",
    "HASH216_FRACTAL_QUDIT_ADMISSION_1_45",
    "LANE5_DIRECT_WITNESS_ROUTING_1_46",
    "LANE5_UNBOUNDED_WORKLOAD_SCALING_1_48",
    "RML19_ROUTE_COMPOSITION_CERTIFICATE_REUSE",
)


class Lane5MandatoryOptimizationError(RuntimeError):
    """Fail-closed mandatory optimization integration error."""


class Pass219Lane5MandatoryOptimizationDispatcher:
    """Compatibility search API plus exact stateful composition fast paths."""

    def __init__(
        self,
        *,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
        state_root: str | Path | None = None,
        vector_key: bytes | None = None,
    ) -> None:
        self.backend = str(backend)
        self.require_physical_gpu = bool(require_physical_gpu)
        self.state_root = Path(state_root).resolve() if state_root is not None else None
        self._ranker = Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(
            backend=self.backend,
            require_physical_gpu=self.require_physical_gpu,
        )
        self._router: Pass219Lane5AutomaticSuperedgeRouter | None = None
        if self.state_root is not None:
            self._router = Pass219Lane5AutomaticSuperedgeRouter(
                self.state_root,
                vector_key=vector_key,
                backend=self.backend,
                require_physical_gpu=self.require_physical_gpu,
            )

    def __enter__(self) -> "Pass219Lane5MandatoryOptimizationDispatcher":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        if self._router is not None:
            self._router.close()
            self._router = None
        self._ranker.close()

    @staticmethod
    def _authority_record() -> dict[str, bool]:
        return {
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "floating_point_canonical_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def status(self) -> dict[str, Any]:
        ranker = self._ranker.status()
        router = self._router.status() if self._router is not None else None
        return {
            "schema": SCHEMA,
            "mandatory_optimization_dispatch": True,
            "default_stateless_ranker": "LANE5_HASH216_GPU_PHASE_INTERLACE_1_37",
            "default_stateful_router": "LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42",
            "mandatory_lineage": list(MANDATORY_LANE5_LINEAGE),
            "stateless_ranker_ready": True,
            "stateful_composition_ready": router is not None,
            "stateful_composition_requires_state_root": True,
            "rml19_exact_certificate_reuse_ready": True,
            "ranker": ranker,
            "router": router,
            "authority": self._authority_record(),
        }

    def capability_snapshot(self) -> dict[str, Any]:
        """Build the repository-derived capability model through 1.44.

        This is intentionally explicit/lazy because capability discovery scans
        repository surfaces.  Its result is evidence for reachability, not a
        replacement execution authority.
        """
        self_model = build_capability_self_model()
        reverse = build_repository_capability_reverse_discovery()
        if self_model.get("canonical_boundary_export") != (
            "hhs_exact_pass219_vm81_environment_admit_signed"
        ):
            raise Lane5MandatoryOptimizationError("LANE5_CANONICAL_BOUNDARY_DRIFT")
        if reverse.get("canonical_boundary_export") != self_model.get(
            "canonical_boundary_export"
        ):
            raise Lane5MandatoryOptimizationError("LANE5_DISCOVERY_BOUNDARY_DRIFT")
        return {
            "schema": SCHEMA,
            "capability_self_model": self_model,
            "repository_reverse_discovery": reverse,
            "mandatory_lineage": list(MANDATORY_LANE5_LINEAGE),
            "authority": self._authority_record(),
        }

    def search_hash216(
        self,
        *,
        query_hash216: str,
        candidates: Sequence[Any],
        tick: int,
        cycle_index: int,
        top_k: int = 32,
    ) -> dict[str, Any]:
        """Stateless compatibility search with an explicit dispatch receipt.

        Persistent route/superedge reuse is not silently attempted here because
        this protocol does not carry the exact parent VM5184 state needed to
        prove a reusable route's parent identity.  The stateful fast path is
        ``compose_or_reuse`` below.
        """
        canonical: list[Hash216CompositionCandidate] = []
        for raw in candidates:
            if isinstance(raw, Hash216CompositionCandidate):
                canonical.append(raw)
                continue
            canonical.append(
                Hash216CompositionCandidate(
                    candidate_id=str(raw.candidate_id),
                    hash216=str(raw.hash216),
                    validated=bool(raw.validated),
                    jump_span=int(getattr(raw, "jump_span", 1)),
                    lineage_signature=str(getattr(raw, "lineage_signature", "")),
                )
            )
        result = self._ranker.search_hash216(
            query_hash216=query_hash216,
            candidates=canonical,
            tick=int(tick),
            cycle_index=int(cycle_index),
            top_k=int(top_k),
        )
        result["mandatory_optimization_dispatch"] = True
        result["optimization_selected"] = "LANE5_HASH216_GPU_PHASE_INTERLACE_1_37"
        result["optimization_available"] = list(MANDATORY_LANE5_LINEAGE)
        result["optimization_inapplicable_without_exact_parent_state"] = [
            "LANE5_HASH216_COMPOSITION_JUMP_STORE_1_38",
            "LANE5_PERSISTENT_HASH216_COMPOSITION_MEMORY_1_39",
            "LANE5_RECURSIVE_HASH216_COMPOSITION_GRAPH_1_40",
            "LANE5_SUPEREDGE_HIERARCHY_1_41",
            "LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42",
        ]
        result["fresh_recomputation_forced"] = False
        return result

    def compose_or_reuse(
        self,
        *,
        current_state: Sequence[int],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
        max_retrievals: int = 8,
        layer_index: int | None = None,
        fallback_candidates: Sequence[Any] = (),
        fallback_top_k: int = 32,
    ) -> dict[str, Any]:
        """Search exact persistent composition memory before fresh ranking.

        1.42 is the accumulated stateful router and therefore transitively
        exposes 1.38 jump reuse, 1.39 restart-persistent memory, 1.40 recursive
        graph search and 1.41 promoted superedges.  A found plan is executed via
        the inherited exact candidate-reuse validators and returns without
        replaying represented intermediate VM81 transitions.
        """
        if self._router is None:
            raise Lane5MandatoryOptimizationError(
                "LANE5_STATEFUL_OPTIMIZATION_REQUIRES_STATE_ROOT"
            )
        plan = self._router.plan_route(
            current_state=current_state,
            goal_hash216=goal_hash216,
            tick=int(tick),
            cycle_index=int(cycle_index),
            max_retrievals=int(max_retrievals),
            layer_index=layer_index,
        )
        if bool(plan.get("found")) and bool(plan.get("exact_target")):
            reused = self._router.execute_plan(
                current_state=current_state,
                plan=plan,
            )
            if int(reused.get("intermediate_vm81_transitions_executed", -1)) != 0:
                raise Lane5MandatoryOptimizationError(
                    "LANE5_OPTIMIZED_ROUTE_REEXECUTED_INTERMEDIATE_VM81"
                )
            return {
                "schema": SCHEMA,
                "mode": "STATEFUL_EXACT_REUSE",
                "optimization_selected": "LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42",
                "optimization_transitive_lineage": [
                    "LANE5_HASH216_COMPOSITION_JUMP_STORE_1_38",
                    "LANE5_PERSISTENT_HASH216_COMPOSITION_MEMORY_1_39",
                    "LANE5_RECURSIVE_HASH216_COMPOSITION_GRAPH_1_40",
                    "LANE5_SUPEREDGE_HIERARCHY_1_41",
                    "LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42",
                ],
                "plan": plan,
                "reuse": reused,
                "represented_transitions": int(reused["represented_transitions"]),
                "intermediate_vm81_transitions_executed": 0,
                "fresh_recomputation_forced": False,
                "authority": self._authority_record(),
            }

        fallback = self.search_hash216(
            query_hash216=goal_hash216,
            candidates=fallback_candidates,
            tick=int(tick),
            cycle_index=int(cycle_index),
            top_k=int(fallback_top_k),
        )
        return {
            "schema": SCHEMA,
            "mode": "NO_EXACT_REUSABLE_ROUTE_FALLBACK_RANKING",
            "optimization_selected": fallback["optimization_selected"],
            "exact_reuse_found": False,
            "plan": plan,
            "fallback": fallback,
            "fresh_recomputation_forced": False,
            "authority": self._authority_record(),
        }

    @staticmethod
    def gate_route_candidate(
        source: Mapping[str, Any],
        target: Mapping[str, Any],
        *,
        route_id: str,
    ) -> dict[str, Any]:
        result = rml19.gate_route_candidate(source, target, route_id=route_id)
        result = dict(result)
        result["mandatory_optimization_dispatch"] = True
        result["optimization_selected"] = "RML19_ROUTE_COMPOSITION_CERTIFICATE_REUSE"
        return result

    @staticmethod
    def gate_composed_route_candidate(
        states: Sequence[Mapping[str, Any]],
        *,
        composition_id: str,
    ) -> dict[str, Any]:
        result = rml19.gate_composed_route_candidate(
            states,
            composition_id=composition_id,
        )
        result = dict(result)
        result["mandatory_optimization_dispatch"] = True
        result["optimization_selected"] = "RML19_ROUTE_COMPOSITION_CERTIFICATE_REUSE"
        return result


__all__ = [
    "Lane5MandatoryOptimizationError",
    "MANDATORY_LANE5_LINEAGE",
    "Pass219Lane5MandatoryOptimizationDispatcher",
    "SCHEMA",
]
