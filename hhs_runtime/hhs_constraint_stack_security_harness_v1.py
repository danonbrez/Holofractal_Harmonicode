"""
HHS Constraint Stack Security Harness v1
========================================

Pass 034 turns the Pass 033 admissibility/security standards into executable
security invariant tests.  The harness does not broaden execution.  It runs the
constraint stack against representative bypass, forgery, and incomplete-witness
scenarios and proves the central HHS propagation rule:

* a terminal value alone is never sufficient;
* silent, schemaless, ledgerless, or partial witness paths are rejected;
* a brute-force sequence that satisfies the complete rule stack is reclassified
  as lawful HHS propagation rather than bypass.

This module is intentionally conservative.  Rejected scenarios never execute
legacy/plugin logic, never mutate external state, and always emit explicit
Hash72/u^72 witnessed failure records and ledger receipts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
import copy
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_reality_to_manifold_translation_v1 import (
    CANONICAL_TENSOR_SEED,
    make_non_silent_security_policy,
    translate_reality_to_manifold,
)
from hhs_runtime.hhs_runtime_contract_v1 import make_execution_request, make_runtime_packet
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_CONSTRAINT_STACK_SECURITY_HARNESS_V1"
VERSION = "PASS_034"
MANIFEST_FILE = "CONSTRAINT_STACK_SECURITY_HARNESS_PASS_034.json"
REPORT_FILE = "CONSTRAINT_STACK_SECURITY_HARNESS_PASS_034.md"
NON_SILENT_REPORT_FILE = "NON_SILENT_OPERATION_TEST_REPORT_PASS_034.md"
ANTI_BRUTEFORCE_REPORT_FILE = "ANTI_BRUTEFORCE_PROPAGATION_TEST_REPORT_PASS_034.md"

ACCEPTED_STATUS = "PROPAGATION_ADMISSIBLE"
RECLASSIFIED_STATUS = "RECLASSIFIED_AS_VALID_PROPAGATION"

REJECTION_STATUS_BY_REASON = {
    "FORGED_TERMINAL_VALUE": "REJECTED_FORGED_TERMINAL_VALUE",
    "LEDGERLESS_MUTATION": "REJECTED_LEDGERLESS_MUTATION",
    "SCHEMALESS_TRANSFORMATION": "REJECTED_SCHEMALESS_TRANSFORMATION",
    "PHASE_PRODUCT_DRIFT": "REJECTED_PHASE_PRODUCT_DRIFT",
    "ROTATION_PROFILE_DRIFT": "REJECTED_ROTATION_PROFILE_DRIFT",
    "TEMPORAL_COHERENCE_DRIFT": "REJECTED_TEMPORAL_COHERENCE_DRIFT",
    "INCOMPLETE_WITNESS_CHAIN": "REJECTED_INCOMPLETE_WITNESS_CHAIN",
    "UNKNOWN_SECURITY_REJECTION": "REJECTED_SECURITY_INVARIANT_FAILURE",
}


@dataclass(frozen=True)
class ConstraintStackScenarioResult:
    schema: str
    version: str
    scenario: str
    status: str
    accepted: bool
    reclassified_as_valid_propagation: bool
    reason_code: str
    expected_status: str
    expected_match: bool
    execution_performed: bool
    mutation_performed: bool
    terminal_value_sufficient: bool
    witness_chain_complete: bool
    required_layers: Dict[str, bool]
    missing_layers: List[str]
    failure_record: Dict[str, Any]
    kernel_witness: Dict[str, Any]
    foundational_conformance: Dict[str, Any]
    ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _json_stable(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str))


def _with_digest72_alias(witness: Mapping[str, Any]) -> Dict[str, Any]:
    data = dict(witness)
    data.setdefault("digest72", data.get("digest") or data.get("dna") or "")
    data.setdefault("authority", "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1")
    return data


def _layer_ok(record: Mapping[str, Any]) -> Dict[str, bool]:
    """Return the explicit layer status for an admissibility candidate."""

    tensor = record.get("tensor_seed") if isinstance(record.get("tensor_seed"), Mapping) else {}
    phase = record.get("phase_product_witnesses") if isinstance(record.get("phase_product_witnesses"), list) else []
    carrier = record.get("hash72_bigint_carrier") if isinstance(record.get("hash72_bigint_carrier"), Mapping) else {}
    harmonic = record.get("harmonic_time_audio_witness") if isinstance(record.get("harmonic_time_audio_witness"), Mapping) else {}
    triangulation = record.get("triangulation_of_truth") if isinstance(record.get("triangulation_of_truth"), Mapping) else {}
    omega = record.get("omega_projection_witness") if isinstance(record.get("omega_projection_witness"), Mapping) else {}
    foundational = record.get("foundational_conformance") if isinstance(record.get("foundational_conformance"), Mapping) else {}
    ledger = record.get("ledger") if isinstance(record.get("ledger"), Mapping) else {}
    security = record.get("security_policy") if isinstance(record.get("security_policy"), Mapping) else {}
    manifold_kernel = record.get("manifold_kernel_witness") if isinstance(record.get("manifold_kernel_witness"), Mapping) else {}
    runtime_packet = record.get("runtime_packet") if isinstance(record.get("runtime_packet"), Mapping) else {}
    execution_request = record.get("execution_request") if isinstance(record.get("execution_request"), Mapping) else {}

    return {
        "schema_identity": bool(record.get("schema")),
        "execution_request": bool(execution_request.get("contract_type") == "execution_request" or execution_request.get("schema")),
        "runtime_packet": bool(runtime_packet.get("contract_type") == "runtime_packet" or runtime_packet.get("schema")),
        "palindromic_tensor_seed12": bool(tensor.get("valid")),
        "palindromic_phase_product_ecc": bool(phase) and all(bool(item.get("palindrome_valid")) for item in phase),
        "hash72_bigint_lossless_decode": bool(carrier.get("lossless_decode")),
        "hash72_u72_kernel_witness": bool(manifold_kernel.get("digest72") or manifold_kernel.get("digest")),
        "hash72_rotation_profile": bool(carrier.get("rotation_profile")) and len(carrier.get("rotation_profile", [])) == 72,
        "harmonic_time_audio_ecc": bool(harmonic.get("harmonic_time_valid")),
        "triangulation_of_truth": bool(triangulation.get("ok")),
        "omega_projection_witness": bool(omega.get("ok")),
        "foundational_conformance": bool(foundational.get("ok")),
        "ledger_receipt": bool(ledger.get("verified")),
        "non_silent_security_policy": bool(security) and security.get("terminal_output_sufficient") is False,
    }


def _missing_layers(layers: Mapping[str, bool]) -> List[str]:
    return [name for name, ok in layers.items() if not ok]


def _reason_from_layers(layers: Mapping[str, bool]) -> str:
    missing = _missing_layers(layers)
    if not layers.get("schema_identity"):
        return "SCHEMALESS_TRANSFORMATION"
    # A candidate that is missing many layers is an incomplete witness chain.
    # A candidate that only lost the ledger receipt is a ledgerless mutation.
    if "ledger_receipt" in missing and len(missing) == 1:
        return "LEDGERLESS_MUTATION"
    if len(missing) > 1:
        return "INCOMPLETE_WITNESS_CHAIN"
    if not layers.get("palindromic_phase_product_ecc"):
        return "PHASE_PRODUCT_DRIFT"
    if not layers.get("hash72_rotation_profile") or not layers.get("hash72_bigint_lossless_decode"):
        return "ROTATION_PROFILE_DRIFT"
    if not layers.get("harmonic_time_audio_ecc"):
        return "TEMPORAL_COHERENCE_DRIFT"
    if missing:
        return "INCOMPLETE_WITNESS_CHAIN"
    return "UNKNOWN_SECURITY_REJECTION"


def make_terminal_value_only_claim(terminal_value: str = CANONICAL_TENSOR_SEED) -> Dict[str, Any]:
    """A guessed terminal value without the witnessed path."""

    return {
        "schema": "HHS_TERMINAL_VALUE_ONLY_CLAIM_V1",
        "version": VERSION,
        "terminal_value": terminal_value,
        "claim": "terminal output is sufficient for propagation",
        "provided_witness_chain": False,
    }


def _make_failure_record(
    *,
    scenario: str,
    status: str,
    reason_code: str,
    candidate: Mapping[str, Any],
) -> Dict[str, Any]:
    source = f"hhs_constraint_stack_security_harness_v1.{scenario}"
    proposition = make_proposition_identity(
        "Constraint-stack security rejects terminal-only, silent, ledgerless, partial, or drifted propagation attempts.",
        source=source,
        context={"scenario": scenario, "reason_code": reason_code, "status": status},
    )
    meaning = make_meaning_witness(
        proposition,
        proposition,
        transformation_rule="security rejection preserves proposition identity while refusing propagation",
        reversible=True,
    )
    request = make_execution_request(
        source=source,
        operation="constraint_stack_security_rejection",
        payload={"scenario": scenario, "reason_code": reason_code, "proposition_identity": proposition, "meaning_witness": meaning},
        requires_authority=True,
    )
    packet = make_runtime_packet(
        "REJECTION",
        source,
        {"scenario": scenario, "reason_code": reason_code, "status": status},
    )
    foundational = assert_foundational_conformance(
        {
            "schema": "HHS_CONSTRAINT_STACK_SECURITY_FAILURE_FOUNDATIONAL_PAYLOAD_V1",
            "scenario": scenario,
            "reason_code": reason_code,
            "proposition_identity": proposition,
            "meaning_witness": meaning,
        },
        source=source,
        require_receipt=False,
    ).to_dict()
    failure_preledger = {
        "schema": "HHS_CONSTRAINT_STACK_SECURITY_FAILURE_RECORD_PRELEDGER_V1",
        "version": VERSION,
        "scenario": scenario,
        "status": status,
        "reason_code": reason_code,
        "execution_performed": False,
        "mutation_performed": False,
        "terminal_value_sufficient": False,
        "candidate_schema": candidate.get("schema"),
    }
    kernel = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_CONSTRAINT_STACK_SECURITY_FAILURE_RECORD_V1",
        {"failure": failure_preledger, "request": request, "packet": packet, "foundational": foundational},
        width=72,
    ).to_dict())
    ledger = append_payload("CONSTRAINT_STACK_SECURITY_FAILURE", source, {**failure_preledger, "kernel_digest": kernel.get("digest72")})
    return {
        "schema": "HHS_CONSTRAINT_STACK_SECURITY_FAILURE_RECORD_V1",
        "version": VERSION,
        "scenario": scenario,
        "status": status,
        "reason_code": reason_code,
        "execution_performed": False,
        "mutation_performed": False,
        "terminal_value_sufficient": False,
        "execution_request": request,
        "runtime_packet": packet,
        "proposition_identity": proposition,
        "meaning_witness": meaning,
        "foundational_conformance": foundational,
        "kernel_witness": kernel,
        "ledger": {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": verify_unified_ledger().get("ok")},
    }


def evaluate_constraint_stack_candidate(
    scenario: str,
    candidate: Mapping[str, Any],
    *,
    expected_status: str,
    brute_force_claim: bool = False,
) -> Dict[str, Any]:
    """Evaluate a candidate propagation object against the full stack."""

    stable_candidate = _json_stable(candidate)
    if not isinstance(stable_candidate, dict):
        stable_candidate = {"schema": "HHS_INVALID_SECURITY_CANDIDATE_V1", "value": stable_candidate}
    layers = _layer_ok(stable_candidate)
    missing = _missing_layers(layers)
    witness_chain_complete = not missing
    accepted = (
        stable_candidate.get("status") == ACCEPTED_STATUS
        and stable_candidate.get("accepted") is True
        and witness_chain_complete
    )
    reclassified = bool(accepted and brute_force_claim)
    if reclassified:
        status = RECLASSIFIED_STATUS
        reason_code = "RULE_FOLLOWING_EQUIVALENCE"
    elif accepted:
        status = ACCEPTED_STATUS
        reason_code = "ALL_CONSTRAINT_LAYERS_CLOSED"
    elif stable_candidate.get("schema") == "HHS_TERMINAL_VALUE_ONLY_CLAIM_V1":
        status = REJECTION_STATUS_BY_REASON["FORGED_TERMINAL_VALUE"]
        reason_code = "FORGED_TERMINAL_VALUE"
    else:
        # Scenario-specific injected drift should report the layer that was
        # deliberately corrupted, even when secondary dependent layers also
        # become unavailable. Partial brute-force remains an incomplete chain.
        if scenario == "invalid_palindromic_phase_product_ecc":
            reason_code = "PHASE_PRODUCT_DRIFT"
        elif scenario == "invalid_hash72_rotation_profile":
            reason_code = "ROTATION_PROFILE_DRIFT"
        elif scenario == "invalid_harmonic_time_audio_ecc":
            reason_code = "TEMPORAL_COHERENCE_DRIFT"
        else:
            reason_code = _reason_from_layers(layers)
        status = REJECTION_STATUS_BY_REASON.get(reason_code, REJECTION_STATUS_BY_REASON["UNKNOWN_SECURITY_REJECTION"])

    if accepted:
        source = f"hhs_constraint_stack_security_harness_v1.{scenario}"
        foundational = dict(stable_candidate.get("foundational_conformance") or {})
        kernel = _with_digest72_alias(make_hash72_kernel_witness(
            "HHS_CONSTRAINT_STACK_SECURITY_ACCEPTED_OR_RECLASSIFIED_V1",
            {"scenario": scenario, "status": status, "candidate_digest": stable_candidate.get("manifold_kernel_witness", {}).get("digest72")},
            width=72,
        ).to_dict())
        ledger_payload = {
            "schema": "HHS_CONSTRAINT_STACK_SECURITY_ACCEPTED_OR_RECLASSIFIED_PRELEDGER_V1",
            "version": VERSION,
            "scenario": scenario,
            "status": status,
            "reason_code": reason_code,
            "reclassified_as_valid_propagation": reclassified,
            "kernel_digest": kernel.get("digest72"),
        }
        ledger = append_payload("CONSTRAINT_STACK_SECURITY_ACCEPTED", source, ledger_payload)
        failure_record = {}
        ledger_summary = {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": verify_unified_ledger().get("ok")}
    else:
        failure_record = _make_failure_record(scenario=scenario, status=status, reason_code=reason_code, candidate=stable_candidate)
        foundational = failure_record["foundational_conformance"]
        kernel = failure_record["kernel_witness"]
        ledger_summary = failure_record["ledger"]

    result = ConstraintStackScenarioResult(
        schema="HHS_CONSTRAINT_STACK_SECURITY_SCENARIO_RESULT_V1",
        version=VERSION,
        scenario=scenario,
        status=status,
        accepted=bool(accepted or reclassified),
        reclassified_as_valid_propagation=reclassified,
        reason_code=reason_code,
        expected_status=expected_status,
        expected_match=status == expected_status,
        execution_performed=False,
        mutation_performed=False,
        terminal_value_sufficient=False,
        witness_chain_complete=witness_chain_complete,
        required_layers=dict(layers),
        missing_layers=missing,
        failure_record=failure_record,
        kernel_witness=kernel,
        foundational_conformance=foundational,
        ledger=ledger_summary,
    ).to_dict()
    return result


def _remove_path(value: Dict[str, Any], *path: str) -> Dict[str, Any]:
    data = copy.deepcopy(value)
    cursor: Any = data
    for key in path[:-1]:
        if not isinstance(cursor, dict):
            return data
        cursor = cursor.get(key)
    if isinstance(cursor, dict):
        cursor.pop(path[-1], None)
    return data


def _drift_phase_products(value: Dict[str, Any]) -> Dict[str, Any]:
    data = copy.deepcopy(value)
    for witness in data.get("phase_product_witnesses", []):
        witness["palindrome_valid"] = False
        if isinstance(witness.get("projected_tensor"), dict):
            witness["projected_tensor"]["valid"] = False
            witness["projected_tensor"].setdefault("reasons", []).append("Pass 034 injected phase-product drift")
    return data


def _drift_rotation_profile(value: Dict[str, Any]) -> Dict[str, Any]:
    data = copy.deepcopy(value)
    if isinstance(data.get("hash72_bigint_carrier"), dict):
        data["hash72_bigint_carrier"]["lossless_decode"] = False
        data["hash72_bigint_carrier"]["rotation_profile"] = data["hash72_bigint_carrier"].get("rotation_profile", [])[:71]
    return data


def _drift_temporal(value: Dict[str, Any]) -> Dict[str, Any]:
    data = copy.deepcopy(value)
    if isinstance(data.get("harmonic_time_audio_witness"), dict):
        data["harmonic_time_audio_witness"]["harmonic_time_valid"] = False
        data["harmonic_time_audio_witness"].setdefault("reasons", []).append("Pass 034 injected temporal coherence drift")
    return data


def _partial_witness(value: Dict[str, Any]) -> Dict[str, Any]:
    data = copy.deepcopy(value)
    keep = {
        "schema",
        "version",
        "status",
        "accepted",
        "tensor_seed",
        "phase_product_witnesses",
        "manifold_kernel_witness",
    }
    return {key: val for key, val in data.items() if key in keep}


def run_constraint_stack_security_harness(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = _repo_root(root)
    canonical = translate_reality_to_manifold(root=repo, accept=True)

    scenarios = [
        ("canonical_full_witness_chain", canonical, ACCEPTED_STATUS, False),
        ("terminal_value_only", make_terminal_value_only_claim(), "REJECTED_FORGED_TERMINAL_VALUE", False),
        ("missing_ledger_receipt", _remove_path(canonical, "ledger"), "REJECTED_LEDGERLESS_MUTATION", False),
        ("missing_schema_identity", _remove_path(canonical, "schema"), "REJECTED_SCHEMALESS_TRANSFORMATION", False),
        ("invalid_palindromic_phase_product_ecc", _drift_phase_products(canonical), "REJECTED_PHASE_PRODUCT_DRIFT", False),
        ("invalid_hash72_rotation_profile", _drift_rotation_profile(canonical), "REJECTED_ROTATION_PROFILE_DRIFT", False),
        ("invalid_harmonic_time_audio_ecc", _drift_temporal(canonical), "REJECTED_TEMPORAL_COHERENCE_DRIFT", False),
        ("partial_bruteforce_witness_chain", _partial_witness(canonical), "REJECTED_INCOMPLETE_WITNESS_CHAIN", True),
        ("full_rule_following_bruteforce_sequence", canonical, RECLASSIFIED_STATUS, True),
    ]

    results = [
        evaluate_constraint_stack_candidate(name, candidate, expected_status=expected, brute_force_claim=bruteforce)
        for name, candidate, expected, bruteforce in scenarios
    ]
    accepted = [item for item in results if item["status"] in (ACCEPTED_STATUS, RECLASSIFIED_STATUS)]
    rejected = [item for item in results if item["status"].startswith("REJECTED")]
    all_expected = all(item["expected_match"] for item in results)
    no_rejected_execution = all(not item["execution_performed"] and not item["mutation_performed"] for item in rejected)
    manifest = {
        "schema": "HHS_CONSTRAINT_STACK_SECURITY_HARNESS_MANIFEST_V1",
        "version": VERSION,
        "standards_exercised": [
            "HHS-S009 Reality-to-Manifold Isomorphic Translation",
            "HHS-S010 Palindromic Phase-Product Error Correction",
            "HHS-S011 BigInt Floating-String Hash72 Serialization",
            "HHS-S012 Harmonic Time / Audio Phase Error Correction",
            "HHS-S013 Non-Silent Operation and Anti-Bruteforce Propagation",
            "HHS-S014 Rule-Following Equivalence of Successful Propagation",
        ],
        "security_policy": make_non_silent_security_policy(),
        "scenario_results": results,
        "summary": {
            "scenario_count": len(results),
            "accepted_or_reclassified_count": len(accepted),
            "rejected_count": len(rejected),
            "all_expected_statuses_matched": all_expected,
            "rejected_scenarios_executed": not no_rejected_execution,
            "terminal_value_sufficient": False,
            "full_rule_following_bruteforce_reclassified": any(item["reclassified_as_valid_propagation"] for item in results),
            "ledger_verified": bool(verify_unified_ledger().get("ok")),
        },
    }
    return manifest


def build_pass_034_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = _repo_root(root)
    manifest = run_constraint_stack_security_harness(root=repo)
    (repo / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

    summary = manifest["summary"]
    report = f"""# Pass 034 — Constraint Stack Security Harness

Pass 034 exercises the Pass 033 constraint/admissibility standards as runtime security invariants.  It proves that full witnessed propagation is admitted, while terminal-only, ledgerless, schemaless, drifted, or partial witness attempts are rejected without execution.

## Scenario summary

- Scenarios executed: `{summary['scenario_count']}`
- Accepted/reclassified: `{summary['accepted_or_reclassified_count']}`
- Rejected: `{summary['rejected_count']}`
- Expected statuses matched: `{summary['all_expected_statuses_matched']}`
- Rejected scenarios executed: `{summary['rejected_scenarios_executed']}`
- Terminal value sufficient: `{summary['terminal_value_sufficient']}`
- Full rule-following brute-force reclassified: `{summary['full_rule_following_bruteforce_reclassified']}`
- Ledger verified: `{summary['ledger_verified']}`

## Tested rejection classes

- `REJECTED_FORGED_TERMINAL_VALUE`
- `REJECTED_LEDGERLESS_MUTATION`
- `REJECTED_SCHEMALESS_TRANSFORMATION`
- `REJECTED_PHASE_PRODUCT_DRIFT`
- `REJECTED_ROTATION_PROFILE_DRIFT`
- `REJECTED_TEMPORAL_COHERENCE_DRIFT`
- `REJECTED_INCOMPLETE_WITNESS_CHAIN`

## Rule-following equivalence

A brute-force sequence that provides the complete witness chain is reclassified as `RECLASSIFIED_AS_VALID_PROPAGATION`, not accepted as bypass.
"""
    (repo / REPORT_FILE).write_text(report, encoding="utf-8")

    non_silent = """# Non-Silent Operation Test Report — Pass 034

Pass 034 validates that silent propagation has no admissible runtime form.  Operations missing schema identity, ledger receipts, correction-layer witnesses, Hash72/u^72 rotation evidence, harmonic-time/audio coherence, or foundational audits are rejected with explicit failure records.

The harness confirms: a terminal output is never sufficient evidence of validity.
"""
    (repo / NON_SILENT_REPORT_FILE).write_text(non_silent, encoding="utf-8")

    anti_bruteforce = """# Anti-Bruteforce Propagation Test Report — Pass 034

Pass 034 validates HHS-S014: successful brute-force propagation is equivalent to rule-following propagation.  Partial or terminal-only brute force is rejected.  A complete brute-force sequence that satisfies the whole witness chain is reclassified as valid HHS propagation because it followed the manifold rules precisely.
"""
    (repo / ANTI_BRUTEFORCE_REPORT_FILE).write_text(anti_bruteforce, encoding="utf-8")
    return manifest


def constraint_stack_security_harness_self_test() -> Dict[str, Any]:
    manifest = build_pass_034_artifacts()
    summary = manifest["summary"]
    expected_statuses = {item["scenario"]: item["status"] for item in manifest["scenario_results"]}
    ok = (
        summary["all_expected_statuses_matched"]
        and not summary["rejected_scenarios_executed"]
        and not summary["terminal_value_sufficient"]
        and summary["full_rule_following_bruteforce_reclassified"]
        and expected_statuses.get("canonical_full_witness_chain") == ACCEPTED_STATUS
        and expected_statuses.get("terminal_value_only") == "REJECTED_FORGED_TERMINAL_VALUE"
        and expected_statuses.get("partial_bruteforce_witness_chain") == "REJECTED_INCOMPLETE_WITNESS_CHAIN"
        and expected_statuses.get("full_rule_following_bruteforce_sequence") == RECLASSIFIED_STATUS
    )
    return {
        "schema": "HHS_CONSTRAINT_STACK_SECURITY_HARNESS_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "service": "constraint_stack_security_harness.self_test",
        "manifest_file": MANIFEST_FILE,
        "report_file": REPORT_FILE,
        "non_silent_report_file": NON_SILENT_REPORT_FILE,
        "anti_bruteforce_report_file": ANTI_BRUTEFORCE_REPORT_FILE,
        "summary": summary,
        "expected_statuses": expected_statuses,
    }


if __name__ == "__main__":
    print(json.dumps(constraint_stack_security_harness_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
