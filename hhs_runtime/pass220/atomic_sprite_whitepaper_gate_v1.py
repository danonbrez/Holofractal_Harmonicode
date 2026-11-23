"""Pass 220: dual-whitepaper corpus gate for atomic/neural sprite candidates.

Source binding and exact-parameter checks are preconditions, not proof that
unformalized natural-language statements have been mechanically established.
Canonical mutation remains delegated to the inherited signed VM81 membrane.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

CORPUS_DIRS = ("whitepapers", "docs/whitepapers")
STATUS = frozenset((
    "CANONICAL_VERBATIM", "DEVELOPMENT_VERBATIM", "EXECUTED_EXACT",
    "HHS_NATIVE_SEMANTIC", "REFERENCE_ONLY",
))
EXECUTION_ELIGIBLE = frozenset(("EXECUTED_EXACT", "HHS_NATIVE_SEMANTIC"))
SCHEMA = "HHS_PASS220_ATOMIC_SPRITE_DUAL_WHITEPAPER_GLOBAL_GATE_V1"


class CorpusConstraintError(ValueError):
    """Fail-closed corpus or parameter binding rejection."""


def _canonical(value: Any, path: str, *, projection: bool = False) -> Any:
    if isinstance(value, float):
        if not projection:
            raise CorpusConstraintError(f"FLOAT_CANONICAL_REJECTED:{path}")
        if not __import__("math").isfinite(value):
            raise CorpusConstraintError(f"NONFINITE_PROJECTION_REJECTED:{path}")
        return {"projection_float": repr(value)}
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, Mapping):
        if any(not isinstance(k, str) for k in value):
            raise CorpusConstraintError(f"NONTEXT_KEY_REJECTED:{path}")
        return {k: _canonical(v, f"{path}.{k}", projection=projection)
                for k, v in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_canonical(v, f"{path}[{i}]", projection=projection)
                for i, v in enumerate(value)]
    raise CorpusConstraintError(f"UNTYPED_VALUE_REJECTED:{path}:{type(value).__name__}")


def _digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def corpus_snapshot(repo_root: Path | str) -> dict[str, Any]:
    """Read every regular corpus file and bind both complete directory trees."""
    base = Path(repo_root).resolve()
    trees: dict[str, Any] = {}
    for dirname in CORPUS_DIRS:
        folder = base / dirname
        if not folder.is_dir() or folder.is_symlink():
            raise CorpusConstraintError(f"CORPUS_MISSING:{dirname}")
        files: dict[str, str] = {}
        for path in sorted(folder.rglob("*")):
            if path.is_symlink():
                raise CorpusConstraintError(f"SYMLINK_CORPUS_REJECTED:{path}")
            if path.is_file():
                key = path.relative_to(base).as_posix()
                files[key] = sha256(path.read_bytes()).hexdigest()
        if not files:
            raise CorpusConstraintError(f"EMPTY_CORPUS_REJECTED:{dirname}")
        trees[dirname] = {"file_count": len(files), "tree_sha256": _digest(files), "files": files}
    roots = {k: {"file_count": v["file_count"], "tree_sha256": v["tree_sha256"]}
             for k, v in trees.items()}
    return {"corpus_dirs": CORPUS_DIRS, "roots": roots,
            "bundle_sha256": _digest(roots), "files": {
                k: sha for tree in trees.values() for k, sha in tree["files"].items()
            }}


def bind_global_parameters(
    repo_root: Path | str,
    parameters: Mapping[str, Mapping[str, Any]],
    *,
    expected_bundle_sha256: str,
) -> dict[str, Any]:
    """Bind EVERY supplied parameter to both corpus roots and a typed source.

    This is a fail-closed *candidate* gate. Native theorem/equation checks and
    signed VM81 environmental admission must still run at their own boundary.
    """
    snap = corpus_snapshot(repo_root)
    if not isinstance(expected_bundle_sha256, str) or snap["bundle_sha256"] != expected_bundle_sha256:
        raise CorpusConstraintError("STALE_OR_UNBOUND_WHITEPAPER_CORPUS")
    if not isinstance(parameters, Mapping) or not parameters:
        raise CorpusConstraintError("EMPTY_PARAMETER_SET_REJECTED")
    bound: dict[str, Any] = {}
    for name, binding in sorted(parameters.items()):
        if not isinstance(name, str) or not name or not isinstance(binding, Mapping):
            raise CorpusConstraintError("UNTYPED_PARAMETER_REJECTED")
        if set(binding) != {"value", "kind", "source_paths", "status", "role", "constraint_id"}:
            raise CorpusConstraintError(f"INCOMPLETE_PARAMETER_BINDING:{name}")
        kind, status, role, cid = (binding[k] for k in ("kind", "status", "role", "constraint_id"))
        if not all(isinstance(v, str) and v for v in (kind, cid)) or status not in STATUS:
            raise CorpusConstraintError(f"UNKNOWN_TYPE_OR_STATUS:{name}")
        if role not in ("NATIVE_EXACT_CANDIDATE", "PROJECTION_ONLY"):
            raise CorpusConstraintError(f"UNKNOWN_AUTHORITY_ROLE:{name}")
        if role == "NATIVE_EXACT_CANDIDATE" and status not in EXECUTION_ELIGIBLE:
            raise CorpusConstraintError(f"NONEXECUTABLE_SOURCE_AS_AUTHORITY:{name}")
        paths = binding["source_paths"]
        if not isinstance(paths, (tuple, list)) or not paths or not all(
            isinstance(p, str) and p in snap["files"] for p in paths
        ):
            raise CorpusConstraintError(f"MISSING_OR_UNVERIFIED_CORPUS_SOURCE:{name}")
        if len(set(paths)) != len(paths):
            raise CorpusConstraintError(f"DUPLICATE_CORPUS_SOURCE:{name}")
        bound[name] = {
            "kind": kind, "status": status, "role": role, "constraint_id": cid,
            "source_files": [{"path": p, "sha256": snap["files"][p]} for p in paths],
            "value": _canonical(binding["value"], name, projection=role == "PROJECTION_ONLY"),
        }
    receipt = {
        "schema": SCHEMA,
        "corpus_roots": snap["roots"], "corpus_bundle_sha256": snap["bundle_sha256"],
        "parameter_count": len(bound), "parameters": bound,
        "all_parameters_source_bound": True,
        "all_parameters_globally_bound_to_both_corpora": True,
        "equation_semantics_proven_by_this_gate": False,
        "signed_vm81_admission_executed": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_hash216_commit_authority": False,
        "status": "CORPUS_BOUND_CANDIDATE_ONLY",
    }
    receipt["receipt_sha256"] = _digest(receipt)
    return receipt
