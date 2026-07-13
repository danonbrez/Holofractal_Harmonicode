"""
HHS Contract/Witness Schema Registry v1
=======================================

Pass 030 consolidates the authority-layer object model before expanding from
contract-bound dry runs toward authorized execution. The registry is a compact,
versioned map for the execution objects that now move through HHS:

* runtime packets and execution requests;
* guarded invocation records;
* semantic adapter records;
* dry-run traces;
* C u^72 Hash72 kernel witnesses;
* HHS Foundational conformance audits;
* unified ledger records;
* API/GUI envelopes;
* failure/rollback records.

The registry does not replace existing contracts. It makes them identifiable,
comparable, and auditable so the authority layer itself cannot drift into a set
of orphan schemas.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_contract_v1 import (
    CONTRACT_VERSION,
    assert_contract,
    make_api_response_contract,
    make_execution_request,
    make_runtime_packet,
)
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_CONTRACT_SCHEMA_REGISTRY_V1"
VERSION = "PASS_030"
MANIFEST_FILE = "CONTRACT_SCHEMA_REGISTRY_PASS_030.json"
REPORT_FILE = "CONTRACT_SCHEMA_REGISTRY_PASS_030.md"
PIPELINE_MAP_FILE = "EXECUTION_PIPELINE_MAP_PASS_030.md"
HASH72_LEN = 72

SCHEMA_FAMILY_RUNTIME_PACKET = "RUNTIME_PACKET"
SCHEMA_FAMILY_EXECUTION_REQUEST = "EXECUTION_REQUEST"
SCHEMA_FAMILY_INVOCATION_RECORD = "INVOCATION_RECORD"
SCHEMA_FAMILY_SEMANTIC_ADAPTER_RECORD = "SEMANTIC_ADAPTER_RECORD"
SCHEMA_FAMILY_DRYRUN_TRACE = "DRYRUN_TRACE"
SCHEMA_FAMILY_KERNEL_WITNESS = "KERNEL_WITNESS"
SCHEMA_FAMILY_FOUNDATIONAL_AUDIT = "FOUNDATIONAL_AUDIT"
SCHEMA_FAMILY_LEDGER_ENTRY = "LEDGER_ENTRY"
SCHEMA_FAMILY_API_ENVELOPE = "API_ENVELOPE"
SCHEMA_FAMILY_FAILURE_RECORD = "FAILURE_RECORD"

PIPELINE_STAGES = [
    "DISCOVERY",
    "REACHABILITY",
    "CAPABILITY_PLANNING",
    "GUARDED_INVOCATION_RECORD",
    "SEMANTIC_ADAPTER_EXECUTION",
    "DRYRUN_LIVE_EXECUTION",
    "AUTHORIZED_EXECUTION_CANDIDATE",
]


class HHSContractSchemaRegistryError(RuntimeError):
    """Raised when a schema object violates the Pass 030 registry."""


@dataclass(frozen=True)
class HHSSchemaFamilySpec:
    family: str
    description: str
    schema_patterns: Sequence[str]
    contract_types: Sequence[str] = field(default_factory=tuple)
    required_fields: Sequence[str] = field(default_factory=tuple)
    required_hash72_fields: Sequence[str] = field(default_factory=tuple)
    requires_kernel_witness: bool = False
    requires_foundational_audit: bool = False
    requires_ledger_binding: bool = False
    failure_behavior: str = "reject_with_failure_record"
    producers: Sequence[str] = field(default_factory=tuple)
    consumers: Sequence[str] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key in ("schema_patterns", "contract_types", "required_fields", "required_hash72_fields", "producers", "consumers"):
            data[key] = list(data[key])
        return data


@dataclass(frozen=True)
class HHSSchemaObjectClassification:
    family: str
    schema: str
    contract_type: str
    confidence: str
    reasons: List[str]
    registry_version: str = VERSION
    registry_schema: str = "HHS_SCHEMA_OBJECT_CLASSIFICATION_V1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HHSSchemaObjectValidation:
    ok: bool
    family: str
    schema: str
    contract_type: str
    missing_fields: List[str]
    missing_hash72_fields: List[str]
    reasons: List[str]
    kernel_witness_required: bool
    foundational_audit_required: bool
    ledger_binding_required: bool
    registry_version: str = VERSION
    registry_schema: str = "HHS_SCHEMA_OBJECT_VALIDATION_V1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def _is_hash72(value: Any) -> bool:
    return isinstance(value, str) and len(value) == HASH72_LEN


def _has_nested_key(obj: Mapping[str, Any], dotted_key: str) -> bool:
    cur: Any = obj
    for part in dotted_key.split("."):
        if not isinstance(cur, Mapping) or part not in cur:
            return False
        cur = cur[part]
    return True


def _nested_value(obj: Mapping[str, Any], dotted_key: str) -> Any:
    cur: Any = obj
    for part in dotted_key.split("."):
        if not isinstance(cur, Mapping):
            return None
        cur = cur.get(part)
    return cur


def schema_family_specs() -> List[Dict[str, Any]]:
    """Return the canonical Pass 030 schema-family registry."""

    specs = [
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_EXECUTION_REQUEST,
            description="Intent-to-execute object generated before service, adapter, dry-run, or future live execution.",
            schema_patterns=("HHS_EXECUTION_REQUEST_CONTRACT_V1",),
            contract_types=("execution_request",),
            required_fields=("request_id", "source", "operation", "payload", "contract_hash72"),
            required_hash72_fields=("contract_hash72",),
            requires_kernel_witness=False,
            requires_foundational_audit=True,
            requires_ledger_binding=False,
            producers=("hhs_runtime_contract_v1.make_execution_request",),
            consumers=("service_registry", "plugin_invocation_executor", "semantic_adapter_runtime", "dryrun_live_plugin_executor"),
        ),
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_RUNTIME_PACKET,
            description="Canonical transport packet for internal/ingress/propagation/egress runtime movement.",
            schema_patterns=("HHS_RUNTIME_PACKET_CONTRACT_V1",),
            contract_types=("runtime_packet",),
            required_fields=("packet_id", "direction", "source", "payload", "payload_hash72", "contract_hash72"),
            required_hash72_fields=("payload_hash72", "contract_hash72"),
            requires_kernel_witness=True,
            requires_foundational_audit=True,
            requires_ledger_binding=False,
            producers=("hhs_runtime_contract_v1.make_runtime_packet",),
            consumers=("io_gateway", "runtime_dataflow_guard", "api_envelope", "gui_runtime_contract_surface"),
        ),
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_INVOCATION_RECORD,
            description="Guarded invocation record for planned plugin/service execution without bypassing authority.",
            schema_patterns=("HHS_GUARDED_PLUGIN_INVOCATION", "HHS_SERVICE_DISPATCH_RECORD"),
            required_fields=("execution_request", "runtime_packet", "foundational_conformance_pre", "foundational_conformance_post"),
            required_hash72_fields=(),
            requires_kernel_witness=True,
            requires_foundational_audit=True,
            requires_ledger_binding=True,
            producers=("hhs_guarded_plugin_invocation_executor_v1", "hhs_service_registry_v1"),
            consumers=("semantic_plugin_adapter_runtime", "dryrun_live_plugin_executor"),
        ),
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_SEMANTIC_ADAPTER_RECORD,
            description="Meaning-preserving adapter execution record that summarizes a plugin function without raw legacy body execution.",
            schema_patterns=("HHS_SEMANTIC_PLUGIN_ADAPTER", "HHS_SEMANTIC_ADAPTER"),
            required_fields=("execution_request", "runtime_packet", "proposition_identity", "meaning_witness"),
            required_hash72_fields=(),
            requires_kernel_witness=True,
            requires_foundational_audit=True,
            requires_ledger_binding=True,
            producers=("hhs_semantic_plugin_adapter_runtime_v1",),
            consumers=("dryrun_live_plugin_executor", "system_closure_harness"),
        ),
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_DRYRUN_TRACE,
            description="Contract-bound dry-run invocation trace; imports/signature validation may occur, but target function bodies and mutation remain blocked.",
            schema_patterns=("HHS_DRYRUN_LIVE_PLUGIN",),
            required_fields=("execution_policy", "function_surface", "dry_run_result", "execution_request", "runtime_packet", "dryrun_kernel_witness"),
            required_hash72_fields=("dryrun_kernel_witness.digest72",),
            requires_kernel_witness=True,
            requires_foundational_audit=True,
            requires_ledger_binding=True,
            producers=("hhs_dryrun_live_plugin_executor_v1",),
            consumers=("future_authorized_execution_gate", "contract_schema_registry"),
        ),
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_KERNEL_WITNESS,
            description="C u^72 Digital DNA witness proving Hash72 authority via rotation profile and zero-sum closure.",
            schema_patterns=("HHS_HASH72_KERNEL_WITNESS_V1",),
            required_fields=("label", "dna", "digest", "zero_sum", "trace_count", "rotation_profile", "positions"),
            required_hash72_fields=("digest",),
            requires_kernel_witness=False,
            requires_foundational_audit=False,
            requires_ledger_binding=False,
            producers=("hhs_hash72_kernel_authority_v1",),
            consumers=("all authority-bearing schemas",),
        ),
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_FOUNDATIONAL_AUDIT,
            description="HHS-M001..M007 conformance record for referential identity, transformation transparency, and meaning conservation.",
            schema_patterns=("HHS_FOUNDATIONAL_CONFORMANCE_V1", "HHS_MEANING_CONSERVATION_WITNESS_V1", "HHS_PROPOSITION_IDENTITY_V1"),
            required_fields=("schema",),
            required_hash72_fields=(),
            requires_kernel_witness=False,
            requires_foundational_audit=False,
            requires_ledger_binding=False,
            producers=("hhs_foundational_standards_v1",),
            consumers=("service_registry", "plugin_adapters", "dryrun_live_plugin_executor", "future_authorized_execution_gate"),
        ),
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_LEDGER_ENTRY,
            description="Persistent receipt-chain summary or entry binding authority-bearing transformations to the unified Hash72 ledger.",
            schema_patterns=("HHS_UNIFIED_HASH72_LEDGER", "HHS_*_LEDGER_PAYLOAD"),
            required_fields=("ledger_hash72", "tip_hash72"),
            required_hash72_fields=("ledger_hash72", "tip_hash72"),
            requires_kernel_witness=True,
            requires_foundational_audit=False,
            requires_ledger_binding=False,
            producers=("hhs_unified_hash72_ledger_v1",),
            consumers=("service_registry", "persistence_guard", "closure_harness", "contract_schema_registry"),
        ),
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_API_ENVELOPE,
            description="Backend/GUI-safe response envelope carrying canonical API response contract and payload witness.",
            schema_patterns=("HHS_API_RESPONSE_CONTRACT_V1", "HHS_CANONICAL_API_RESPONSE_ENVELOPE_V1"),
            contract_types=("api_response",),
            required_fields=("route", "method", "payload", "payload_hash72", "contract_hash72"),
            required_hash72_fields=("payload_hash72", "contract_hash72"),
            requires_kernel_witness=True,
            requires_foundational_audit=False,
            requires_ledger_binding=False,
            producers=("hhs_runtime_contract_v1.envelope_api_response", "backend_routes"),
            consumers=("gui_runtime_contract_surface",),
        ),
        HHSSchemaFamilySpec(
            family=SCHEMA_FAMILY_FAILURE_RECORD,
            description="Explicit rejection/rollback/error record for schema violations, blocked executions, and failed closure checks.",
            schema_patterns=("HHS_FAILURE_RECORD", "HHS_AUTHORIZED_EXECUTION_FAILURE_RECORD_V1", "HHS_ROLLBACK", "HHS_REJECTION"),
            required_fields=("schema", "source", "reason"),
            required_hash72_fields=(),
            requires_kernel_witness=True,
            requires_foundational_audit=True,
            requires_ledger_binding=True,
            producers=("future_authorized_execution_gate", "rollback_handlers"),
            consumers=("ledger", "operator_reports", "closure_harness"),
        ),
    ]
    return [spec.to_dict() for spec in specs]


def _registry_by_family() -> Dict[str, Dict[str, Any]]:
    return {spec["family"]: spec for spec in schema_family_specs()}


def classify_schema_object(obj: Mapping[str, Any]) -> Dict[str, Any]:
    data = dict(obj or {})
    schema = str(data.get("schema") or data.get("registry_schema") or "")
    contract_type = str(data.get("contract_type") or "")
    reasons: List[str] = []

    def hit(family: str, reason: str, confidence: str = "HIGH") -> Dict[str, Any]:
        reasons.append(reason)
        return HHSSchemaObjectClassification(family, schema, contract_type, confidence, reasons).to_dict()

    if contract_type == "execution_request" or schema == "HHS_EXECUTION_REQUEST_CONTRACT_V1":
        return hit(SCHEMA_FAMILY_EXECUTION_REQUEST, "matched execution_request contract type or schema")
    if contract_type == "runtime_packet" or schema == "HHS_RUNTIME_PACKET_CONTRACT_V1":
        return hit(SCHEMA_FAMILY_RUNTIME_PACKET, "matched runtime_packet contract type or schema")
    if contract_type == "api_response" or schema in {"HHS_API_RESPONSE_CONTRACT_V1", "HHS_CANONICAL_API_RESPONSE_ENVELOPE_V1"}:
        return hit(SCHEMA_FAMILY_API_ENVELOPE, "matched api_response contract type or envelope schema")
    if schema == "HHS_HASH72_KERNEL_WITNESS_V1" or {"rotation_profile", "positions", "zero_sum"}.issubset(data.keys()):
        return hit(SCHEMA_FAMILY_KERNEL_WITNESS, "matched Hash72/u^72 kernel witness structure")
    if schema in {"HHS_FOUNDATIONAL_CONFORMANCE_V1", "HHS_MEANING_CONSERVATION_WITNESS_V1", "HHS_PROPOSITION_IDENTITY_V1"}:
        return hit(SCHEMA_FAMILY_FOUNDATIONAL_AUDIT, "matched foundational/conservation schema")
    if "DRYRUN_LIVE_PLUGIN" in schema or "dry_run_result" in data or "dryrun_kernel_witness" in data:
        return hit(SCHEMA_FAMILY_DRYRUN_TRACE, "matched dry-run execution trace fields")
    if "SEMANTIC_PLUGIN_ADAPTER" in schema or "semantic_adapter" in schema.lower():
        return hit(SCHEMA_FAMILY_SEMANTIC_ADAPTER_RECORD, "matched semantic adapter schema pattern")
    if "GUARDED_PLUGIN_INVOCATION" in schema or schema == "HHS_SERVICE_DISPATCH_RECORD_V1":
        return hit(SCHEMA_FAMILY_INVOCATION_RECORD, "matched guarded invocation/service dispatch schema")
    if "ledger_hash72" in data and "tip_hash72" in data:
        return hit(SCHEMA_FAMILY_LEDGER_ENTRY, "matched ledger hash summary fields")
    if schema == "HHS_AUTHORIZED_EXECUTION_FAILURE_RECORD_V1":
        return hit(SCHEMA_FAMILY_FAILURE_RECORD, "matched authorized execution failure record schema")
    if "error" in data or "errors" in data or "reason" in data or "rollback" in schema.lower() or "rejection" in schema.lower():
        return hit(SCHEMA_FAMILY_FAILURE_RECORD, "matched failure/rejection/rollback indicators", confidence="MEDIUM")
    return hit("UNKNOWN", "no Pass 030 schema-family match", confidence="LOW")


def validate_schema_object(obj: Mapping[str, Any]) -> Dict[str, Any]:
    data = dict(obj or {})
    classification = classify_schema_object(data)
    family = classification["family"]
    specs = _registry_by_family()
    spec = specs.get(family)
    missing_fields: List[str] = []
    missing_hash72_fields: List[str] = []
    reasons: List[str] = []

    if spec is None:
        reasons.append("schema family is not registered")
        return HHSSchemaObjectValidation(
            ok=False,
            family=family,
            schema=classification.get("schema", ""),
            contract_type=classification.get("contract_type", ""),
            missing_fields=[],
            missing_hash72_fields=[],
            reasons=reasons,
            kernel_witness_required=False,
            foundational_audit_required=False,
            ledger_binding_required=False,
        ).to_dict()

    for key in spec.get("required_fields", []):
        if not _has_nested_key(data, str(key)):
            missing_fields.append(str(key))
    for key in spec.get("required_hash72_fields", []):
        value = _nested_value(data, str(key))
        if not _is_hash72(value):
            missing_hash72_fields.append(str(key))

    if missing_fields:
        reasons.append("missing required fields: " + ", ".join(missing_fields))
    if missing_hash72_fields:
        reasons.append("missing native 72-symbol fields: " + ", ".join(missing_hash72_fields))

    # Reuse the canonical runtime contract validator where the object is a
    # native contract. This avoids duplicate rules for the established surface.
    contract_type = str(data.get("contract_type") or "")
    if contract_type in {"execution_request", "runtime_packet", "api_response"}:
        try:
            assert_contract(data, expected_type=contract_type)
        except Exception as exc:
            reasons.append(f"canonical runtime contract validator rejected object: {type(exc).__name__}: {exc}")

    return HHSSchemaObjectValidation(
        ok=not reasons,
        family=family,
        schema=classification.get("schema", ""),
        contract_type=classification.get("contract_type", ""),
        missing_fields=missing_fields,
        missing_hash72_fields=missing_hash72_fields,
        reasons=reasons,
        kernel_witness_required=bool(spec.get("requires_kernel_witness")),
        foundational_audit_required=bool(spec.get("requires_foundational_audit")),
        ledger_binding_required=bool(spec.get("requires_ledger_binding")),
    ).to_dict()


def _sample_objects() -> Dict[str, Dict[str, Any]]:
    proposition = make_proposition_identity(
        "Pass 030 preserves authority-layer schema identity before authorized execution expansion.",
        source="hhs_contract_schema_registry_v1.sample_objects",
        context={"pass": VERSION},
    )
    meaning = make_meaning_witness(
        proposition,
        proposition,
        transformation_rule="schema registry classification preserves object identity",
        reversible=True,
    )
    request = make_execution_request(
        source="hhs_contract_schema_registry_v1.sample_objects",
        operation="contract_schema_registry.self_test",
        payload={"proposition_identity": proposition, "meaning_witness": meaning},
    )
    packet = make_runtime_packet(
        "INTERNAL",
        "hhs_contract_schema_registry_v1.sample_objects",
        {"proposition_identity": proposition, "meaning_witness": meaning},
    )
    api = make_api_response_contract("/api/runtime/contract-schema-registry", "GET", {"ok": True})
    kernel_witness = make_hash72_kernel_witness("hhs_contract_schema_registry_sample_v1", {"request": request, "packet": packet}, width=72).to_dict()
    foundational = assert_foundational_conformance(
        {"schema": "HHS_SCHEMA_REGISTRY_FOUNDATIONAL_SAMPLE_V1", "proposition_identity": proposition, "meaning_witness": meaning},
        source="hhs_contract_schema_registry_v1.sample_objects",
        require_receipt=False,
    ).to_dict()
    ledger_summary = {
        "schema": "HHS_UNIFIED_HASH72_LEDGER_SUMMARY_V1",
        "entry_count": 0,
        "tip_hash72": kernel_witness["digest"],
        "ledger_hash72": kernel_witness["dna"],
    }
    dryrun_trace = {
        "schema": "HHS_DRYRUN_LIVE_PLUGIN_EXECUTION_V1",
        "execution_policy": {"dry_run_execution": True, "function_body_execution": False},
        "function_surface": {"function": "sample", "body_execution_performed": False},
        "dry_run_result": {"call_performed": False, "mutation_performed": False},
        "execution_request": request,
        "runtime_packet": packet,
        "dryrun_kernel_witness": {**kernel_witness, "digest72": kernel_witness["digest"]},
        "foundational_conformance_pre": foundational,
        "foundational_conformance_post": foundational,
        "ledger": ledger_summary,
    }
    invocation = {
        "schema": "HHS_SERVICE_DISPATCH_RECORD_V1",
        "execution_request": request,
        "runtime_packet": packet,
        "foundational_conformance_pre": foundational,
        "foundational_conformance_post": foundational,
        "unified_ledger": ledger_summary,
    }
    semantic_adapter = {
        "schema": "HHS_SEMANTIC_PLUGIN_ADAPTER_RECORD_V1",
        "execution_request": request,
        "runtime_packet": packet,
        "proposition_identity": proposition,
        "meaning_witness": meaning,
        "adapter_kernel_witness": {**kernel_witness, "digest72": kernel_witness["digest"]},
        "ledger": ledger_summary,
    }
    failure = {
        "schema": "HHS_FAILURE_RECORD_V1",
        "source": "hhs_contract_schema_registry_v1.sample_objects",
        "reason": "sample rejection path",
        "rollback": False,
        "kernel_witness": {**kernel_witness, "digest72": kernel_witness["digest"]},
        "foundational_conformance": foundational,
        "ledger": ledger_summary,
    }
    return {
        "execution_request": request,
        "runtime_packet": packet,
        "api_envelope": api,
        "kernel_witness": kernel_witness,
        "foundational_audit": foundational,
        "ledger_entry": ledger_summary,
        "dryrun_trace": dryrun_trace,
        "invocation_record": invocation,
        "semantic_adapter_record": semantic_adapter,
        "failure_record": failure,
    }


def build_contract_schema_registry_manifest(root: Optional[str | Path] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    specs = schema_family_specs()
    samples = _sample_objects()
    classifications = {name: classify_schema_object(obj) for name, obj in samples.items()}
    validations = {name: validate_schema_object(obj) for name, obj in samples.items()}
    spec_payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "family_count": len(specs),
        "pipeline_stage_count": len(PIPELINE_STAGES),
        "families": [spec["family"] for spec in specs],
        "pipeline_stages": PIPELINE_STAGES,
        "policy": "Every execution-related object must be schema-identifiable, versioned, comparable, Hash72/u^72 witness-compatible, and failure-path explicit before promotion to authorized execution.",
    }
    witness = make_hash72_kernel_witness("hhs_contract_schema_registry_manifest_v1", spec_payload, width=72).to_dict()
    ok = all(item.get("ok") for item in validations.values()) and len(specs) == 10
    return {
        **spec_payload,
        "ok": bool(ok),
        "repo_root": str(root_path),
        "schema_families": specs,
        "sample_classifications": classifications,
        "sample_validations": validations,
        "sample_objects": samples,
        "hash72_kernel_witness": {**witness, "digest72": witness.get("digest", "")},
    }


def write_contract_schema_registry_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_contract_schema_registry_manifest(root_path)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_registry_report(root_path, manifest)
    _write_pipeline_map(root_path, manifest)
    return manifest


def _write_registry_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = ["| Family | Kernel Witness | Foundational Audit | Ledger Binding | Failure Behavior |", "|---|---:|---:|---:|---|"]
    for spec in manifest.get("schema_families", []):
        rows.append(
            "| `{}` | {} | {} | {} | `{}` |".format(
                spec.get("family"),
                bool(spec.get("requires_kernel_witness")),
                bool(spec.get("requires_foundational_audit")),
                bool(spec.get("requires_ledger_binding")),
                spec.get("failure_behavior"),
            )
        )
    validation_rows = ["| Sample | Family | OK | Reasons |", "|---|---|---:|---|"]
    for name, validation in manifest.get("sample_validations", {}).items():
        validation_rows.append(
            "| `{}` | `{}` | {} | {} |".format(
                name,
                validation.get("family"),
                bool(validation.get("ok")),
                "; ".join(validation.get("reasons") or []) or "—",
            )
        )
    report = f"""# Contract/Witness Schema Registry — Pass 030

## Purpose

Pass 030 consolidates HHS execution objects into one inspectable authority-layer registry. The goal is to prevent schema drift before the runtime promotes dry-run traces into controlled authorized execution.

## Non-Bypass Rule

```text
execution object
→ schema family classification
→ required fields/hash72 fields
→ Hash72/u^72 witness requirement
→ HHS-M001..M007 foundational audit requirement
→ ledger/failure-path requirement
→ only then eligible for future authorized execution
```

## Summary

```json
{json.dumps({k: manifest.get(k) for k in ['schema', 'version', 'ok', 'family_count', 'pipeline_stage_count', 'policy']}, indent=2, sort_keys=True)}
```

## Schema Families

{chr(10).join(rows)}

## Sample Validations

{chr(10).join(validation_rows)}

## Registry Witness

```json
{json.dumps(manifest.get('hash72_kernel_witness', {}), indent=2, sort_keys=True)}
```
"""
    (root / REPORT_FILE).write_text(report, encoding="utf-8")


def _write_pipeline_map(root: Path, manifest: Mapping[str, Any]) -> None:
    pipeline = """# Execution Pipeline Map — Pass 030

## Staged Runtime Model

```text
Discovery
  ↓
Reachability
  ↓
Capability Planning
  ↓
Guarded Invocation Record
  ↓
Semantic Adapter Execution
  ↓
Dry-Run Live Execution
  ↓
Authorized Execution Candidate
```

## Authority Object Flow

```text
EXECUTION_REQUEST
  → RUNTIME_PACKET
  → INVOCATION_RECORD
  → SEMANTIC_ADAPTER_RECORD
  → DRYRUN_TRACE
  → KERNEL_WITNESS
  → FOUNDATIONAL_AUDIT
  → LEDGER_ENTRY
  → API_ENVELOPE / FAILURE_RECORD
```

## Pass 030 Gate

Future live execution must not be promoted from dry-run unless the object set is:

1. schema-family identifiable;
2. versioned;
3. carrying required native 72-symbol Hash72/u^72 witnesses;
4. carrying HHS-M001..M007 foundational conformance where required;
5. ledger-compatible;
6. failure-path explicit.

## Registered Families

"""
    for spec in manifest.get("schema_families", []):
        pipeline += f"### {spec.get('family')}\n\n{spec.get('description')}\n\n"
        pipeline += "```json\n" + json.dumps({
            "required_fields": spec.get("required_fields"),
            "required_hash72_fields": spec.get("required_hash72_fields"),
            "requires_kernel_witness": spec.get("requires_kernel_witness"),
            "requires_foundational_audit": spec.get("requires_foundational_audit"),
            "requires_ledger_binding": spec.get("requires_ledger_binding"),
            "producers": spec.get("producers"),
            "consumers": spec.get("consumers"),
        }, indent=2, sort_keys=True) + "\n```\n\n"
    (root / PIPELINE_MAP_FILE).write_text(pipeline, encoding="utf-8")


def contract_schema_registry_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    manifest = write_contract_schema_registry_artifacts(root)
    return {
        "schema": "HHS_CONTRACT_SCHEMA_REGISTRY_SELF_TEST_V1",
        "ok": bool(manifest.get("ok")),
        "family_count": manifest.get("family_count"),
        "pipeline_stage_count": manifest.get("pipeline_stage_count"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE, PIPELINE_MAP_FILE],
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
        "sample_validation_ok": all(item.get("ok") for item in manifest.get("sample_validations", {}).values()),
    }


if __name__ == "__main__":
    print(json.dumps(contract_schema_registry_self_test(), indent=2, sort_keys=True))
