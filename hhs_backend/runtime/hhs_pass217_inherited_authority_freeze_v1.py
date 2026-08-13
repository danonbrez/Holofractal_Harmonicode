"""Pass 217 Iteration 1 inherited-main and capability-inventory freeze.

This module is evidence-only.  It binds the exact inherited Git tree, reuses
the two Pass 214 repository/operation census authorities against that frozen
tree, and projects a fail-closed discovery view for the capabilities that
Pass 217 must preserve and Pass 219 will later consume.  It does not generate
the Genesis ROM, mutate the VM81 nucleus, admit state, or mint Hash72/Hash216
transition authority.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any, Iterator, Mapping, Sequence

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_final_v1 import (
    build_final_cumulative_operation_census,
)
from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import (
    FROZEN_RUNTIME,
    FROZEN_RUNTIME_GIT_BLOB,
)
from hhs_backend.runtime.hhs_pass214_repository_census_v1 import (
    build_repository_census,
)


SCHEMA = "HHS_PASS_217_ITERATION_1_INHERITED_AUTHORITY_FREEZE_V1"
CLASSIFICATION = "HHS_PASS_217_ITERATION_1_BASE_AND_CAPABILITY_INVENTORY_FROZEN"
PASS_NUMBER = 217
ITERATION = 1
BASE_COMMIT = "66c614ae1de0c1b1651451e2c406307a8dee83ed"
BASE_TREE = "4d8c87797d8844b8868f6b412ba45f936731c6c4"
BASE_SUBJECT = "Record Pass 159 authoritative main closure"
MERGE_TARGET = "main"

CONTRACT_PATHS = (
    "HHS_PASS_217_GENESIS_HYDRATION_ROM_BINARY_NORMAL_FORM_CONTRACT.md",
    "HHS_PASS_218_SKIP_DEFAULT_NATIVE_CORPUS_CRAWLER_LINGUISTIC_HYDRATION_CONTRACT.md",
    "HHS_PASS_219_CPP_COMPOUND_SYMBOLIC_CONSTRAINT_RUNTIME_CONTRACT.md",
)

# These are discovery queries, never semantic-equivalence declarations.  Each
# family retains exact matching paths and operation identities from the frozen
# base so later passes can reconcile them rather than reimplement by name.
FOCUS_FAMILIES: tuple[tuple[str, str], ...] = (
    (
        "genesis_binary_normal_form",
        r"genesis|binary[ _-]?normal|hydration[ _-]?rom|logical[ _-]?genesis",
    ),
    (
        "vm81_c_nucleus_and_abi",
        r"vm81|harmonicode_vm_runtime|native[ _-]?abi|c[ _-]?abi|kernel[ _-]?runtime",
    ),
    (
        "hash72_hash216_receipt_lineage",
        r"hash72|hash216|receipt|lineage|ancestry",
    ),
    (
        "vm5184_g243_hydration",
        r"vm5184|g243|hydration|hydrate|continuation",
    ),
    (
        "ordered_xyzw_phase_chirality",
        r"octonion|phase[ _-]?gear|chirality|ordered[ _-]?phase|phase[ _-]?tensor|reciprocal[ _-]?phase",
    ),
    (
        "fibonacci_loshu_magic_tensor",
        r"fibonacci|lo[ _-]?shu|magic[ _-]?square|sudoku[ _-]?tensor",
    ),
    (
        "global_constraint_membranes",
        r"global[ _-]?tensor|constraint[ _-]?membrane|constraint[ _-]?graph|constraint[ _-]?solver|constraint[ _-]?runtime",
    ),
    (
        "golay_rom_correction",
        r"golay|error[ _-]?correction|syndrome|interleav|erasure[ _-]?recovery",
    ),
    (
        "cache_vector_continuation",
        r"cache|vector[ _-]?(store|index)|nearest[ _-]?state|branch[ _-]?predict|compiled[ _-]?rom|delta[ _-]?continuation",
    ),
    (
        "shared_graph_tensor_primitives",
        r"graph[ _-]?kernel|tensor[ _-]?kernel|sparse[ _-]?tensor|graph|tensor",
    ),
    (
        "rna_molecular_constraints",
        r"(^|[^a-z0-9])(rna|nucleotide|toehold|hairpin)([^a-z0-9]|$)|molecular[ _-]?logic",
    ),
    (
        "protein_fold_topology",
        r"(^|[^a-z0-9])(protein|folding)([^a-z0-9]|$)|protein[ _-]?fold|contact[ _-]?(map|tensor)",
    ),
    (
        "e6_exact_symmetry",
        r"(^|[^a-z0-9])e6([^a-z0-9]|$)|root[ _-]?system|cartan|dynkin",
    ),
    (
        "cpp_constraint_translation_surface",
        r"c\+\+|cpp|compound[ _-]?runtime|constraint[ _-]?program|module[ _-]?registry|high[ _-]?to[ _-]?low",
    ),
)


class Pass217FreezeError(RuntimeError):
    """Raised when the bound Iteration 1 snapshot cannot be reproduced."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _run(
    cwd: Path,
    args: Sequence[str],
    *,
    allow_no_match: bool = False,
) -> bytes:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode == 0:
        return completed.stdout
    if allow_no_match and completed.returncode == 1:
        return b""
    detail = completed.stderr.decode("utf-8", "replace").strip()
    raise Pass217FreezeError(
        f"PASS217_ITERATION1_COMMAND_FAILED:{' '.join(args)}:{detail}"
    )


def _git_text(root: Path, *args: str) -> str:
    return _run(root, ("git", "-C", str(root), *args)).decode().strip()


@contextmanager
def _materialized_snapshot(root: Path, commit: str) -> Iterator[Path]:
    """Materialize an exact local Git object without consulting the network."""

    with tempfile.TemporaryDirectory(prefix="hhs-pass217-i1-") as temp:
        snapshot = Path(temp) / "snapshot"
        _run(
            root,
            (
                "git",
                "clone",
                "--quiet",
                "--shared",
                "--no-checkout",
                str(root),
                str(snapshot),
            ),
        )
        _run(
            snapshot,
            (
                "git",
                "-C",
                str(snapshot),
                "checkout",
                "--quiet",
                "--detach",
                commit,
            ),
        )
        yield snapshot


def _blob_record(snapshot: Path, path: str) -> dict[str, Any]:
    blob = _git_text(snapshot, "rev-parse", f"HEAD:{path}")
    content = (snapshot / path).read_bytes()
    return {
        "path": path,
        "git_blob": blob,
        "sha256": sha256(content).hexdigest(),
        "size_bytes": len(content),
    }


def _grep_paths(snapshot: Path, pattern: str) -> set[str]:
    raw = _run(
        snapshot,
        (
            "git",
            "-C",
            str(snapshot),
            "grep",
            "-I",
            "-i",
            "-E",
            "-l",
            pattern,
            "--",
        ),
        allow_no_match=True,
    )
    return {
        line.decode("utf-8", "surrogateescape")
        for line in raw.splitlines()
        if line
    }


def _focus_inventory(
    snapshot: Path,
    path_census: Sequence[Mapping[str, Any]],
    operations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    blob_rows = {
        str(row["path"]): row
        for row in path_census
        if row.get("object_type") == "blob"
    }
    result: dict[str, Any] = {}
    for family, pattern in FOCUS_FAMILIES:
        matcher = re.compile(pattern, re.IGNORECASE)
        matched_paths = _grep_paths(snapshot, pattern)
        matched_paths.update(
            path for path in blob_rows if matcher.search(path.replace("-", "_"))
        )
        matched_paths &= set(blob_rows)
        matched_operations = [
            row
            for row in operations
            if matcher.search(
                " ".join(
                    (
                        str(row.get("path", "")),
                        str(row.get("raw_name", "")),
                        str(row.get("normalized_semantic_name", "")),
                        str(row.get("kind", "")),
                    )
                )
            )
        ]
        dispositions = Counter(
            str(blob_rows[path]["disposition"]) for path in matched_paths
        )
        callable_count = dispositions["SCANNED_CALLABLE"]
        if callable_count:
            status = "IMPLEMENTATION_CANDIDATES_DISCOVERED_UNVERIFIED"
        elif matched_paths:
            status = "CONTRACT_DATA_OR_EVIDENCE_DISCOVERED"
        else:
            status = "NOT_DISCOVERED_ON_BOUND_BASE"
        result[family] = {
            "query": pattern,
            "status": status,
            "semantic_equivalence_proven": False,
            "authority_promoted": False,
            "matched_tracked_file_count": len(matched_paths),
            "matched_operation_identity_count": len(matched_operations),
            "callable_candidate_file_count": callable_count,
            "disposition_counts": dict(sorted(dispositions.items())),
            "tracked_path_examples": sorted(matched_paths)[:4],
            "operation_examples": [
                {
                    "kind": str(row["kind"]),
                    "path": str(row["path"]),
                    "raw_name": str(row["raw_name"]),
                    "operation_key": str(row["operation_key"]),
                }
                for row in sorted(
                    matched_operations,
                    key=lambda item: (
                        str(item["path"]),
                        int(item["line"]),
                        str(item["raw_name"]),
                    ),
                )[:4]
            ],
        }
    return result


def _transition_window(
    path_census: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    by_pass: dict[int, list[str]] = {number: [] for number in range(213, 220)}
    observed: set[int] = set()
    for row in path_census:
        if row.get("object_type") != "blob":
            continue
        number = row["origin"].get("pass_number")
        if number is None:
            continue
        value = int(number)
        observed.add(value)
        if value in by_pass:
            by_pass[value].append(str(row["path"]))
    return {
        "observed_numbered_passes": sorted(observed),
        "maximum_numbered_pass_path": max(observed) if observed else None,
        "required_transition_window": {
            f"pass_{number}": {
                "tracked_blob_count": len(by_pass[number]),
                "path_examples": sorted(by_pass[number])[:6],
                "implementation_or_closure_inferred_from_path_count": False,
            }
            for number in range(213, 220)
        },
    }


def build_inherited_authority_freeze(
    repository_root: Path | str,
    *,
    base_ref: str = BASE_COMMIT,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    if not (root / ".git").exists():
        raise Pass217FreezeError("PASS217_ITERATION1_GIT_METADATA_REQUIRED")
    commit = _git_text(root, "rev-parse", f"{base_ref}^{{commit}}")
    tree = _git_text(root, "rev-parse", f"{commit}^{{tree}}")
    subject = _git_text(root, "show", "-s", "--format=%s", commit)
    if commit != BASE_COMMIT:
        raise Pass217FreezeError(f"PASS217_ITERATION1_BASE_COMMIT_MISMATCH:{commit}")
    if tree != BASE_TREE:
        raise Pass217FreezeError(f"PASS217_ITERATION1_BASE_TREE_MISMATCH:{tree}")
    if subject != BASE_SUBJECT:
        raise Pass217FreezeError(f"PASS217_ITERATION1_BASE_SUBJECT_MISMATCH:{subject}")

    with _materialized_snapshot(root, commit) as snapshot:
        repository_census = build_repository_census(snapshot, source_ref=commit)
        operation_census = build_final_cumulative_operation_census(
            snapshot,
            source_ref=commit,
        )
        protected_runtime = _blob_record(snapshot, FROZEN_RUNTIME)
        if protected_runtime["git_blob"] != FROZEN_RUNTIME_GIT_BLOB:
            raise Pass217FreezeError(
                "PASS217_ITERATION1_PROTECTED_RUNTIME_BLOB_MISMATCH:"
                + str(protected_runtime["git_blob"])
            )
        contracts = [_blob_record(snapshot, path) for path in CONTRACT_PATHS]
        focus = _focus_inventory(
            snapshot,
            repository_census["path_census"],
            operation_census["operations"],
        )
        pass_inventory = _transition_window(repository_census["path_census"])

    transition = pass_inventory["required_transition_window"]
    pass_215_present = transition["pass_215"]["tracked_blob_count"] > 0
    pass_216_present = transition["pass_216"]["tracked_blob_count"] > 0
    predecessor_surfaces_present = pass_215_present and pass_216_present
    inheritance_status = (
        "PREDECESSOR_SURFACES_PRESENT_CLOSURE_STILL_REQUIRES_PROOF"
        if predecessor_surfaces_present
        else "HOLD_FOR_PASS_215_216_AUTHORITATIVE_RECONCILIATION"
    )

    repository_summary = repository_census["summary"]
    operation_summary = operation_census["summary"]
    body: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "base": {
            "branch_role": "AUTHORITATIVE_MAIN_SNAPSHOT",
            "commit": commit,
            "tree": tree,
            "subject": subject,
            "merge_target": MERGE_TARGET,
        },
        "contracts": contracts,
        "protected_authority": {
            "c_vm81_runtime_nucleus": protected_runtime,
            "expected_git_blob": FROZEN_RUNTIME_GIT_BLOB,
            "semantics_modified": False,
            "abi_modified": False,
        },
        "repository_tree_inventory": {
            "source_commit": repository_summary["source_commit"],
            "source_tree": repository_summary["source_tree"],
            "roots": repository_summary["roots"],
            "coverage": repository_summary["coverage"],
            "disposition_counts": repository_summary["disposition_counts"],
            "language_counts": repository_summary["language_counts"],
            "origin_counts": repository_summary["origin_counts"],
            "optimization_family_counts": repository_summary[
                "optimization_family_counts"
            ],
            "modality_counts": repository_summary["modality_counts"],
            "static_discovery_only": True,
        },
        "cumulative_operation_inventory": {
            "schema": operation_census["schema"],
            "classification": operation_census["classification"],
            "census_sha256": operation_census["census_sha256"],
            "source_commit": operation_summary["source_commit"],
            "source_tree": operation_summary["source_tree"],
            "coverage": operation_summary["coverage"],
            "family_counts": operation_summary["family_counts"],
            "reuse_accounting": operation_summary["reuse_accounting"],
            "semantic_accounting": operation_summary["semantic_accounting"],
            "python_exposure_counts": operation_summary["python_exposure_counts"],
            "known_opcode_family_anchors": operation_summary[
                "known_opcode_family_anchors"
            ],
            "parse_error_count": operation_summary["parse_error_count"],
            "automatic_semantic_collapse_performed": False,
        },
        "numbered_pass_inventory": pass_inventory,
        "pass219_preparation_inventory": {
            "classification": "DISCOVERY_ONLY_REQUIRES_SEMANTIC_RECONCILIATION",
            "families": focus,
            "families_sha256": _digest(focus),
            "pass219_runtime_implementation_started": False,
            "pass219_authority_promoted": False,
        },
        "inheritance_gate": {
            "contract_requires_complete_inheritance_through_pass": 216,
            "pass_215_surfaces_present_on_bound_base": pass_215_present,
            "pass_216_surfaces_present_on_bound_base": pass_216_present,
            "path_presence_proves_implementation_or_closure": False,
            "status": inheritance_status,
            "contract_schema_and_inventory_preparation_may_continue": True,
            "genesis_rom_or_runtime_authority_promotion_allowed": False,
        },
        "claim_boundary": {
            "iteration1_inventory_complete_for_bound_base": True,
            "repository_tree_reused_from_pass214_authority": True,
            "operation_inventory_reused_from_pass214_authority": True,
            "discovered_names_prove_semantic_equivalence": False,
            "runtime_mutation_performed": False,
            "protected_c_runtime_modified": False,
            "canonical_authority_promoted": False,
            "genesis_rom_generated": False,
            "golay_physical_rom_generated": False,
            "migration_started": False,
            "authoritative_hash72_transition_receipt_minted": False,
            "authoritative_hash216_transition_minted": False,
            "pass217_implementation_complete": False,
            "pass219_implementation_complete": False,
        },
        "next_action": (
            "Preserve this base freeze; reconcile authoritative Pass 215/216 "
            "inheritance before runtime promotion while preparing Pass 217 "
            "Iteration 2 machine contracts, schemas, and reference vectors."
        ),
    }
    body["freeze_sha256"] = _digest(body)
    validate_inherited_authority_freeze(body)
    return body


def validate_inherited_authority_freeze(value: Mapping[str, Any]) -> None:
    data = json.loads(json.dumps(value))
    supplied = data.pop("freeze_sha256", None)
    if supplied != _digest(data):
        raise Pass217FreezeError("PASS217_ITERATION1_FREEZE_SHA256_MISMATCH")
    if data.get("schema") != SCHEMA:
        raise Pass217FreezeError("PASS217_ITERATION1_SCHEMA_MISMATCH")
    if data.get("classification") != CLASSIFICATION:
        raise Pass217FreezeError("PASS217_ITERATION1_CLASSIFICATION_MISMATCH")
    if data.get("pass") != PASS_NUMBER or data.get("iteration") != ITERATION:
        raise Pass217FreezeError("PASS217_ITERATION1_COORDINATE_MISMATCH")
    if data["base"]["commit"] != BASE_COMMIT or data["base"]["tree"] != BASE_TREE:
        raise Pass217FreezeError("PASS217_ITERATION1_BASE_IDENTITY_MISMATCH")
    protected = data["protected_authority"]
    if protected["c_vm81_runtime_nucleus"]["git_blob"] != FROZEN_RUNTIME_GIT_BLOB:
        raise Pass217FreezeError("PASS217_ITERATION1_RUNTIME_BLOB_MISMATCH")
    anchors = data["cumulative_operation_inventory"][
        "known_opcode_family_anchors"
    ]
    if not anchors["all_satisfied"] or anchors["raw_known_opcode_identity_minimum"] != 137:
        raise Pass217FreezeError("PASS217_ITERATION1_OPCODE_ANCHOR_MISMATCH")
    families = data["pass219_preparation_inventory"]["families"]
    if set(families) != {name for name, _ in FOCUS_FAMILIES}:
        raise Pass217FreezeError("PASS217_ITERATION1_FOCUS_FAMILY_SET_MISMATCH")
    if data["pass219_preparation_inventory"]["families_sha256"] != _digest(families):
        raise Pass217FreezeError("PASS217_ITERATION1_FOCUS_FAMILY_ROOT_MISMATCH")
    claims = data["claim_boundary"]
    forbidden_true = (
        "runtime_mutation_performed",
        "protected_c_runtime_modified",
        "canonical_authority_promoted",
        "genesis_rom_generated",
        "golay_physical_rom_generated",
        "migration_started",
        "authoritative_hash72_transition_receipt_minted",
        "authoritative_hash216_transition_minted",
        "pass217_implementation_complete",
        "pass219_implementation_complete",
    )
    if any(claims[key] for key in forbidden_true):
        raise Pass217FreezeError("PASS217_ITERATION1_AUTHORITY_OVERCLAIM")


def write_inherited_authority_freeze(
    value: Mapping[str, Any],
    output: Path | str,
) -> None:
    validate_inherited_authority_freeze(value)
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(_canonical(value) + b"\n")


def load_inherited_authority_freeze(path: Path | str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_inherited_authority_freeze(data)
    return data


def verify_inherited_authority_freeze(
    repository_root: Path | str,
    evidence_path: Path | str,
) -> dict[str, Any]:
    recorded = load_inherited_authority_freeze(evidence_path)
    rebuilt = build_inherited_authority_freeze(repository_root)
    if recorded != rebuilt:
        raise Pass217FreezeError("PASS217_ITERATION1_REBUILD_MISMATCH")
    return rebuilt
