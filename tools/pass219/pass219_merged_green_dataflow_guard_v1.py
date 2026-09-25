#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Iterable

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST_REPO_PATH = "contracts/pass219/PASS_219_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.json"
DEFAULT_MANIFEST = ROOT / MANIFEST_REPO_PATH

ALLOWED_STATUS = {"A", "M", "D", "R", "C", "T"}


@dataclass(frozen=True)
class Change:
    status: str
    old_path: str | None
    path: str


def run_git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(ref: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", f"{ref}:{path}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    return value or None


def git_text(ref: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if proc.returncode != 0:
        return None
    try:
        return proc.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def git_path_exists(ref: str, path: str) -> bool:
    return git_blob(ref, path) is not None


def merge_base(base: str, head: str) -> str:
    return run_git("merge-base", base, head).strip()


def parse_changes(base: str, head: str) -> list[Change]:
    proc = subprocess.run(
        ["git", "diff", "--name-status", "-z", "--find-renames", f"{base}...{head}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    fields = proc.stdout.decode("utf-8", "surrogateescape").split("\0")
    if fields and fields[-1] == "":
        fields.pop()

    out: list[Change] = []
    i = 0
    while i < len(fields):
        raw_status = fields[i]
        i += 1
        status = raw_status[:1]
        if status not in ALLOWED_STATUS:
            raise RuntimeError(f"unsupported git diff status: {raw_status!r}")
        if status in {"R", "C"}:
            old_path = fields[i]
            new_path = fields[i + 1]
            i += 2
            out.append(Change(status=status, old_path=old_path, path=new_path))
        else:
            path = fields[i]
            i += 1
            out.append(Change(status=status, old_path=None, path=path))
    return out


def _under_root(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip("/") + "/")


def pass_number_from_path(path: str, manifest: dict[str, Any]) -> int | None:
    pattern = re.compile(manifest["pass_token_regex"])
    values = [int(m.group(1)) for m in pattern.finditer(path)]
    if not values:
        root_match = re.match(r"(?i)^HHS_PASS_(\d{1,3})", pathlib.PurePosixPath(path).name)
        if root_match:
            values.append(int(root_match.group(1)))
    return min(values) if values else None


def is_proof_path(path: str, manifest: dict[str, Any]) -> bool:
    return _under_root(path, manifest["proof_directory"]) and path.endswith(".json")


def is_protected_path(
    path: str,
    manifest: dict[str, Any],
    *,
    status: str = "M",
) -> bool:
    normalized = pathlib.PurePosixPath(path).as_posix()

    if normalized in set(manifest["always_protected_paths"]):
        return True

    if is_proof_path(normalized, manifest):
        return status != "A"

    number = pass_number_from_path(normalized, manifest)
    if number is None or number > int(manifest["protected_pass_ceiling"]):
        return False

    return any(_under_root(normalized, root) for root in manifest["protected_roots"])


def source_extension(path: str) -> str:
    return pathlib.PurePosixPath(path).suffix.lower()


def extract_identifiers(text: str | None, path: str) -> set[str]:
    if text is None:
        return set()

    suffix = source_extension(path)
    if suffix == ".py":
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return set()
        names: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
        names.update(re.findall(r"\bHHS_[A-Z0-9_]{3,}\b", text))
        return names

    if suffix in {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp"}:
        tokens = set(re.findall(r"\bhhs_[A-Za-z0-9_]{3,}\b", text))
        tokens.update(re.findall(r"\bHHSExact[A-Za-z0-9_]{3,}\b", text))
        tokens.update(re.findall(r"\bHHS_EXACT_[A-Z0-9_]{3,}\b", text))
        return tokens

    return set()


def count_sensitive_symbols(text: str | None, manifest: dict[str, Any]) -> dict[str, int]:
    haystack = text or ""
    return {symbol: haystack.count(symbol) for symbol in manifest["sensitive_symbols"]}


def authority_sensitive_growth(
    change: Change,
    base: str,
    head: str,
    manifest: dict[str, Any],
) -> dict[str, int]:
    if source_extension(change.path) not in set(manifest["source_extensions"]):
        return {}
    base_path = change.old_path if change.status == "R" and change.old_path else change.path
    before = count_sensitive_symbols(git_text(base, base_path), manifest)
    after = count_sensitive_symbols(git_text(head, change.path), manifest)
    return {
        symbol: after[symbol] - before[symbol]
        for symbol in manifest["sensitive_symbols"]
        if after[symbol] > before[symbol]
    }


def head_contains_identifier(head: str, identifier: str, paths: Iterable[str]) -> bool:
    for path in paths:
        text = git_text(head, path)
        if text is not None and identifier in text:
            return True
    return False


def changed_proof_paths(changes: list[Change], manifest: dict[str, Any]) -> list[str]:
    return [
        c.path
        for c in changes
        if c.status in {"A", "M"} and is_proof_path(c.path, manifest)
    ]


def _require_bool_map(
    doc: dict[str, Any],
    keys: list[str],
    errors: list[str],
    prefix: str,
) -> None:
    values = doc.get(prefix)
    if not isinstance(values, dict):
        errors.append(f"{prefix}:MISSING_MAP")
        return
    for key in keys:
        if values.get(key) is not True:
            errors.append(f"{prefix}:{key}:MUST_BE_TRUE")


def manifest_monotonicity_errors(
    base_manifest: dict[str, Any],
    head_manifest: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    cfg = base_manifest.get("self_integrity", {})

    if int(head_manifest.get("protected_pass_ceiling", -1)) < int(
        base_manifest.get("protected_pass_ceiling", -1)
    ):
        errors.append("POLICY_PROTECTED_PASS_CEILING_DECREASED")

    for field in cfg.get("manifest_set_fields_must_be_monotonic", []):
        before = set(base_manifest.get(field, []))
        after = set(head_manifest.get(field, []))
        missing = sorted(before - after)
        if missing:
            errors.append(
                f"POLICY_MONOTONIC_SET_SHRANK:{field}:" + ",".join(missing)
            )

    for field in cfg.get("manifest_true_maps_must_not_weaken", []):
        before = base_manifest.get(field, {})
        after = head_manifest.get(field, {})
        if not isinstance(before, dict) or not isinstance(after, dict):
            errors.append(f"POLICY_TRUE_MAP_INVALID:{field}")
            continue
        for key, value in before.items():
            if value is True and after.get(key) is not True:
                errors.append(f"POLICY_TRUE_FLAG_WEAKENED:{field}:{key}")

    if cfg.get("proof_directory_may_not_change", False):
        if head_manifest.get("proof_directory") != base_manifest.get("proof_directory"):
            errors.append("POLICY_PROOF_DIRECTORY_CHANGED")

    if cfg.get("proof_schema_may_not_change", False):
        if head_manifest.get("proof_schema") != base_manifest.get("proof_schema"):
            errors.append("POLICY_PROOF_SCHEMA_CHANGED")

    if cfg.get("required_check_name_may_not_change", False):
        before = base_manifest.get("github_merge_layer", {}).get("required_check_name")
        after = head_manifest.get("github_merge_layer", {}).get("required_check_name")
        if before != after:
            errors.append("POLICY_REQUIRED_CHECK_NAME_CHANGED")

    return errors


def validate_policy_self_integrity(
    base: str,
    head: str,
    manifest: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    cfg = manifest.get("self_integrity", {})
    policy_paths = list(cfg.get("policy_paths", []))

    for path in policy_paths:
        if not git_path_exists(head, path):
            errors.append(f"POLICY_SELF_PATH_MISSING:{path}")

    head_manifest_text = git_text(head, MANIFEST_REPO_PATH)
    if head_manifest_text is None:
        errors.append("POLICY_HEAD_MANIFEST_MISSING")
        return errors
    try:
        head_manifest = json.loads(head_manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"POLICY_HEAD_MANIFEST_INVALID_JSON:{exc}")
        return errors

    base_manifest_text = git_text(base, MANIFEST_REPO_PATH)
    if base_manifest_text is not None:
        try:
            base_manifest = json.loads(base_manifest_text)
        except json.JSONDecodeError as exc:
            errors.append(f"POLICY_BASE_MANIFEST_INVALID_JSON:{exc}")
            return errors
        errors.extend(manifest_monotonicity_errors(base_manifest, head_manifest))

    anchor_targets = (
        (
            "tools/pass219/pass219_merged_green_dataflow_guard_v1.py",
            cfg.get("guard_script_required_anchors", []),
            "GUARD",
        ),
        (
            ".github/workflows/pass219-merged-green-dataflow-nonregression-v1.yml",
            cfg.get("workflow_required_anchors", []),
            "WORKFLOW",
        ),
        (
            "contracts/pass219/PASS_219_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.md",
            cfg.get("contract_required_anchors", []),
            "CONTRACT",
        ),
        (
            ".github/rulesets/HHS_MAIN_MERGED_GREEN_DATAFLOW_RULESET_V1.json",
            cfg.get("ruleset_required_anchors", []),
            "RULESET",
        ),
        (
            "contracts/pass219/PASS_219_MAIN_BRANCH_MERGE_RULES_V1.md",
            cfg.get("merge_rules_required_anchors", []),
            "MERGE_RULES",
        ),
    )
    for path, anchors, label in anchor_targets:
        text = git_text(head, path)
        if text is None:
            errors.append(f"POLICY_{label}_MISSING:{path}")
            continue
        for anchor in anchors:
            if anchor not in text:
                errors.append(f"POLICY_{label}_ANCHOR_MISSING:{anchor}")

    return errors


def validate_proof_document(
    proof_path: str,
    proof: dict[str, Any],
    *,
    actual_merge_base: str,
    base: str,
    head: str,
    manifest: dict[str, Any],
    impacted: dict[str, Change],
) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    covered: set[str] = set()

    if proof.get("schema") != manifest["proof_schema"]:
        errors.append(f"{proof_path}:SCHEMA_MISMATCH")
    if proof.get("mode") not in set(manifest["allowed_modes"]):
        errors.append(f"{proof_path}:MODE_INVALID")
    if proof.get("merge_base") != actual_merge_base:
        errors.append(f"{proof_path}:MERGE_BASE_MISMATCH")

    _require_bool_map(
        proof,
        list(manifest["mandatory_invariants"]),
        errors,
        "invariants",
    )

    profiles = proof.get("validation_profiles")
    required_profiles = set(manifest["mandatory_validation_profiles"])
    if not isinstance(profiles, list):
        errors.append(f"{proof_path}:VALIDATION_PROFILES_MISSING")
    elif not required_profiles.issubset(set(profiles)):
        missing = sorted(required_profiles - set(profiles))
        errors.append(f"{proof_path}:VALIDATION_PROFILES_MISSING:{','.join(missing)}")

    for field in ("defect_or_iteration", "receipt_continuity", "rollback_plan"):
        value = proof.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{proof_path}:{field}:MISSING")

    for field in ("regression_tests", "negative_tests"):
        values = proof.get(field)
        if not isinstance(values, list) or not values:
            errors.append(f"{proof_path}:{field}:MISSING")
        else:
            for test_path in values:
                if not isinstance(test_path, str) or not test_path.startswith("tests/"):
                    errors.append(f"{proof_path}:{field}:INVALID_PATH:{test_path!r}")
                elif not git_path_exists(head, test_path):
                    errors.append(f"{proof_path}:{field}:NOT_IN_HEAD:{test_path}")

    rows = proof.get("protected_changes")
    if not isinstance(rows, list) or not rows:
        errors.append(f"{proof_path}:protected_changes:MISSING")
        return errors, covered

    mode = proof.get("mode")
    self_cfg = manifest.get("self_integrity", {})
    self_paths = set(self_cfg.get("policy_paths", []))
    seen_paths: set[str] = set()

    for row in rows:
        if not isinstance(row, dict):
            errors.append(f"{proof_path}:protected_changes:ROW_NOT_OBJECT")
            continue
        path = row.get("path")
        if not isinstance(path, str) or path not in impacted:
            errors.append(f"{proof_path}:UNKNOWN_PROTECTED_CHANGE:{path!r}")
            continue
        if path in seen_paths:
            errors.append(f"{proof_path}:DUPLICATE_CHANGE:{path}")
            continue
        seen_paths.add(path)
        covered.add(path)
        change = impacted[path]

        base_path = change.old_path if change.status == "R" and change.old_path else path
        expected_before = git_blob(base, base_path)
        expected_after = git_blob(head, path)

        if row.get("change_status") != change.status:
            errors.append(f"{proof_path}:{path}:STATUS_MISMATCH")
        if row.get("predecessor_blob") != expected_before:
            errors.append(f"{proof_path}:{path}:PREDECESSOR_BLOB_MISMATCH")

        claimed_after = row.get("successor_blob")
        if expected_after is None:
            if claimed_after != "DELETED":
                errors.append(f"{proof_path}:{path}:SUCCESSOR_DELETION_MISMATCH")
        elif claimed_after != expected_after:
            errors.append(f"{proof_path}:{path}:SUCCESSOR_BLOB_MISMATCH")

        if change.status in {"D", "R"} and mode != "REPAIR_FORWARD_REFINEMENT":
            errors.append(f"{proof_path}:{path}:DELETION_OR_RENAME_REQUIRES_REPAIR_FORWARD")

        if (
            self_cfg.get("existing_policy_change_requires_repair_forward", False)
            and path in self_paths
            and git_blob(base, base_path) is not None
            and mode != "REPAIR_FORWARD_REFINEMENT"
        ):
            errors.append(f"{proof_path}:{path}:POLICY_CHANGE_REQUIRES_REPAIR_FORWARD")

        base_text = git_text(base, base_path)
        head_text = git_text(head, path)
        removed = sorted(
            extract_identifiers(base_text, base_path)
            - extract_identifiers(head_text, path)
        )

        superseded_rows = row.get("superseded_identifiers", [])
        if not isinstance(superseded_rows, list):
            superseded_rows = []
            errors.append(f"{proof_path}:{path}:SUPERSEDED_IDENTIFIERS_INVALID")

        mappings: dict[str, dict[str, Any]] = {}
        for item in superseded_rows:
            if isinstance(item, dict) and isinstance(item.get("identifier"), str):
                mappings[item["identifier"]] = item

        if removed and mode == "BACKWARD_COMPATIBLE_ITERATION":
            errors.append(
                f"{proof_path}:{path}:BACKWARD_COMPAT_REMOVED_IDENTIFIERS:{','.join(removed)}"
            )

        if removed and mode == "REPAIR_FORWARD_REFINEMENT":
            replacement_paths = [
                p
                for p in row.get("replacement_paths", [])
                if isinstance(p, str) and git_path_exists(head, p)
            ]
            search_paths = ([path] if git_path_exists(head, path) else []) + replacement_paths
            if change.status == "D" and not replacement_paths:
                errors.append(f"{proof_path}:{path}:DELETION_REPLACEMENT_PATH_MISSING")
            for identifier in removed:
                item = mappings.get(identifier)
                if item is None:
                    errors.append(
                        f"{proof_path}:{path}:UNMAPPED_REMOVED_IDENTIFIER:{identifier}"
                    )
                    continue
                replacement = item.get("replacement_identifier")
                adapter = item.get("compatibility_adapter")
                if not isinstance(replacement, str) or not replacement:
                    errors.append(f"{proof_path}:{path}:{identifier}:REPLACEMENT_MISSING")
                elif not head_contains_identifier(head, replacement, search_paths):
                    errors.append(
                        f"{proof_path}:{path}:{identifier}:REPLACEMENT_NOT_FOUND:{replacement}"
                    )
                if not isinstance(adapter, str) or not adapter:
                    errors.append(f"{proof_path}:{path}:{identifier}:ADAPTER_MISSING")
                elif not head_contains_identifier(head, adapter, search_paths):
                    errors.append(
                        f"{proof_path}:{path}:{identifier}:ADAPTER_NOT_FOUND:{adapter}"
                    )

        predecessor_identifiers = extract_identifiers(base_text, base_path)
        preserved = row.get("preserved_identifiers", [])
        if not isinstance(preserved, list):
            errors.append(f"{proof_path}:{path}:PRESERVED_IDENTIFIERS_INVALID")
            preserved = []

        replacement_paths = [
            p
            for p in row.get("replacement_paths", [])
            if isinstance(p, str) and git_path_exists(head, p)
        ]

        # Retained predecessor identifiers are recomputed directly from the Git
        # blobs. The proof may enumerate important preserved identifiers, but it
        # cannot hide removals: backward-compatible mode rejects every removal,
        # and repair-forward mode requires a mapping for every removal.
        for identifier in preserved:
            if not isinstance(identifier, str) or not identifier:
                errors.append(f"{proof_path}:{path}:PRESERVED_IDENTIFIER_INVALID")
                continue
            if identifier not in predecessor_identifiers:
                errors.append(
                    f"{proof_path}:{path}:PRESERVED_IDENTIFIER_NOT_IN_PREDECESSOR:{identifier}"
                )
                continue
            if identifier not in (head_text or "") and not head_contains_identifier(
                head, identifier, replacement_paths
            ):
                errors.append(
                    f"{proof_path}:{path}:PRESERVED_IDENTIFIER_NOT_FOUND:{identifier}"
                )

    return errors, covered


def build_impacted(
    changes: list[Change],
    base: str,
    head: str,
    manifest: dict[str, Any],
) -> tuple[dict[str, Change], dict[str, dict[str, int]]]:
    impacted: dict[str, Change] = {}
    growth: dict[str, dict[str, int]] = {}

    for change in changes:
        old_protected = bool(
            change.old_path
            and is_protected_path(change.old_path, manifest, status="M")
        )
        new_protected = is_protected_path(
            change.path, manifest, status=change.status
        )

        symbol_growth = authority_sensitive_growth(change, base, head, manifest)
        if symbol_growth:
            growth[change.path] = symbol_growth

        if old_protected or new_protected or symbol_growth:
            if is_proof_path(change.path, manifest) and change.status == "A":
                continue
            impacted[change.path] = change

    return impacted, growth


def validate(
    base: str,
    head: str,
    manifest_path: pathlib.Path,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    actual_merge_base = merge_base(base, head)
    changes = parse_changes(base, head)
    impacted, sensitive_growth = build_impacted(changes, base, head, manifest)
    self_integrity_errors = validate_policy_self_integrity(base, head, manifest)

    result: dict[str, Any] = {
        "schema": "HHS_PASS219_MERGED_GREEN_DATAFLOW_GUARD_RESULT_V1",
        "base": base,
        "head": head,
        "merge_base": actual_merge_base,
        "changed_count": len(changes),
        "protected_change_count": len(impacted),
        "protected_changes": [
            {
                "status": c.status,
                "old_path": c.old_path,
                "path": c.path,
                "sensitive_symbol_growth": sensitive_growth.get(c.path, {}),
            }
            for c in impacted.values()
        ],
        "proof_required": bool(impacted),
        "proof_paths": [],
        "errors": list(self_integrity_errors),
        "status": "FAIL" if self_integrity_errors else "PASS",
    }

    if not impacted:
        return result

    proof_paths = changed_proof_paths(changes, manifest)
    result["proof_paths"] = proof_paths
    if not proof_paths:
        result["errors"].append("PROTECTED_CHANGE_WITHOUT_SUCCESSOR_PROOF")
        result["status"] = "FAIL"
        return result

    covered: set[str] = set()
    for proof_path in proof_paths:
        proof_text = git_text(head, proof_path)
        if proof_text is None:
            result["errors"].append(f"{proof_path}:UNREADABLE")
            continue
        try:
            proof = json.loads(proof_text)
        except json.JSONDecodeError as exc:
            result["errors"].append(f"{proof_path}:INVALID_JSON:{exc}")
            continue
        errors, proof_covered = validate_proof_document(
            proof_path,
            proof,
            actual_merge_base=actual_merge_base,
            base=base,
            head=head,
            manifest=manifest,
            impacted=impacted,
        )
        result["errors"].extend(errors)
        covered.update(proof_covered)

    missing = sorted(set(impacted) - covered)
    if missing:
        result["errors"].append("UNPROVEN_PROTECTED_CHANGES:" + ",".join(missing))

    if result["errors"]:
        result["status"] = "FAIL"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output")
    args = parser.parse_args()

    result = validate(
        args.base,
        args.head,
        pathlib.Path(args.manifest),
    )

    encoded = json.dumps(result, indent=2, sort_keys=True)
    print(encoded)
    if args.output:
        pathlib.Path(args.output).write_text(encoded + "\n", encoding="utf-8")

    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
