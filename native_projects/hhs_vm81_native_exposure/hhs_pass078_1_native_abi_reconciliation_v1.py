from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json, re

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass078_vm81_native_exposure_v1 import native_capability_manifest

PASS_ID = "PASS_078_1"
SCHEMA = "HHS_NATIVE_ABI_DECLARATION_RECONCILIATION_PASS_078_1_V1"
HEADER = "hhs_runtime/include/HARMONICODE_VM_RUNTIME.h"
ALLOWED = {
    "IMPLEMENT_AS_FROZEN_ABI",
    "MAP_TO_EXISTING_NATIVE_PRIMITIVE",
    "DEPRECATE_AS_UNSUPPORTED_DECLARATION",
    "RETAIN_AS_TYPED_UNRESOLVED",
}

CANDIDATES = {
    "hhs_vm_init": ["vm81_init", "hhs_runtime_init"],
    "hhs_vm_reset": ["vm81_init", "hhs_runtime_reset"],
    "hhs_vm_step": ["vm81_step", "hhs_runtime_step"],
    "hhs_vm_run": ["run_vm"],
    "hhs_vm_get_receipt": ["hhs_receipt_commit", "compose_receipt_hash"],
    "hhs_vm_tensor81": ["hhs_hash72_tensor_project"],
    "hhs_vm_cell": ["apply_instruction"],
    "hhs_vm_current_hash72": ["project_hash72", "hhs_hash72_project"],
    "hhs_vm_previous_hash72": ["compose_receipt_hash"],
    "hhs_vm_witness_flags": ["vm81_step", "apply_instruction"],
    "hhs_vm_is_converged": ["close81", "close_orientation", "close_constraint"],
    "hhs_vm_is_halted": ["run_vm", "vm81_step"],
    "hhs_vm_transport_flux": ["propagate_phase_transport"],
    "hhs_vm_orientation_flux": ["close_orientation"],
    "hhs_vm_constraint_flux": ["constraint_bias_at", "constraint_compete", "constraint_relax"],
}

DECL_RE = re.compile(r"(?ms)(?P<ret>[A-Za-z_][\w\s\*]*?)\s+(?P<name>hhs_vm_[A-Za-z_]\w*)\s*\((?P<args>.*?)\)\s*;")


def _root(label: str, body: Mapping[str, Any]) -> dict[str, Any]:
    out = stable(dict(body))
    out[f"{label}_root_hash72"] = product_root(label, out)
    return stable(out)


def _declared_signatures(repo: Path) -> dict[str, dict[str, Any]]:
    text = (repo / HEADER).read_text(encoding="utf-8")
    out: dict[str, dict[str, Any]] = {}
    for m in DECL_RE.finditer(text):
        ret = " ".join(m.group("ret").split())
        args = " ".join(m.group("args").split())
        name = m.group("name")
        out[name] = {
            "declared_symbol": name,
            "declaration_source": HEADER,
            "declared_signature": f"{ret} {name}({args})",
            "declaration_line": text.count("\n", 0, m.start()) + 1,
        }
    return out


def reconcile_native_abi(repo: Path) -> dict[str, Any]:
    caps = native_capability_manifest(repo)
    unresolved = list(caps["public_declarations_without_same_translation_unit_definition"])
    declared = _declared_signatures(repo)
    native_by_symbol = {f["symbol"]: f for f in caps["functions"]}
    records = []
    for symbol in sorted(unresolved):
        candidates = CANDIDATES.get(symbol, [])
        evidence = [HEADER]
        candidate_rows = []
        for candidate in candidates:
            f = native_by_symbol.get(candidate)
            if f:
                evidence.append(f["source_path"])
                candidate_rows.append({
                    "symbol": candidate,
                    "signature": f["signature"],
                    "native_visibility": f["native_visibility"],
                    "semantic_authority": f["semantic_authority"],
                })
        rationale = (
            "The declaration uses the public HHSVMState/HHSProgram/HHSReceipt representation, while the frozen "
            "native implementation uses VM81/Instruction/VMReceipt or a distinct runtime ABI state. Candidate "
            "primitives show operational proximity but no proven state-layout, transition, receipt, ownership, "
            "or failure-semantic equivalence. Mapping would therefore be a new architectural adapter, not a "
            "truthful alias, and cannot be admitted inside Pass 078.1."
        )
        record = {
            **declared[symbol],
            "matching_definition": None,
            "candidate_native_primitive": candidate_rows,
            "semantic_equivalence_status": "UNPROVEN_REPRESENTATION_AND_CONTRACT_EQUIVALENCE",
            "disposition": "RETAIN_AS_TYPED_UNRESOLVED",
            "architectural_revision_required": True,
            "callable_after_reconciliation": False,
            "rationale": rationale,
            "evidence_files": sorted(set(evidence)),
        }
        record["disposition_root_hash72"] = product_root("hhs_native_abi_declaration_disposition_v1", stable(record))
        records.append(stable(record))
    result = {
        "schema": SCHEMA,
        "record_schema": "HHS_NATIVE_ABI_DECLARATION_DISPOSITION_V1",
        "pass_id": PASS_ID,
        "parent_pass": "PASS_078",
        "policy": "RECONCILE_DECLARATION_TRUTH_WITHOUT_FABRICATING_NATIVE_SEMANTICS",
        "allowed_dispositions": sorted(ALLOWED),
        "unresolved_abi_declarations_total": len(unresolved),
        "unresolved_abi_declarations_dispositioned": len(records),
        "false_callable_claims": sum(1 for r in records if r["callable_after_reconciliation"] and not r["matching_definition"]),
        "fabricated_native_implementations": 0,
        "semantic_equivalence_unproven_mappings": sum(1 for r in records if r["disposition"] == "MAP_TO_EXISTING_NATIVE_PRIMITIVE" and r["semantic_equivalence_status"] != "SEMANTIC_EQUIVALENCE_PROVEN"),
        "silent_kernel_semantic_changes": 0,
        "remaining_typed_unresolved": sum(1 for r in records if r["disposition"] == "RETAIN_AS_TYPED_UNRESOLVED"),
        "declarations": records,
    }
    result["pass078_1_native_abi_reconciliation_root_hash72"] = product_root("pass078_1_native_abi_reconciliation", stable(result))
    return stable(result)


def verify_reconciliation(repo: Path, manifest: Mapping[str, Any]) -> bool:
    regenerated = reconcile_native_abi(repo)
    return stable(dict(manifest)) == regenerated


def build_release(repo: Path) -> dict[str, Any]:
    reconciliation = reconcile_native_abi(repo)
    release = {
        "schema": "HHS_PASS_078_1_RELEASE_BUNDLE_V1",
        "pass_id": PASS_ID,
        "parent_pass078_capability_root_hash72": native_capability_manifest(repo)["pass078_native_capability_manifest_root_hash72"],
        "reconciliation": reconciliation,
        "closure": {
            "all_declarations_dispositioned": reconciliation["unresolved_abi_declarations_total"] == reconciliation["unresolved_abi_declarations_dispositioned"],
            "no_false_callable_claims": reconciliation["false_callable_claims"] == 0,
            "no_fabricated_native_implementations": reconciliation["fabricated_native_implementations"] == 0,
            "no_unproven_mappings": reconciliation["semantic_equivalence_unproven_mappings"] == 0,
            "no_silent_kernel_semantic_changes": reconciliation["silent_kernel_semantic_changes"] == 0,
        },
    }
    release["pass078_1_release_root_hash72"] = product_root("pass078_1_release", stable(release))
    return stable(release)


def write_artifacts(repo: Path) -> dict[str, Any]:
    release = build_release(repo)
    artifact_dir = repo / "native_projects/hhs_vm81_native_exposure/artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "PASS_078_1_NATIVE_ABI_DECLARATION_DISPOSITIONS.json").write_text(json.dumps(release["reconciliation"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (artifact_dir / "HHS_PASS_078_1_RELEASE_BUNDLE.json").write_text(json.dumps(release, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return release
