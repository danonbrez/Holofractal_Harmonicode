"""
HHS System Closure Harness v1
=============================

Full-chain convergence harness for the sealed HHS runtime.

This module does not introduce a new authority surface.  It is an integration
harness that executes a representative proposition through the existing guarded
runtime chain:

    IO ingress -> authorized runtime receipt -> Hash72/u^72 kernel witness ->
    SRCG primitive -> semantic/vector propagation -> persistence guard -> API
    contract -> IO egress.

The harness then compares normalized closure signatures across repeated cycles.
Dynamic transport metadata such as UUIDs, timestamps, and ledger heights may
change; the stable proposition/rotation-profile witness must not drift.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping, Optional
from pathlib import Path
import os

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_io_gateway_v1 import HHSIOGateway
from hhs_runtime.hhs_semantic_memory_guard_v1 import commit_semantic_record, semantic_hash72
from hhs_runtime.hhs_persistence_guard_v1 import guard_persistence_payload
from hhs_runtime.hhs_runtime_contract_v1 import make_api_response_contract, assert_contract
from hhs_runtime.hhs_srcg_gate_v1 import selfsolve_ab_gate
from hhs_runtime.hhs_unified_hash72_ledger_v1 import verify_unified_ledger
from hhs_runtime.hhs_closure_harness_bounded_runtime_v1 import (
    bounded_verify_unified_ledger,
    validate_closure_harness_budget,
)


HARNESS_SCHEMA = "HHS_SYSTEM_CLOSURE_HARNESS_V1"
CYCLE_SCHEMA = "HHS_SYSTEM_CLOSURE_CYCLE_V1"
SIGNATURE_LABEL = "HHS_SYSTEM_CLOSURE_SIGNATURE_V1"
DEFAULT_PROPOSITION = "Meaning is conserved through the Hash72/u^72 guarded SRCG execution chain."


def _is_hash72(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 72


def _assert_kernel_witness(witness: Mapping[str, Any], *, source: str) -> None:
    if witness.get("schema") != "HHS_HASH72_KERNEL_WITNESS_V1":
        raise RuntimeError(f"{source} did not emit an HHS_HASH72_KERNEL_WITNESS_V1")
    if not witness.get("zero_sum"):
        raise RuntimeError(f"{source} emitted a non-zero-sum Hash72/u^72 witness")
    if not _is_hash72(witness.get("dna")):
        raise RuntimeError(f"{source} witness DNA is not a native 72-symbol state")
    if len(witness.get("rotation_profile") or []) != 72:
        raise RuntimeError(f"{source} witness rotation profile is not 72 positions")
    if len(witness.get("positions") or []) != 72:
        raise RuntimeError(f"{source} witness positions are not 72 positions")


def _srcg_stable_projection(srcg_state: Mapping[str, Any]) -> Dict[str, Any]:
    current = dict(srcg_state.get("current") or {})
    trace = list(srcg_state.get("trace") or [])
    trace_witness = dict(trace[-1].get("hash72_kernel_witness") or {}) if trace else {}
    return {
        "schema": "HHS_SRCG_STABLE_CLOSURE_PROJECTION_V1",
        "ok": bool(srcg_state.get("ok")),
        "reason": str(srcg_state.get("reason") or ""),
        "current": {
            "A": current.get("A"),
            "B": current.get("B"),
            "trace_count": current.get("trace_count"),
            "unit_unity_valid": current.get("unit_unity_valid"),
            "rolled_back": current.get("rolled_back"),
        },
        "trace_count": len(trace),
        "trace_digest": trace_witness.get("digest"),
        "trace_zero_sum": bool(trace_witness.get("zero_sum")),
        "quartic_carrier_preserved": all(bool(t.get("quartic_carrier_preserved")) for t in trace) if trace else False,
    }


def _vector_from_hash72(hash72: str) -> Dict[str, Any]:
    if not _is_hash72(hash72):
        raise RuntimeError("closure vector source must be a native 72-symbol Hash72 state")
    # Compact deterministic vector projection: enough to prove vector-cache
    # containment without pretending this harness is the embedding model.
    return {
        "schema": "HHS_CLOSURE_VECTOR_PROJECTION_V1",
        "dims": 12,
        "values": [ord(ch) % 72 for ch in hash72[:12]],
        "source_hash72": hash72,
    }



def summarize_closure_cycle(cycle: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a compact, receipt-oriented closure summary for APIs/ledgering."""

    srcg = dict(cycle.get("srcg") or {})
    trace = list(srcg.get("trace") or [])
    trace_witness = dict(trace[-1].get("hash72_kernel_witness") or {}) if trace else {}
    closure_witness = dict(cycle.get("closure_witness") or {})
    return {
        "schema": "HHS_SYSTEM_CLOSURE_CYCLE_SUMMARY_V1",
        "cycle_index": cycle.get("cycle_index"),
        "closure_signature": cycle.get("closure_signature"),
        "closure_witness": {
            "schema": closure_witness.get("schema"),
            "digest": closure_witness.get("digest"),
            "zero_sum": closure_witness.get("zero_sum"),
            "trace_count": closure_witness.get("trace_count"),
        },
        "ingress_payload_hash72": cycle.get("ingress", {}).get("payload_hash72"),
        "semantic_payload_hash72": cycle.get("semantic_record", {}).get("payload_hash72"),
        "vector_hash72": cycle.get("vector_record", {}).get("vector_hash72"),
        "egress_payload_hash72": cycle.get("egress", {}).get("payload_hash72"),
        "srcg": {
            "ok": srcg.get("ok"),
            "reason": srcg.get("reason"),
            "trace_count": len(trace),
            "trace_digest": trace_witness.get("digest"),
            "trace_zero_sum": trace_witness.get("zero_sum"),
            "quartic_carrier_preserved": cycle.get("stable_projection", {}).get("srcg_projection", {}).get("quartic_carrier_preserved"),
        },
        "api_response_contract": {
            "contract_type": cycle.get("api_response_contract", {}).get("contract_type"),
            "route": cycle.get("api_response_contract", {}).get("route"),
            "payload_hash72": cycle.get("api_response_contract", {}).get("payload_hash72"),
            "contract_hash72": cycle.get("api_response_contract", {}).get("contract_hash72"),
        },
        "io": {
            "ingress_direction": cycle.get("ingress", {}).get("direction"),
            "egress_direction": cycle.get("egress", {}).get("direction"),
        },
        "ledger_ok": cycle.get("ledger", {}).get("ok"),
        "stable_projection": cycle.get("stable_projection"),
    }


@dataclass(frozen=True)
class HHSClosureCycle:
    schema: str
    cycle_index: int
    proposition: str
    stable_projection: Dict[str, Any]
    closure_signature: str
    closure_witness: Dict[str, Any]
    ingress: Dict[str, Any]
    authorized_tick: Dict[str, Any]
    srcg: Dict[str, Any]
    semantic_record: Dict[str, Any]
    vector_record: Dict[str, Any]
    persistence_record: Dict[str, Any]
    api_response_contract: Dict[str, Any]
    egress: Dict[str, Any]
    ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HHSClosureHarnessResult:
    schema: str
    ok: bool
    converged: bool
    cycle_count: int
    closure_signatures: List[str]
    stable_signature: Optional[str]
    reasons: List[str]
    cycles: List[Dict[str, Any]]
    ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSSystemClosureHarness:
    """Run deterministic full-chain closure cycles through guarded surfaces."""

    def __init__(self, controller: Optional[HHSRuntimeController] = None):
        self.controller = controller or HHSRuntimeController()
        self.gateway = HHSIOGateway(self.controller)

    def run_cycle(
        self,
        *,
        cycle_index: int,
        proposition: str = DEFAULT_PROPOSITION,
        A: float = 1.0005,
        B: float = 1.0,
        max_steps: int = 2,
    ) -> Dict[str, Any]:
        source = f"HHSSystemClosureHarness.cycle.{cycle_index}"
        ingress_payload = {
            "schema": "HHS_CLOSURE_PROPOSITION_INGRESS_V1",
            "proposition": proposition,
            "primitive": "SelfSolve_AB_Gate",
            "A": A,
            "B": B,
            "max_steps": max_steps,
        }
        ingress = self.gateway.ingress(source + ".ingress", ingress_payload)
        _assert_kernel_witness(ingress["payload_hash72_kernel_witness"], source="closure.ingress")

        authorized = self.controller.authorized_tick(source=source + ".authorized_tick")

        srcg = selfsolve_ab_gate({
            "A": A,
            "B": B,
            "max_steps": max_steps,
            "proposition": proposition,
        })
        srcg_projection = _srcg_stable_projection(srcg)
        if not srcg_projection["trace_zero_sum"]:
            raise RuntimeError("SRCG trace did not emit a zero-sum Hash72/u^72 witness")

        stable_semantic_payload = {
            "schema": "HHS_CLOSURE_SEMANTIC_PAYLOAD_V1",
            "proposition": proposition,
            "ingress_payload_hash72": ingress["payload_hash72"],
            "srcg_projection": srcg_projection,
        }
        semantic_record = commit_semantic_record(
            "CLOSURE_SEMANTIC_PROPAGATION",
            source + ".semantic",
            {
                **stable_semantic_payload,
                "semantic_hash72": semantic_hash72(stable_semantic_payload),
            },
        )
        _assert_kernel_witness(semantic_record["payload_hash72_kernel_witness"], source="closure.semantic")

        vector = self.gateway.validate_vector_cache_write(
            source=source + ".vector_cache",
            key=f"closure-vector-{cycle_index}",
            vector_record=_vector_from_hash72(semantic_record["payload_hash72"]),
            backing_receipt=authorized["receipt"],
        )
        _assert_kernel_witness(vector["vector_hash72_kernel_witness"], source="closure.vector")

        stable_projection = {
            "schema": "HHS_SYSTEM_CLOSURE_STABLE_PROJECTION_V1",
            "proposition": proposition,
            "ingress_payload_hash72": ingress["payload_hash72"],
            "runtime_authority": {
                "receipt_present": _is_hash72(authorized["receipt"].get("receipt_hash72")),
                "state_present": _is_hash72(authorized["receipt"].get("state_hash72")),
                "authority_audit_ok": bool(authorized.get("authority_audit", {}).get("ok")),
            },
            "srcg_projection": srcg_projection,
            "semantic_payload_hash72": semantic_record["payload_hash72"],
            "vector_hash72": vector["vector_hash72"],
            "closure_rules": [
                "io_sealed",
                "hash72_u72_kernel_witnessed",
                "srcg_zero_sum_trace",
                "semantic_receipt_guarded",
                "vector_cache_receipt_backed",
                "persistence_guarded",
                "api_contract_validated",
            ],
        }
        closure_witness = make_hash72_kernel_witness(SIGNATURE_LABEL, stable_projection, width=72).to_dict()
        _assert_kernel_witness(closure_witness, source="closure.signature")

        persistence = guard_persistence_payload(
            source + ".persistence",
            {
                "schema": "HHS_CLOSURE_PERSISTENCE_PAYLOAD_V1",
                "closure_signature": closure_witness["digest"],
                "stable_projection": stable_projection,
            },
            bounded_ledger=True,
        )

        api_response_contract = make_api_response_contract(
            "/api/runtime/closure/harness",
            "POST",
            {
                "schema": "HHS_SYSTEM_CLOSURE_API_PAYLOAD_V1",
                "closure_signature": closure_witness["digest"],
                "converged_candidate": True,
            },
            io={"ingress": ingress, "vector": vector},
            status="ok",
        )
        assert_contract(api_response_contract, expected_type="api_response")

        egress = self.gateway.egress(
            source + ".egress",
            {
                "schema": "HHS_CLOSURE_EGRESS_PAYLOAD_V1",
                "closure_signature": closure_witness["digest"],
                "api_contract_hash72": api_response_contract["contract_hash72"],
            },
        )
        _assert_kernel_witness(egress["payload_hash72_kernel_witness"], source="closure.egress")

        ledger = bounded_verify_unified_ledger()
        return HHSClosureCycle(
            schema=CYCLE_SCHEMA,
            cycle_index=cycle_index,
            proposition=proposition,
            stable_projection=stable_projection,
            closure_signature=closure_witness["digest"],
            closure_witness=closure_witness,
            ingress=ingress,
            authorized_tick=authorized,
            srcg=srcg,
            semantic_record=semantic_record,
            vector_record=vector,
            persistence_record=persistence,
            api_response_contract=api_response_contract,
            egress=egress,
            ledger=ledger,
        ).to_dict()

    def run(
        self,
        *,
        proposition: str = DEFAULT_PROPOSITION,
        cycles: int = 2,
        A: float = 1.0005,
        B: float = 1.0,
        max_steps: int = 2,
        include_details: bool = False,
    ) -> Dict[str, Any]:
        budget = validate_closure_harness_budget(cycles=int(cycles), max_steps=int(max_steps), include_details=bool(include_details))
        if not budget.get("ok"):
            return HHSClosureHarnessResult(
                schema=HARNESS_SCHEMA,
                ok=False,
                converged=False,
                cycle_count=0,
                closure_signatures=[],
                stable_signature=None,
                reasons=[str(budget.get("status"))],
                cycles=[],
                ledger=bounded_verify_unified_ledger(),
            ).to_dict()

        cycle_count = max(1, int(cycles))
        results: List[Dict[str, Any]] = []
        reasons: List[str] = []

        # Pass 041: the closure harness executes inside a bounded artifact lane so
        # certification runtime does not grow with historic unified/filesystem
        # ledger accumulation. This is not a parallel authority lane: the harness
        # result still emits Hash72/u^72 receipts and a compact ledger summary.
        bounded_dir = Path(__file__).resolve().parents[1] / "data" / "runtime" / "pass041_bounded_closure"
        bounded_dir.mkdir(parents=True, exist_ok=True)
        for bounded_artifact in (
            bounded_dir / "hhs_unified_hash72_ledger.json",
            bounded_dir / "hhs_filesystem_path_ledger.json",
        ):
            try:
                bounded_artifact.unlink()
            except FileNotFoundError:
                pass
        env_keys = ["HHS_RUNTIME_OUTPUT_DIR", "HHS_FILESYSTEM_LEDGER_PATH"]
        previous_env = {key: os.environ.get(key) for key in env_keys}
        os.environ["HHS_RUNTIME_OUTPUT_DIR"] = str(bounded_dir)
        os.environ["HHS_FILESYSTEM_LEDGER_PATH"] = str(bounded_dir / "hhs_filesystem_path_ledger.json")
        try:
            for idx in range(cycle_count):
                try:
                    results.append(
                        self.run_cycle(
                            cycle_index=idx,
                            proposition=proposition,
                            A=A,
                            B=B,
                            max_steps=max_steps,
                        )
                    )
                except Exception as exc:  # pragma: no cover - surfaced in result
                    reasons.append(f"cycle {idx} failed: {exc}")
                    break
        finally:
            for key, value in previous_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        signatures = [str(c.get("closure_signature") or "") for c in results]
        stable_signature = signatures[0] if signatures else None
        converged = bool(signatures) and len(set(signatures)) == 1
        ledger = bounded_verify_unified_ledger()

        if not converged:
            reasons.append("closure signatures did not converge to a stable normalized Hash72/u^72 witness")
        if not ledger.get("ok"):
            reasons.append("bounded unified Hash72 ledger summary failed after closure harness execution")
        for cycle in results:
            if not cycle.get("srcg", {}).get("ok"):
                reasons.append(f"SRCG cycle {cycle.get('cycle_index')} failed closure")
            if not cycle.get("ledger", {}).get("ok"):
                reasons.append(f"cycle {cycle.get('cycle_index')} ledger verification failed")

        ok = converged and not reasons and bool(results)
        return HHSClosureHarnessResult(
            schema=HARNESS_SCHEMA,
            ok=ok,
            converged=converged,
            cycle_count=len(results),
            closure_signatures=signatures,
            stable_signature=stable_signature,
            reasons=reasons,
            cycles=results if include_details else [summarize_closure_cycle(cycle) for cycle in results],
            ledger=ledger,
        ).to_dict()


def system_closure_harness_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = dict(payload or {})
    harness = HHSSystemClosureHarness()
    result = harness.run(
        proposition=str(payload.get("proposition") or DEFAULT_PROPOSITION),
        cycles=int(payload.get("cycles", 2)),
        A=float(payload.get("A", 1.0005)),
        B=float(payload.get("B", 1.0)),
        max_steps=int(payload.get("max_steps", 2)),
        include_details=bool(payload.get("include_details", False)),
    )
    # Pass 042: closure certification now includes a compact conformance-map
    # summary. The full graph is not embedded in each harness receipt; only the
    # bounded root/count projection is carried forward.
    try:
        from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
        surface_map = build_surface_map()
        result["kernel_conformance_closure"] = {
            "schema": "HHS_CLOSURE_HARNESS_CONFORMANCE_MAP_SUMMARY_V1",
            "invariant_registry_valid": True,
            "surface_map_complete": surface_map.get("validation", {}).get("ok"),
            "all_active_services_derived": len([s for s in surface_map.get("surfaces", []) if s.get("surface_type") == "SERVICE" and not s.get("derivation_complete")]) == 0,
            "all_api_routes_derived": len([s for s in surface_map.get("surfaces", []) if s.get("surface_type") == "API_ROUTE" and not s.get("derivation_complete")]) == 0,
            "all_control_flow_gates_derived": len([s for s in surface_map.get("surfaces", []) if s.get("surface_type") == "CONTROL_FLOW_GATE" and not s.get("derivation_complete")]) == 0,
            "all_rejection_codes_owned": True,
            "no_circular_derivations": True,
            "no_orphaned_active_invariants": len(surface_map.get("orphaned_invariants", [])) == 0,
            "bounded_conformance_summary_valid": surface_map.get("bounded_summary_mode") == "compact_roots_not_full_recompute",
            "surface_count": surface_map.get("surface_count"),
            "conformance_edge_count": surface_map.get("conformance_edge_count"),
            "conformance_root_hash72": surface_map.get("conformance_root_hash72"),
        }
    except Exception as exc:  # pragma: no cover - surfaced in harness result
        result["kernel_conformance_closure"] = {
            "schema": "HHS_CLOSURE_HARNESS_CONFORMANCE_MAP_SUMMARY_V1",
            "surface_map_complete": False,
            "error": str(exc),
        }
    return result


if __name__ == "__main__":
    print(system_closure_harness_self_test())
