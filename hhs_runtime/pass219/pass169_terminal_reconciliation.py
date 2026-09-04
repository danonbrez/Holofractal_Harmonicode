"""Pass 219 I164 fail-closed reconciliation of remaining Pass169 terminal obligations.

This module does not manufacture missing Pass169 authority.  It binds the frozen
I161-I163 evidence, inventories exact HARMONICODE fixtures that remain available
in the repository, checks the contract-required canonical corpus/artifacts and
public CLI/HTTP surfaces, and refuses the Pass169 terminal classification until
all required evidence is actually present.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

PASS = 219
ITERATION = "I164"
BASE_MAIN = "42b614f5fbba3e90aa2571c138c53c25591326a2"
FIXED_RESOLUTION = "72^42=5184^21"
PASS169_CONTRACT_ID = "HHS-P169-HSAE-VM81-ESCPR"
PASS169_TERMINAL_CLASSIFICATION = (
    "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_"
    "VM81_EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME_VERIFIED"
)

PASS169_CONTRACT_PATH = Path(
    "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_VM81_"
    "EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME.md"
)
PASS168_COMPLETION_RECEIPT_PATH = Path("HHS_PASS_168_COMPLETION_RECEIPT.json")
PASS169_CANONICAL_CORPUS_PATH = Path("HHS_PASS_169_CANONICAL_ALGEBRA_CORPUS.harmonicode")

I161_EVIDENCE_PATH = Path("evidence/pass219/PASS_219_I161_FEATURE_VALIDATION_33823367993.json")
I162_EVIDENCE_PATH = Path("evidence/pass219/PASS_219_I162_FEATURE_VALIDATION_33836940374.json")
I163_EVIDENCE_PATH = Path("evidence/pass219/PASS_219_I163_FEATURE_VALIDATION_33866718853.json")

REQUIRED_PASS169_ARTIFACTS: Tuple[str, ...] = (
    "HHS_PASS_169_CONTRACT.md",
    "HHS_PASS_169_AUTHORITY_BINDING.json",
    "HHS_PASS_169_CANONICAL_ALGEBRA_CORPUS.harmonicode",
    "HHS_PASS_169_SOURCE_MANIFEST.json",
    "HHS_PASS_169_SYMBOL_REGISTRY.json",
    "HHS_PASS_169_TYPE_REGISTRY.json",
    "HHS_PASS_169_CONSTRAINT_GRAPH.json",
    "HHS_PASS_169_HARMONIC_FUNCTION_DEFINITIONS.json",
    "HHS_PASS_169_EXACT_VALUE_PROFILE.json",
    "HHS_PASS_169_RUNTIME_CALL_MAP.json",
    "HHS_PASS_169_VM81_ADMISSION_SCHEMA.json",
    "HHS_PASS_169_HASH72_RECEIPT_SCHEMA.json",
    "HHS_PASS_169_HASH216_IDENTITY_SCHEMA.json",
    "HHS_PASS_169_TEST_MATRIX.json",
    "HHS_PASS_169_NEGATIVE_TEST_MATRIX.json",
    "HHS_PASS_169_IMPLEMENTATION_REPORT.md",
    "HHS_PASS_169_VALIDATION_REPORT.md",
    "HHS_PASS_169_COMPLETION_RECEIPT.json",
)

REQUIRED_CLI_OPERATIONS: Tuple[str, ...] = (
    "hhs algebra status",
    "hhs algebra source",
    "hhs algebra tokens",
    "hhs algebra ast",
    "hhs algebra symbols",
    "hhs algebra constraints",
    "hhs algebra inspect <node>",
    "hhs algebra typecheck",
    "hhs algebra normalize",
    "hhs algebra prove",
    "hhs algebra prove --constraint <id>",
    "hhs algebra evaluate --candidate",
    "hhs algebra admit <candidate-id>",
    "hhs algebra commit <candidate-id>",
    "hhs algebra receipt <transition-id>",
    "hhs algebra replay <transition-id>",
    "hhs algebra reverse <transition-id>",
    "hhs algebra divergence <transition-id>",
    "hhs algebra export-proof <transition-id>",
    "hhs algebra validate",
)

REQUIRED_HTTP_ENDPOINTS: Tuple[Tuple[str, str], ...] = (
    ("GET", "/v1/algebra"),
    ("POST", "/v1/algebra/sources"),
    ("GET", "/v1/algebra/sources/{source_id}"),
    ("GET", "/v1/algebra/sources/{source_id}/tokens"),
    ("GET", "/v1/algebra/sources/{source_id}/ast"),
    ("GET", "/v1/algebra/sources/{source_id}/constraints"),
    ("POST", "/v1/algebra/sources/{source_id}/typecheck"),
    ("POST", "/v1/algebra/sources/{source_id}/normalize"),
    ("POST", "/v1/algebra/sources/{source_id}/candidates"),
    ("GET", "/v1/algebra/candidates/{candidate_id}"),
    ("POST", "/v1/algebra/candidates/{candidate_id}/validate"),
    ("POST", "/v1/algebra/candidates/{candidate_id}/commit"),
    ("GET", "/v1/algebra/proofs/{proof_id}"),
    ("GET", "/v1/algebra/transitions/{transition_id}"),
    ("GET", "/v1/algebra/transitions/{transition_id}/receipt"),
    ("POST", "/v1/algebra/transitions/{transition_id}/replay"),
    ("POST", "/v1/algebra/transitions/{transition_id}/reverse"),
)

# These exact fixtures are recoverable repository evidence.  I164 deliberately
# does not relabel any one of them (or their concatenation) as the missing
# Pass169 canonical corpus without an authoritative byte-preservation receipt.
RECOVERABLE_HARMONICODE_FIXTURES: Tuple[str, ...] = (
    "contracts/pass219/PASS_219_NATIVE_UNIVERSAL_CONSTRAINT_ENVELOPE_1_8_0.harmonicode",
    "contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode",
    "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode",
    "contracts/pass219/PASS_219_DENOMINATOR_MAGNITUDE_PROJECTION_1_21_8.harmonicode",
)

_CODE_SUFFIXES = {".py", ".c", ".h", ".cc", ".cpp", ".hpp", ".js", ".mjs", ".ts", ".tsx"}
_EXCLUDED_SCAN_DIRS = {".git", "docs", "contracts", "evidence", "artifacts", "node_modules", ".venv", "venv"}


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _fixture_record(root: Path, relative_path: str) -> Dict[str, Any]:
    path = root / relative_path
    if not path.is_file():
        return {
            "path": relative_path,
            "present": False,
            "qualifies_as_pass169_canonical_corpus": False,
        }
    data = path.read_bytes()
    return {
        "path": relative_path,
        "present": True,
        "bytes": len(data),
        "sha256": sha256(data).hexdigest(),
        "qualifies_as_pass169_canonical_corpus": False,
    }


def _iter_code_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in _CODE_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if any(part in _EXCLUDED_SCAN_DIRS for part in rel.parts):
            continue
        yield path


def _scan_runtime_surfaces(root: Path) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    cli_hits: Dict[str, List[str]] = {operation: [] for operation in REQUIRED_CLI_OPERATIONS}
    http_hits: Dict[str, List[str]] = {
        f"{method} {endpoint}": [] for method, endpoint in REQUIRED_HTTP_ENDPOINTS
    }
    for path in _iter_code_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = _relative(root, path)
        for operation in REQUIRED_CLI_OPERATIONS:
            if operation in text:
                cli_hits[operation].append(rel)
        for method, endpoint in REQUIRED_HTTP_ENDPOINTS:
            key = f"{method} {endpoint}"
            # Requiring the route literal in executable code prevents prose/docs
            # from being mistaken for a served endpoint.  Method presence is
            # reported separately through the key and can be strengthened by a
            # later concrete route implementation.
            if endpoint in text:
                http_hits[key].append(rel)
    return cli_hits, http_hits


def _frozen_evidence(root: Path) -> Dict[str, Any]:
    i161 = _load_json(root / I161_EVIDENCE_PATH)
    i162 = _load_json(root / I162_EVIDENCE_PATH)
    i163 = _load_json(root / I163_EVIDENCE_PATH)

    i161_ok = (
        i161.get("result") == "PASS"
        and i161.get("typed_graph_transition", {}).get("after", {}).get("proved") == 10
        and i161.get("typed_graph_transition", {}).get("after", {}).get("unresolved") == 0
        and i161.get("semantic_guards", {}).get("scalar_zero_equals_scalar_one") is False
        and i161.get("semantic_guards", {}).get("floating_point_canonical_authority") is False
    )
    i162_runtime = i162.get("runtime_execution", {})
    i162_ok = all(
        i162_runtime.get(key) is True
        for key in (
            "exact_vm81_admission_verified",
            "atomic_commit_verified",
            "hash72_receipt_verified",
            "hash216_proof_identity_verified",
            "deterministic_replay_verified",
            "source_reconstruction_verified",
        )
    ) and i162.get("semantic_guards", {}).get("floating_point_authority") is False

    i163_reverse = i163.get("reverse_model", {})
    i163_cross = i163.get("cross_architecture", {})
    i163_ok = (
        i163_reverse.get("pass159_reverse_transition_receipt_verified") is True
        and i163_reverse.get("pass159_reverse_transition_deterministic") is True
        and i163_reverse.get("vm81_prior_transaction_state_restore_verified") is True
        and i163_reverse.get("hash72_ring_prior_state_restore_verified") is True
        and i163_cross.get("records_identical") is True
        and i163.get("authority", {}).get("interpreter_compiler_equality_verified") is True
        and i163.get("authority", {}).get("floating_point_authority") is False
    )

    return {
        "i161": {"path": I161_EVIDENCE_PATH.as_posix(), "verified": i161_ok},
        "i162": {"path": I162_EVIDENCE_PATH.as_posix(), "verified": i162_ok},
        "i163": {"path": I163_EVIDENCE_PATH.as_posix(), "verified": i163_ok},
        "all_frozen_evidence_verified": bool(i161_ok and i162_ok and i163_ok),
    }


def build_i164_pass169_terminal_reconciliation(repo_root: str | Path = ".") -> Dict[str, Any]:
    root = Path(repo_root).resolve()
    contract_path = root / PASS169_CONTRACT_PATH
    contract_text = contract_path.read_text(encoding="utf-8") if contract_path.is_file() else ""
    contract_bound = PASS169_CONTRACT_ID in contract_text and PASS169_TERMINAL_CLASSIFICATION in contract_text

    frozen = _frozen_evidence(root)
    corpus_present = (root / PASS169_CANONICAL_CORPUS_PATH).is_file()
    artifact_presence = {
        path: (root / path).is_file() for path in REQUIRED_PASS169_ARTIFACTS
    }
    missing_artifacts = [path for path, present in artifact_presence.items() if not present]

    cli_hits, http_hits = _scan_runtime_surfaces(root)
    cli_complete = all(bool(paths) for paths in cli_hits.values())
    http_complete = all(bool(paths) for paths in http_hits.values())

    pass168_receipt_path = root / PASS168_COMPLETION_RECEIPT_PATH
    pass168_resolved = False
    pass168_receipt: Dict[str, Any] | None = None
    if pass168_receipt_path.is_file():
        try:
            pass168_receipt = _load_json(pass168_receipt_path)
            pass168_resolved = bool(
                pass168_receipt.get("terminal_verified") is True
                or pass168_receipt.get("verified") is True
            )
        except (json.JSONDecodeError, OSError):
            pass168_receipt = None

    fixtures = [_fixture_record(root, path) for path in RECOVERABLE_HARMONICODE_FIXTURES]

    terminal_conditions = {
        "full_source_corpus_preserved": corpus_present,
        "all_source_symbols_distinguishable": corpus_present and artifact_presence.get("HHS_PASS_169_SYMBOL_REGISTRY.json", False),
        "complete_constraint_graph_executable": frozen["i161"]["verified"] and frozen["i162"]["verified"],
        "exact_numeric_authority_demonstrated": frozen["i162"]["verified"],
        "symbolic_harmonic_functions_registered": artifact_presence.get("HHS_PASS_169_HARMONIC_FUNCTION_DEFINITIONS.json", False),
        "O_not_Pi_symbol_separation_registered": artifact_presence.get("HHS_PASS_169_SYMBOL_REGISTRY.json", False),
        "no_ieee_canonical_authority": frozen["all_frozen_evidence_verified"],
        "canonical_computation_through_runtime_abi": frozen["i162"]["verified"],
        "vm81_admission_and_commit_verified": frozen["i162"]["verified"],
        "hash72_receipts_verified": frozen["i162"]["verified"],
        "hash216_identities_verified": frozen["i162"]["verified"],
        "interpreter_compiler_agreement_verified": frozen["i163"]["verified"],
        "deterministic_replay_verified": frozen["i162"]["verified"],
        "reverse_execution_restores_prior_state": frozen["i163"]["verified"],
        "cross_architecture_evidence_matches": frozen["i163"]["verified"],
        "pass168_parent_resolved": pass168_resolved,
    }

    blockers: List[str] = []
    if not contract_bound:
        blockers.append("PASS169_CONTRACT_ID_OR_TERMINAL_CLASSIFICATION_NOT_BOUND")
    if not corpus_present:
        blockers.append("PASS169_CANONICAL_CORPUS_ABSENT")
    if missing_artifacts:
        blockers.append("PASS169_REQUIRED_ARTIFACT_SET_INCOMPLETE")
    if not cli_complete:
        blockers.append("PASS169_REQUIRED_CLI_SURFACE_INCOMPLETE")
    if not http_complete:
        blockers.append("PASS169_REQUIRED_HTTP_SURFACE_INCOMPLETE")
    if not pass168_resolved:
        blockers.append("PASS168_TERMINAL_PARENT_RECEIPT_UNRESOLVED")
    if not frozen["all_frozen_evidence_verified"]:
        blockers.append("I161_I163_FROZEN_EVIDENCE_INVALID")

    terminal_verified = bool(
        contract_bound
        and not blockers
        and all(terminal_conditions.values())
        and all(artifact_presence.values())
        and cli_complete
        and http_complete
    )

    return {
        "schema": "HHS_PASS219_I164_PASS169_TERMINAL_RECONCILIATION_V1",
        "pass": PASS,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "fixed_resolution": FIXED_RESOLUTION,
        "contract": {
            "path": PASS169_CONTRACT_PATH.as_posix(),
            "id": PASS169_CONTRACT_ID,
            "terminal_classification": PASS169_TERMINAL_CLASSIFICATION,
            "bound": contract_bound,
        },
        "frozen_evidence": frozen,
        "canonical_corpus": {
            "required_path": PASS169_CANONICAL_CORPUS_PATH.as_posix(),
            "present": corpus_present,
            "reconstruction_from_partial_fixtures_authorized": False,
            "recoverable_exact_fixtures": fixtures,
        },
        "required_artifacts": {
            "presence": artifact_presence,
            "missing": missing_artifacts,
            "complete": not missing_artifacts,
        },
        "public_surfaces": {
            "cli": {
                "complete": cli_complete,
                "required_operations": list(REQUIRED_CLI_OPERATIONS),
                "implementation_hits": cli_hits,
            },
            "http": {
                "complete": http_complete,
                "required_endpoints": [f"{method} {endpoint}" for method, endpoint in REQUIRED_HTTP_ENDPOINTS],
                "implementation_hits": http_hits,
            },
        },
        "pass168_parent": {
            "completion_receipt_path": PASS168_COMPLETION_RECEIPT_PATH.as_posix(),
            "receipt_present": pass168_receipt_path.is_file(),
            "resolved": pass168_resolved,
        },
        "terminal_conditions": terminal_conditions,
        "blockers": blockers,
        "pass169_terminal_contract_verified": terminal_verified,
        "authority": {
            "new_vm81_mutation_authority": False,
            "new_hash72_mint_authority": False,
            "hash216_persistence_authority": False,
            "floating_point_canonical_authority": False,
            "partial_source_relabeling_as_canonical_corpus": False,
        },
        "next_boundary": (
            "PASS169_CANONICAL_CORPUS_AND_GENERAL_PUBLIC_SURFACE_CLOSURE"
            if not terminal_verified
            else "PASS169_TERMINAL_CLOSURE_VERIFIED"
        ),
    }


def i164_pass169_terminal_reconciliation_self_test(repo_root: str | Path = ".") -> Dict[str, Any]:
    report = build_i164_pass169_terminal_reconciliation(repo_root)
    if not report["contract"]["bound"]:
        raise AssertionError("Pass169 contract binding missing")
    if not report["frozen_evidence"]["all_frozen_evidence_verified"]:
        raise AssertionError("I161-I163 frozen evidence no longer verifies")
    if report["authority"]["partial_source_relabeling_as_canonical_corpus"]:
        raise AssertionError("partial source fixture promoted to canonical Pass169 corpus")
    if report["authority"]["floating_point_canonical_authority"]:
        raise AssertionError("floating-point canonical authority introduced")
    return report


__all__ = [
    "build_i164_pass169_terminal_reconciliation",
    "i164_pass169_terminal_reconciliation_self_test",
]
