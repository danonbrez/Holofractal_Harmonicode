#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hhs_runtime.pass219.multimodal_optimization_generalization import (  # noqa: E402
    OptimizationGeneralizationError,
    validate_manifest,
)

MANIFEST_DIR = ROOT / "contracts/pass219/optimization_generalization"
CODE_PREFIXES = ("hhs_runtime/", "hhs_backend/", "native_projects/", "applications/")
CODE_SUFFIXES = (".py", ".c", ".cc", ".cpp", ".h", ".hpp", ".mjs", ".js", ".ts", ".tsx", ".rs", ".cu")
POLICY_EXCLUSIONS = {
    "hhs_runtime/include/hhs_runtime_exact_abi.h",
    "hhs_runtime/c/hhs_runtime_exact_abi.c",
}
POLICY_PREFIXES = (
    "hhs_runtime/include/hhs_pass219_multimodal_optimization_generalization_",
    "hhs_runtime/c/hhs_pass219_multimodal_optimization_generalization_",
    "hhs_runtime/pass219/multimodal_optimization_generalization.py",
)
SIGNAL = re.compile(
    r"\b(optimi[sz](?:e|ed|ation|ations|ing)|latency|compression|compress(?:ed|ion|or)?|"
    r"cach(?:e|ed|ing)|branch prediction|memory efficiency|throughput|fast[-_ ]?path|"
    r"sparse[-_ ]?(?:update|projection|path)|vector[-_ ]?cache)\b",
    re.IGNORECASE,
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_all() -> list[dict]:
    rows = []
    for path in sorted(MANIFEST_DIR.glob("*.json")):
        result = validate_manifest(_json(path))
        rows.append({"path": str(path.relative_to(ROOT)), **result})
    if not rows:
        raise OptimizationGeneralizationError("NO_OPTIMIZATION_GENERALIZATION_MANIFESTS")
    return rows


def _changed_paths(base: str) -> list[str]:
    out = subprocess.check_output(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=ROOT,
        text=True,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def _added_lines(base: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "diff", "--unified=0", f"{base}...HEAD", "--", path],
        cwd=ROOT,
        text=True,
        errors="replace",
    )


def _is_candidate(path: str) -> bool:
    if path in POLICY_EXCLUSIONS or path.startswith(POLICY_PREFIXES):
        return False
    return path.startswith(CODE_PREFIXES) and path.endswith(CODE_SUFFIXES)


def audit_diff(base: str) -> dict:
    changed = _changed_paths(base)
    detected: list[str] = []
    for path in changed:
        if not _is_candidate(path):
            continue
        diff = _added_lines(base, path)
        added = "\n".join(
            line[1:] for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        if SIGNAL.search(added):
            detected.append(path)

    manifest_paths = [
        path for path in changed
        if path.startswith("contracts/pass219/optimization_generalization/")
        and path.endswith(".json")
    ]
    covered: set[str] = set()
    validated = []
    for rel in manifest_paths:
        manifest = _json(ROOT / rel)
        result = validate_manifest(manifest)
        covered.update(str(v) for v in manifest.get("changed_paths", []))
        validated.append({"path": rel, **result})

    missing = sorted(set(detected) - covered)
    if missing:
        raise OptimizationGeneralizationError(
            "UNDECLARED_OPTIMIZATION_CHANGE:" + ",".join(missing)
        )
    return {
        "detected_optimization_paths": sorted(detected),
        "covered_paths": sorted(covered),
        "validated_manifests": validated,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-all")
    audit = sub.add_parser("audit-diff")
    audit.add_argument("base")
    args = parser.parse_args()

    if args.command == "validate-all":
        result = {"manifests": validate_all()}
    else:
        result = audit_diff(args.base)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
