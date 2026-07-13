"""
HHS Kernel Invariant Registry v1
=================================

Pass 042 executable registry of kernel invariants.  This module is deliberately
small and deterministic: invariants are not comments attached to services; they
are first-class records that own witnesses, validators, rejection codes, and the
runtime domains they derive.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION = "PASS_042_KERNEL_DERIVED_CONFORMANCE_SURFACE_MAP_V1"
REGISTRY_SCHEMA = "HHS_KERNEL_INVARIANT_REGISTRY_V1"
INVARIANT_SCHEMA = "HHS_KERNEL_INVARIANT_RECORD_V1"
HASH72_AUTHORITY = "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"

ADMIT_KERNEL_INVARIANT_REGISTRY = "ADMIT_KERNEL_INVARIANT_REGISTRY"
REJECT_DUPLICATE_INVARIANT = "REJECT_DUPLICATE_INVARIANT"
REJECT_UNKNOWN_INVARIANT_DEPENDENCY = "REJECT_UNKNOWN_INVARIANT_DEPENDENCY"
REJECT_CIRCULAR_DERIVATION = "REJECT_CIRCULAR_DERIVATION"
REJECT_AMBIGUOUS_INVARIANT_OWNERSHIP = "REJECT_AMBIGUOUS_INVARIANT_OWNERSHIP"
REJECT_MISSING_INVARIANT_WITNESS_REQUIREMENT = "REJECT_MISSING_INVARIANT_WITNESS_REQUIREMENT"
REJECT_MISSING_INVARIANT_VALIDATOR = "REJECT_MISSING_INVARIANT_VALIDATOR"
REJECT_MISSING_INVARIANT_REJECTION_CODE = "REJECT_MISSING_INVARIANT_REJECTION_CODE"


@dataclass(frozen=True)
class HHSKernelInvariant:
    schema: str
    invariant_id: str
    name: str
    statement: str
    domain: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    required_witnesses: List[str] = field(default_factory=list)
    required_validators: List[str] = field(default_factory=list)
    rejection_codes: List[str] = field(default_factory=list)
    kernel_authority: str = HASH72_AUTHORITY

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _normalize_list(values: Optional[Iterable[Any]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        text = str(value).strip()
        if text:
            out.append(text)
    return sorted(dict.fromkeys(out))


def _hash72(label: str, payload: Any, *, width: int = 72) -> str:
    return make_hash72_kernel_witness(label, payload, width=width).digest


def _canonical_invariant(record: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "schema": INVARIANT_SCHEMA,
        "invariant_id": str(record.get("invariant_id", "")).strip(),
        "name": str(record.get("name", "")).strip(),
        "statement": str(record.get("statement", "")).strip(),
        "domain": _normalize_list(record.get("domain", [])),
        "depends_on": _normalize_list(record.get("depends_on", [])),
        "required_witnesses": _normalize_list(record.get("required_witnesses", [])),
        "required_validators": _normalize_list(record.get("required_validators", [])),
        "rejection_codes": _normalize_list(record.get("rejection_codes", [])),
        "kernel_authority": str(record.get("kernel_authority") or HASH72_AUTHORITY),
    }


class HHSInvariantRegistryError(RuntimeError):
    pass


class HHSKernelInvariantRegistry:
    def __init__(self):
        self._invariants: Dict[str, HHSKernelInvariant] = {}
        self._name_owners: Dict[str, str] = {}
        self._validator_owners: Dict[str, str] = {}
        self._rejection_owners: Dict[str, str] = {}

    def register_invariant(self, invariant: Mapping[str, Any]) -> HHSKernelInvariant:
        data = _canonical_invariant(invariant)
        invariant_id = data["invariant_id"]
        if not invariant_id:
            raise HHSInvariantRegistryError("invariant_id is required")
        existing = self._invariants.get(invariant_id)
        if existing:
            if existing.to_dict() != data:
                raise HHSInvariantRegistryError(REJECT_DUPLICATE_INVARIANT)
            return existing
        name = data["name"]
        if name in self._name_owners and self._name_owners[name] != invariant_id:
            raise HHSInvariantRegistryError(REJECT_AMBIGUOUS_INVARIANT_OWNERSHIP)
        if not data["required_witnesses"]:
            raise HHSInvariantRegistryError(REJECT_MISSING_INVARIANT_WITNESS_REQUIREMENT)
        if not data["required_validators"]:
            raise HHSInvariantRegistryError(REJECT_MISSING_INVARIANT_VALIDATOR)
        if not data["rejection_codes"]:
            raise HHSInvariantRegistryError(REJECT_MISSING_INVARIANT_REJECTION_CODE)
        record = HHSKernelInvariant(**data)
        self._invariants[invariant_id] = record
        self._name_owners[name] = invariant_id
        for validator in record.required_validators:
            self._validator_owners.setdefault(validator, invariant_id)
        for code in record.rejection_codes:
            self._rejection_owners.setdefault(code, invariant_id)
        return record

    def get_invariant(self, invariant_id: str) -> Dict[str, Any]:
        return self._invariants[str(invariant_id)].to_dict()

    def list_invariants(self) -> List[Dict[str, Any]]:
        return [self._invariants[k].to_dict() for k in sorted(self._invariants)]

    def lookup(self, *, service: str = "", schema: str = "", validator: str = "", rejection_code: str = "", runtime_surface: str = "") -> List[Dict[str, Any]]:
        terms = {str(x).lower() for x in [service, schema, validator, rejection_code, runtime_surface] if str(x).strip()}
        out: List[Dict[str, Any]] = []
        for inv in self.list_invariants():
            blob = json.dumps(inv, sort_keys=True).lower()
            if any(term in blob for term in terms):
                out.append(inv)
        return out

    def resolve_invariant_dependencies(self, invariant_id: str) -> List[str]:
        seen: Set[str] = set()
        visiting: Set[str] = set()
        order: List[str] = []

        def visit(iid: str) -> None:
            if iid not in self._invariants:
                raise HHSInvariantRegistryError(REJECT_UNKNOWN_INVARIANT_DEPENDENCY)
            if iid in visiting:
                raise HHSInvariantRegistryError(REJECT_CIRCULAR_DERIVATION)
            if iid in seen:
                return
            visiting.add(iid)
            for dep in self._invariants[iid].depends_on:
                visit(dep)
            visiting.remove(iid)
            seen.add(iid)
            order.append(iid)

        visit(str(invariant_id))
        return order

    def validate_invariant_registry(self) -> Dict[str, Any]:
        reasons: List[str] = []
        for inv in self._invariants.values():
            for dep in inv.depends_on:
                if dep not in self._invariants:
                    reasons.append(f"{inv.invariant_id} depends on unknown {dep}")
            try:
                self.resolve_invariant_dependencies(inv.invariant_id)
            except HHSInvariantRegistryError as exc:
                reasons.append(f"{inv.invariant_id}: {exc}")
            if not inv.required_witnesses:
                reasons.append(f"{inv.invariant_id} has no witness requirement")
            if not inv.required_validators:
                reasons.append(f"{inv.invariant_id} has no validator")
            if not inv.rejection_codes:
                reasons.append(f"{inv.invariant_id} has no rejection code")
        witness = self.build_invariant_registry_witness()
        return {
            "schema": "HHS_KERNEL_INVARIANT_REGISTRY_DECISION_V1",
            "ok": not reasons,
            "status": ADMIT_KERNEL_INVARIANT_REGISTRY if not reasons else "REJECT_INVALID_KERNEL_INVARIANT_REGISTRY",
            "invariant_count": len(self._invariants),
            "reasons": reasons,
            "registry_root_hash72": witness["registry_root_hash72"],
            "hash72_kernel_witness": witness["hash72_kernel_witness"],
        }

    def build_invariant_registry_witness(self) -> Dict[str, Any]:
        payload = {
            "schema": REGISTRY_SCHEMA,
            "version": VERSION,
            "invariants": self.list_invariants(),
        }
        witness = make_hash72_kernel_witness("HHS_KERNEL_INVARIANT_REGISTRY_V1", payload, width=72)
        return {
            "schema": "HHS_KERNEL_INVARIANT_REGISTRY_WITNESS_V1",
            "version": VERSION,
            "registry_root_hash72": witness.digest,
            "hash72_kernel_witness": witness.to_dict(),
        }


INVARIANT_SEED: List[Dict[str, Any]] = [
    {
        "invariant_id": "HHS-I001",
        "name": "Meaning Conservation",
        "statement": "Every admitted transformation preserves declared semantic identity across pre-state and post-state.",
        "domain": ["runtime_contracts", "control_flow", "plugin_execution", "carrier_reconstruction"],
        "depends_on": [],
        "required_witnesses": ["HHS_MEANING_CONSERVATION_WITNESS_V1"],
        "required_validators": ["validate_meaning_conservation"],
        "rejection_codes": ["REJECT_MEANING_NOT_CONSERVED"],
    },
    {
        "invariant_id": "HHS-I002",
        "name": "Hash72/u^72 witness authority",
        "statement": "Every canonical state, transition, contract, receipt, and derivation has a kernel-authorized witness.",
        "domain": ["hash72", "receipts", "contracts", "derivations"],
        "depends_on": [],
        "required_witnesses": ["HHS_HASH72_KERNEL_WITNESS_V1"],
        "required_validators": ["validate_hash72_kernel_authority"],
        "rejection_codes": ["REJECT_HASH72_AUTHORITY_MISSING"],
    },
    {
        "invariant_id": "HHS-I003",
        "name": "Full-state transition integrity",
        "statement": "Control-flow decisions operate on complete pre-state, result, and post-state transitions rather than scalar proxies.",
        "domain": ["control_flow", "runtime_transitions"],
        "depends_on": ["HHS-I001", "HHS-I002"],
        "required_witnesses": ["HHS_CONTROL_FLOW_TRANSITION_WITNESS_V1"],
        "required_validators": ["validate_control_flow_transition_audit"],
        "rejection_codes": ["REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY"],
    },
    {
        "invariant_id": "HHS-I004",
        "name": "Bounded recursive closure",
        "statement": "Certification, validation, and recursive execution remain inside declared step, cycle, ledger, and artifact budgets.",
        "domain": ["closure_harness", "validation", "recursive_execution"],
        "depends_on": ["HHS-I002"],
        "required_witnesses": ["HHS_BOUNDED_CLOSURE_WITNESS_V1"],
        "required_validators": ["validate_bounded_recursive_closure"],
        "rejection_codes": ["REJECT_UNBOUNDED_RECURSIVE_CLOSURE"],
    },
    {
        "invariant_id": "HHS-I005",
        "name": "Guarded execution path",
        "statement": "No runtime execution bypasses the declared contract, guard, adapter, authority, and receipt chain.",
        "domain": ["service_dispatch", "api", "plugin_execution", "authorized_execution"],
        "depends_on": ["HHS-I002"],
        "required_witnesses": ["HHS_GUARDED_EXECUTION_WITNESS_V1"],
        "required_validators": ["validate_guarded_execution_path"],
        "rejection_codes": ["REJECT_GUARDED_EXECUTION_BYPASS"],
    },
    {
        "invariant_id": "HHS-I006",
        "name": "Ledger continuity",
        "statement": "Every committed state mutation has a canonical parent, receipt, ledger entry, and tip transition.",
        "domain": ["ledger", "persistence", "state_mutation"],
        "depends_on": ["HHS-I002"],
        "required_witnesses": ["HHS_LEDGER_CONTINUITY_WITNESS_V1"],
        "required_validators": ["validate_ledger_continuity"],
        "rejection_codes": ["REJECT_LEDGER_CONTINUITY_BROKEN"],
    },
    {
        "invariant_id": "HHS-I007",
        "name": "Validation residue compression",
        "statement": "Validation history is preserved as compressed witness chains rather than unbounded artifact replication.",
        "domain": ["validation", "closure_harness", "control_flow", "carrier_reconstruction"],
        "depends_on": ["HHS-I002", "HHS-I004"],
        "required_witnesses": ["HHS_VALIDATION_RESIDUE_RECEIPT_V1"],
        "required_validators": ["validate_validation_residue_compression"],
        "rejection_codes": ["REJECT_VALIDATION_RESIDUE_RAW_CACHE_RETAINED"],
    },
    {
        "invariant_id": "HHS-I008",
        "name": "Canonical representation",
        "statement": "Every runtime object has one declared canonical schema and deterministic serialization path.",
        "domain": ["contracts", "schemas", "serialization", "witnesses"],
        "depends_on": ["HHS-I002"],
        "required_witnesses": ["HHS_CANONICAL_REPRESENTATION_WITNESS_V1"],
        "required_validators": ["validate_canonical_representation"],
        "rejection_codes": ["REJECT_NONCANONICAL_REPRESENTATION"],
    },
    {
        "invariant_id": "HHS-I009",
        "name": "No hidden parallel archive",
        "statement": "Carrier enhancement may preserve provenance and transformation history but cannot create undeclared duplicate payload lanes.",
        "domain": ["carrier_archive", "hhfs", "udfp"],
        "depends_on": ["HHS-I008"],
        "required_witnesses": ["HHS_HHFS_NO_PARALLEL_LANE_WITNESS_V1"],
        "required_validators": ["validate_no_hidden_parallel_archive"],
        "rejection_codes": ["REJECT_HHFS_PARALLEL_STORAGE_LANE"],
    },
    {
        "invariant_id": "HHS-I010",
        "name": "Reconstruction reversibility",
        "statement": "Every admitted reconstruction path declares sufficient witness information to recover or verify the canonical represented state.",
        "domain": ["reconstruction", "carrier_archive", "ecc"],
        "depends_on": ["HHS-I002", "HHS-I009"],
        "required_witnesses": ["HHS_RECONSTRUCTION_WITNESS_V1"],
        "required_validators": ["validate_reconstruction_reversibility"],
        "rejection_codes": ["REJECT_RECONSTRUCTION_REJECTED_WITNESS_CORRUPTED"],
    },
    {
        "invariant_id": "HHS-I011",
        "name": "Invariant-derived admissibility",
        "statement": "Admission and rejection decisions derive from kernel invariants rather than local arbitrary policy.",
        "domain": ["admissibility", "conformance", "runtime_decision"],
        "depends_on": ["HHS-I002"],
        "required_witnesses": ["HHS_KERNEL_DERIVATION_WITNESS_V1"],
        "required_validators": ["validate_invariant_derived_admissibility"],
        "rejection_codes": ["REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT"],
    },
    {
        "invariant_id": "HHS-I012",
        "name": "Zero-bypass prohibition",
        "statement": "No service, API, executor, adapter, or control-flow gate may bypass required authority or conformance stages.",
        "domain": ["zero_bypass", "service_dispatch", "api", "execution"],
        "depends_on": ["HHS-I005", "HHS-I011"],
        "required_witnesses": ["HHS_ZERO_BYPASS_INTERPOSITION_WITNESS_V1"],
        "required_validators": ["validate_zero_bypass_prohibition"],
        "rejection_codes": ["REJECTED_MISSING_INTERPOSITION_DECISION"],
    },
    {
        "invariant_id": "HHS-I013",
        "name": "Explicit mutation ownership",
        "statement": "Every state mutation declares its owning surface, persistence policy, rollback behavior, and ledger effect.",
        "domain": ["mutation", "persistence", "rollback", "ledger"],
        "depends_on": ["HHS-I006", "HHS-I011"],
        "required_witnesses": ["HHS_MUTATION_OWNERSHIP_WITNESS_V1"],
        "required_validators": ["validate_explicit_mutation_ownership"],
        "rejection_codes": ["REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY"],
    },
    {
        "invariant_id": "HHS-I014",
        "name": "Surface reachability closure",
        "statement": "Every executable surface must be boot-, service-, API-, or control-flow reachable through a declared canonical path.",
        "domain": ["reachability", "service_registry", "api", "gui"],
        "depends_on": ["HHS-I011", "HHS-I012"],
        "required_witnesses": ["HHS_SURFACE_REACHABILITY_WITNESS_V1"],
        "required_validators": ["validate_surface_reachability_closure"],
        "rejection_codes": ["REJECT_UNDERIVED_RUNTIME_SURFACE"],
    },
    {
        "invariant_id": "HHS-I015",
        "name": "Self-consistent derivation closure",
        "statement": "The conformance map itself must be kernel-derived, witnessed, bounded, and included in the closure harness.",
        "domain": ["conformance", "closure_harness", "surface_map"],
        "depends_on": ["HHS-I004", "HHS-I011", "HHS-I014"],
        "required_witnesses": ["HHS_KERNEL_CONFORMANCE_MAP_WITNESS_V1"],
        "required_validators": ["validate_self_consistent_derivation_closure"],
        "rejection_codes": ["REJECT_CONFORMANCE_MAP_NOT_SELF_DERIVED"],
    },
    {
        "invariant_id": "HHS-I016",
        "name": "Expanded state decay",
        "statement": "Every expanded validation, derivation, reconstruction, or execution-preflight state has a bounded decay lifecycle and either propagates to a new witnessed Hash72/u^72 state or self-deletes with a compact decay witness.",
        "domain": ["metadata_lifecycle", "validation", "autocomposition", "performance", "decay"],
        "depends_on": ["HHS-I002", "HHS-I007", "HHS-I011"],
        "required_witnesses": ["HHS_EXPANDED_STATE_DECAY_RECORD_V1", "HHS_COMPACT_CONFORMANCE_RESIDUE_V1"],
        "required_validators": ["validate_expanded_state_decay_lifecycle", "validate_bounded_metadata_lifecycle"],
        "rejection_codes": ["REJECT_EXPIRED_EXPANDED_STATE", "REJECT_UNBOUNDED_EXPANDED_STATE_LIFETIME"],
    },
    {
        "invariant_id": "HHS-I017",
        "name": "Runtime canonical observer boundary",
        "statement": "Only Runtime-admitted identity may enter canonical HHS state; interfaces, providers, projections, and translations are request/observation/projection surfaces, not canonical authorities.",
        "domain": ["runtime_observer", "capability_provider", "interface_projection", "modality_translation"],
        "depends_on": ["HHS-I001", "HHS-I002", "HHS-I008", "HHS-I011", "HHS-I012", "HHS-I014"],
        "required_witnesses": ["HHS_RUNTIME_OBSERVATION_RECORD_V1", "HHS_RUNTIME_CANONICAL_IDENTITY_ADMISSION_V1"],
        "required_validators": ["validate_runtime_canonical_observer_boundary", "validate_provider_noncanonical_ingress"],
        "rejection_codes": ["REJECT_INTERFACE_AS_CANONICAL_AUTHORITY", "REJECT_PROVIDER_AS_CANONICAL_AUTHORITY", "REJECT_PROJECTION_AS_CANONICAL_IDENTITY", "REJECT_TRANSLATION_SELF_AUTHORIZATION"],
    },
    {
        "invariant_id": "HHS-I018",
        "name": "Canonical semantic translation boundary",
        "statement": "Translation preserves source identity, epistemic status, provenance, authority boundaries, and declared loss across every semantic projection.",
        "domain": ["translation", "language_interface", "projection", "provenance"],
        "depends_on": ["HHS-I001", "HHS-I002", "HHS-I017"],
        "required_witnesses": ["HHS_CANONICAL_SEMANTIC_TRANSLATION_WITNESS_V1"],
        "required_validators": ["validate_canonical_semantic_translation_boundary"],
        "rejection_codes": ["REJECT_TRANSLATION_MUTATES_CANONICAL_MEANING"],
    },
    {
        "invariant_id": "HHS-I019",
        "name": "Canonical derivation authority boundary",
        "statement": "Derivation is the continuity carrier of canonical identity across transformation; competence never implies authority and canonical continuation requires role-local authority, witnessed handoff, provenance, and independent revalidation.",
        "domain": ["authority_graph", "role_contract", "agent_orchestration", "handoff", "response_selection", "attention_separation"],
        "depends_on": ["HHS-I001", "HHS-I002", "HHS-I017", "HHS-I018"],
        "required_witnesses": ["HHS_CANONICAL_AUTHORITY_GRAPH_V1", "HHS_CROSS_ROLE_HANDOFF_V1", "HHS_INDEPENDENT_REVALIDATION_DECISION_V1"],
        "required_validators": ["validate_role_local_authority", "validate_derivation_equivalence", "independently_revalidate"],
        "rejection_codes": ["REJECT_AGENT_CAPABILITY_AS_CANONICAL_AUTHORITY", "REJECT_OUTPUT_EQUIVALENCE_AS_DERIVATION_EQUIVALENCE", "REJECT_CROSS_AGENT_HANDOFF_WITHOUT_PROVENANCE", "REJECT_CANONICAL_CONTINUATION_WITHOUT_REVALIDATION"],
    },
]


def build_default_invariant_registry() -> HHSKernelInvariantRegistry:
    registry = HHSKernelInvariantRegistry()
    for invariant in INVARIANT_SEED:
        registry.register_invariant(invariant)
    return registry


def register_invariant(invariant: Mapping[str, Any], registry: Optional[HHSKernelInvariantRegistry] = None) -> Dict[str, Any]:
    return (registry or build_default_invariant_registry()).register_invariant(invariant).to_dict()


def get_invariant(invariant_id: str) -> Dict[str, Any]:
    return build_default_invariant_registry().get_invariant(invariant_id)


def list_invariants() -> List[Dict[str, Any]]:
    return build_default_invariant_registry().list_invariants()


def resolve_invariant_dependencies(invariant_id: str) -> List[str]:
    return build_default_invariant_registry().resolve_invariant_dependencies(invariant_id)


def validate_invariant_registry(registry: Optional[HHSKernelInvariantRegistry] = None) -> Dict[str, Any]:
    return (registry or build_default_invariant_registry()).validate_invariant_registry()


def build_invariant_registry_witness(registry: Optional[HHSKernelInvariantRegistry] = None) -> Dict[str, Any]:
    return (registry or build_default_invariant_registry()).build_invariant_registry_witness()


def kernel_invariant_registry_self_test() -> Dict[str, Any]:
    registry = build_default_invariant_registry()
    validation = registry.validate_invariant_registry()
    dependencies = {iid: registry.resolve_invariant_dependencies(iid) for iid in sorted(registry._invariants)}
    return {
        "schema": "HHS_KERNEL_INVARIANT_REGISTRY_SELF_TEST_V1",
        "ok": validation.get("ok") and len(registry.list_invariants()) == 16,
        "version": VERSION,
        "invariant_count": len(registry.list_invariants()),
        "validation": validation,
        "dependencies": dependencies,
    }


if __name__ == "__main__":
    print(kernel_invariant_registry_self_test())
