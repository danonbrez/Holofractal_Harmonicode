#!/usr/bin/env python3
"""Fail-closed validator for the 23-file HHS runtime JSON specification package."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - deployment dependency gate
    raise SystemExit("python jsonschema package is required") from exc

REQUIRED_DOMAIN_TOKENS = {
    "canonical_constants_and_minimum_registry_unit": ("canonical", "minimum", "registry", "unit"),
    "vm81_vm5184_logical_and_control_addressing": ("vm81", "vm5184", "address"),
    "hash216_snapshot_identity": ("hash216", "snapshot", "identity"),
    "fixed_width_noncommutative_nested_constraint_bytecode": (
        "fixed", "width", "noncommutative", "bytecode"
    ),
    "novel_transition_and_inverse_delta_records": ("novel", "transition", "inverse", "delta"),
    "cpu_directed_gpu_dispatch_manifests": ("cpu", "gpu", "dispatch", "manifest"),
    "global_serialization_vector_cache_entries": ("serialization", "vector", "cache"),
    "emergent_object_closure": ("emergent", "object", "closure"),
    "validation_and_commit_receipts": ("validation", "commit", "receipt"),
    "deep_learning_candidate_transitions": ("deep", "learning", "candidate", "transition"),
    "phase_error_syndromes_5184": ("5184", "phase", "error", "syndrome"),
    "runtime_state_machine_rules": ("runtime", "state", "machine", "rule"),
    "default_implementation_profile": ("default", "implementation", "profile"),
    "examples_checksums_and_conformance_vectors": ("example", "checksum", "conformance", "vector"),
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", json.dumps(value, sort_keys=True).lower())


def candidate_manifests(documents: dict[Path, Any]) -> list[Path]:
    candidates: list[Path] = []
    for path, value in documents.items():
        name = path.name.lower()
        schema = str(value.get("schema", "")).lower() if isinstance(value, dict) else ""
        if "manifest" in name or "package_manifest" in schema or "specification_package" in schema:
            candidates.append(path)
    return sorted(candidates)


def entry_path(entry: Any) -> str | None:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        for key in ("path", "file", "filename", "name"):
            if key in entry:
                return str(entry[key])
    return None


def entry_checksum(entry: Any) -> str | None:
    if not isinstance(entry, dict):
        return None
    for key in ("sha256", "checksum_sha256", "checksum", "digest"):
        value = entry.get(key)
        if isinstance(value, str):
            return value.removeprefix("sha256:").lower()
    return None


def manifest_entries(manifest: dict[str, Any]) -> list[Any]:
    for key in ("files", "artifacts", "package_files", "documents"):
        value = manifest.get(key)
        if isinstance(value, list):
            return value
    return []


def checksum_map(manifest: dict[str, Any]) -> dict[str, str]:
    for key in ("checksums", "sha256", "file_checksums"):
        value = manifest.get(key)
        if isinstance(value, dict):
            return {
                str(path): str(checksum).removeprefix("sha256:").lower()
                for path, checksum in value.items()
            }
    return {}


def local_schema_path(root: Path, document_path: Path, reference: str) -> Path | None:
    if reference.startswith(("http://", "https://")):
        return None
    reference = reference.removeprefix("file://")
    candidates = [
        (document_path.parent / reference).resolve(),
        (root / reference).resolve(),
    ]
    for candidate in candidates:
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    return None


def declared_schema_reference(value: dict[str, Any]) -> str | None:
    for key in ("$schema_ref", "schema_ref", "schema_path", "instance_schema"):
        reference = value.get(key)
        if isinstance(reference, str):
            return reference
    schema_value = value.get("$schema")
    if isinstance(schema_value, str) and not schema_value.startswith("https://json-schema.org/"):
        return schema_value
    return None


def validate_instances(root: Path, documents: dict[Path, Any]) -> tuple[int, list[str]]:
    validated = 0
    failures: list[str] = []
    for path, value in documents.items():
        if not isinstance(value, dict):
            continue
        reference = declared_schema_reference(value)
        if reference is None:
            continue
        schema_path = local_schema_path(root, path, reference)
        if schema_path is None:
            failures.append(f"local schema reference unavailable for {path.relative_to(root)}: {reference}")
            continue
        schema = documents.get(schema_path)
        if schema is None:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(schema).validate(value)
        except jsonschema.ValidationError as exc:
            failures.append(f"schema validation failed for {path.relative_to(root)}: {exc.message}")
            continue
        validated += 1
    return validated, failures


def declared_examples(manifest: dict[str, Any], documents: dict[Path, Any]) -> set[str]:
    examples: set[str] = set()
    value = manifest.get("examples")
    if isinstance(value, list):
        for entry in value:
            path = entry_path(entry)
            if path:
                examples.add(path)
    for path, document in documents.items():
        if "example" in path.name.lower():
            examples.add(path.as_posix())
        if isinstance(document, dict) and str(document.get("role", "")).lower() == "example":
            examples.add(path.as_posix())
    return examples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=os.environ.get("HHS_JSON_SPEC_PACKAGE_ROOT"))
    parser.add_argument("--manifest", default=os.environ.get("HHS_JSON_SPEC_MANIFEST"))
    parser.add_argument(
        "--expected-files",
        type=int,
        default=int(os.environ.get("HHS_JSON_SPEC_EXPECTED_FILES", "23")),
    )
    parser.add_argument(
        "--expected-examples",
        type=int,
        default=int(os.environ.get("HHS_JSON_SPEC_EXPECTED_EXAMPLES", "4")),
    )
    parser.add_argument("--receipt", default=None)
    args = parser.parse_args()

    if not args.root:
        raise SystemExit("HHS_JSON_SPEC_PACKAGE_ROOT or --root is required")
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"JSON specification package root does not exist: {root}")

    files = sorted(path for path in root.rglob("*.json") if path.is_file())
    if len(files) != args.expected_files:
        raise SystemExit(
            f"JSON specification package contains {len(files)} JSON files; expected {args.expected_files}"
        )

    documents: dict[Path, Any] = {}
    for path in files:
        try:
            documents[path.resolve()] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SystemExit(f"invalid JSON document {path}: {exc}") from exc

    if args.manifest:
        manifest_path = Path(args.manifest)
        if not manifest_path.is_absolute():
            manifest_path = root / manifest_path
        manifest_path = manifest_path.resolve()
    else:
        candidates = candidate_manifests(documents)
        if len(candidates) != 1:
            names = [str(path.relative_to(root)) for path in candidates]
            raise SystemExit(f"exactly one package manifest is required; found {names}")
        manifest_path = candidates[0]
    manifest = documents.get(manifest_path)
    if not isinstance(manifest, dict):
        raise SystemExit(f"package manifest is unavailable or not an object: {manifest_path}")

    failures: list[str] = []
    entries = manifest_entries(manifest)
    checksums = checksum_map(manifest)
    referenced: set[str] = set()
    for entry in entries:
        relative = entry_path(entry)
        if not relative:
            failures.append("manifest contains a file entry without a path")
            continue
        referenced.add(relative)
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            failures.append(f"manifest path escapes package root: {relative}")
            continue
        if not path.is_file():
            failures.append(f"manifest file is missing: {relative}")
            continue
        expected = entry_checksum(entry) or checksums.get(relative)
        if expected and sha256_file(path) != expected:
            failures.append(f"checksum mismatch: {relative}")
    for relative, expected in checksums.items():
        path = (root / relative).resolve()
        if not path.is_file():
            failures.append(f"checksum file is missing: {relative}")
        elif sha256_file(path) != expected:
            failures.append(f"checksum mismatch: {relative}")

    if not entries and not checksums:
        failures.append("package manifest must declare files or checksums")
    if referenced and len(referenced) != args.expected_files:
        failures.append(
            f"manifest declares {len(referenced)} unique files; expected {args.expected_files}"
        )

    validated_instances, schema_failures = validate_instances(root, documents)
    failures.extend(schema_failures)
    if validated_instances < args.expected_examples:
        failures.append(
            f"only {validated_instances} schema-linked instances validated; expected at least {args.expected_examples}"
        )

    examples = declared_examples(manifest, documents)
    if len(examples) < args.expected_examples:
        failures.append(f"only {len(examples)} examples declared; expected at least {args.expected_examples}")

    corpus = " ".join(
        f"{path.relative_to(root).as_posix().lower()} {normalized_text(value)}"
        for path, value in documents.items()
    )
    domain_results: dict[str, bool] = {}
    for domain, tokens in REQUIRED_DOMAIN_TOKENS.items():
        domain_results[domain] = all(token in corpus for token in tokens)
        if not domain_results[domain]:
            failures.append(f"required specification domain not evidenced: {domain}")

    conformance_files = [
        path for path in files
        if "conformance" in path.name.lower() or "vector" in path.name.lower()
    ]
    if not conformance_files:
        failures.append("no conformance-vector JSON document found")

    receipt = {
        "schema": "HHS_PASS_208_JSON_SPEC_PACKAGE_VALIDATION_RECEIPT_V1",
        "ok": not failures,
        "package_root": str(root),
        "manifest": str(manifest_path.relative_to(root)),
        "json_file_count": len(files),
        "expected_json_file_count": args.expected_files,
        "declared_file_count": len(referenced),
        "schema_linked_instances_validated": validated_instances,
        "declared_example_count": len(examples),
        "expected_example_count": args.expected_examples,
        "conformance_vector_files": [str(path.relative_to(root)) for path in conformance_files],
        "domain_results": domain_results,
        "package_root_sha256": hashlib.sha256(
            b"".join(
                path.relative_to(root).as_posix().encode("utf-8")
                + b"\0"
                + sha256_file(path).encode("ascii")
                for path in files
            )
        ).hexdigest(),
        "failures": failures,
    }
    output = json.dumps(receipt, indent=2, sort_keys=True)
    print(output)
    if args.receipt:
        receipt_path = Path(args.receipt)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(output + "\n", encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
