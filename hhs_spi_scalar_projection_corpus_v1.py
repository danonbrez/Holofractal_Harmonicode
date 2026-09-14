"""
Pass 219 — SPI Repository Scalar-Projection Corpus Coverage v1.

This module inventories the repository's executable ``*.harmonicode`` source
corpus and classifies scalar-capable source-span candidates against the
repository-audited SPI scalar projection registry.

Authority boundary
------------------
The corpus scanner is downstream of preserved HARMONICODE source and the
non-executing Pass 075 parser. It does not rewrite source, solve native symbols,
commute ordered products, admit VM81 state, or mint canonical Hash72/Hash216
lineage.

The current parser is statement-oriented rather than a complete nested
expression AST. Accordingly this v1 pass reports:
  * parser-bound exact source identity;
  * deterministic lexical scalar-candidate spans;
  * registered proof bindings where exact profiles exist;
  * explicit SYMBOLIC / UNSUPPORTED_DOMAIN / MISSING_PROJECTION states.

No unregistered expression is inferred into PROVEN.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Dict, Iterable, Mapping, Sequence

from hhs_spi_scalar_projection_registry_v1 import (
    AUDITED_MAIN_SHA,
    MISSING_PROJECTION,
    PROVEN,
    SYMBOLIC,
    UNSUPPORTED_DOMAIN,
    build_registry,
)

FORMAT = "HHS_SPI_SCALAR_PROJECTION_CORPUS_V1"
VERSION = "1.0.0"
MANIFEST_SCHEMA = "HHS_SPI_REPOSITORY_CORPUS_COVERAGE_MANIFEST_V1"
CANDIDATE_SCHEMA = "HHS_SPI_SCALAR_CANDIDATE_COVERAGE_V1"

CANONICAL_SOURCE_PATH = "HHS_PASS_169_CANONICAL_ALGEBRA_CORPUS.harmonicode"
CANONICAL_ALIAS_PATH = "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode"

EXPECTED_HARMONICODE_SOURCES: Dict[str, Dict[str, Any]] = {
    "HHS_PASS_168_SOURCE_FIXTURE.harmonicode": {
        "tier": "FIXTURE",
        "sha256": "fdbee5db0f2fea428b6b88e5ac9b273e6aa3754fa00f84e8923456373275166e",
        "bytes": 424,
    },
    CANONICAL_SOURCE_PATH: {
        "tier": "CANONICAL_SOURCE_OF_RECORD",
        "sha256": "3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53",
        "bytes": 632,
    },
    CANONICAL_ALIAS_PATH: {
        "tier": "CANONICAL_BYTE_ALIAS",
        "sha256": "3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53",
        "bytes": 632,
    },
    "contracts/pass219/PASS_219_DENOMINATOR_MAGNITUDE_PROJECTION_1_21_8.harmonicode": {
        "tier": "CONTRACT_PROJECTION_SOURCE",
        "sha256": "c28efa30c3aa8aa6b6041d2cd199853bc50f470de46b8db753b91f4412cb6d25",
        "bytes": 55,
    },
    "contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode": {
        "tier": "CONTRACT_NATIVE_SOURCE",
        "sha256": "ac143798146d89a3fe932f39ccb4d612e4fb3e45c471abc1a8bbbebb0f9c0a6a",
        "bytes": 348,
    },
    "contracts/pass219/PASS_219_NATIVE_UNIVERSAL_CONSTRAINT_ENVELOPE_1_8_0.harmonicode": {
        "tier": "CONTRACT_NATIVE_SOURCE",
        "sha256": "7eb0cc5707a4a58a5a8e4879e0e2e3bdab22c15fe4503fb3a3b0e16596343d42",
        "bytes": 354,
    },
}

_ALIAS_BINDINGS: Sequence[Dict[str, Any]] = (
    {"variants": ("a²", "a^2"), "proof_id": "SPI-PROJ-0001", "role": "EXACT_SCALAR_SOURCE"},
    {"variants": ("b²", "b^2"), "proof_id": "SPI-PROJ-0002", "role": "EXACT_SCALAR_SOURCE"},
    {"variants": ("c²", "c^2"), "proof_id": "SPI-PROJ-0003", "role": "EXACT_SCALAR_SOURCE"},
    {"variants": ("b⁴", "b^4"), "proof_id": "SPI-PROJ-0004", "role": "EXACT_SCALAR_SOURCE"},
    {"variants": ("c⁴", "c^4"), "proof_id": "SPI-PROJ-0005", "role": "EXACT_SCALAR_SOURCE"},
    {"variants": ("b⁶", "b^6"), "proof_id": "SPI-PROJ-0006", "role": "EXACT_SCALAR_SOURCE"},
    {"variants": ("b²c²", "b^2c^2"), "proof_id": "SPI-PROJ-0007", "role": "EXACT_SCALAR_SOURCE"},
    {"variants": ("b²c²-a²", "b^2c^2-a^2"), "proof_id": "SPI-PROJ-0008", "role": "EXACT_SCALAR_SOURCE"},
    {"variants": ("b⁴+c²", "b^4+c^2"), "proof_id": "SPI-PROJ-0009", "role": "EXACT_SCALAR_SOURCE"},
    {"variants": ("b⁶c⁴", "b^6c^4"), "proof_id": "SPI-PROJ-0010", "role": "EXACT_SCALAR_SOURCE"},
    {
        "variants": ("(b^(2c²)c^(b⁴))²", "(b^(2c^2)c^b^4)^2"),
        "proof_id": "SPI-PROJ-0011",
        "role": "PROFILE_EQUIVALENT_SOURCE",
    },
    {"variants": ("P²-pq", "P^2-pq"), "proof_id": "SPI-T1", "role": "SPI_DEFECT_FRAGMENT"},
    {"variants": ("t³-t", "t^3-t"), "proof_id": "SPI-T3A", "role": "POLYNOMIAL_FRAGMENT"},
    {"variants": ("m²-m", "m^2-m"), "proof_id": "SPI-T3A", "role": "POLYNOMIAL_FRAGMENT"},
    {"variants": ("P²(MOD)(pq)", "P^2(MOD)(pq)"), "proof_id": "SPI-T3C", "role": "EXACT_NATIVE_EDGE"},
    {"variants": ("u⁷²", "u^72"), "proof_id": "SPI-T6", "role": "T6_PHASE_UNIT_FRAGMENT"},
)

_SUPERSCRIPT_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_SUPERSCRIPT_TO_ASCII = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

ASCII_POWER_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(?:[A-Za-z_ΔΠπρφψχδτ][A-Za-z0-9_ΔΠπρφψχδτ]*|\([^()\n]{1,96}\))"
    r"\^(?:\([^()\n]{1,96}\)|-?\d+|[A-Za-z_ΔΠπρφψχδτ][A-Za-z0-9_ΔΠπρφψχδτ]*)"
)
SUPERSCRIPT_POWER_RE = re.compile(
    rf"(?<![A-Za-z0-9_])[A-Za-z_ΔΠπρφψχδτ][A-Za-z0-9_ΔΠπρφψχδτ]*[{_SUPERSCRIPT_DIGITS}]+"
)
INTEGER_RE = re.compile(r"(?<![A-Za-z0-9_])[-+]?\d+(?![A-Za-z0-9_])")
SUPERSCRIPT_INTEGER_RE = re.compile(rf"[{_SUPERSCRIPT_DIGITS}]+")
CALL_NAME_RE = re.compile(r"\b(NcalcMatrixPower|MatrixTimes|Mod|Sqrt|RealSurd)\s*([\(\[])")

SYMBOLIC_CALL_FAMILIES = {
    "NcalcMatrixPower": {
        "coverage_state": SYMBOLIC,
        "projection_id": "SPI-O2-MATRIX",
        "reason": "exact ordered matrix-power scalar witness remains open",
    },
    "MatrixTimes": {
        "coverage_state": SYMBOLIC,
        "projection_id": "SPI-MATRIX-OP-FAMILY",
        "reason": "matrix operation retained symbolically; no scalar collapse authorized",
    },
    "Mod": {
        "coverage_state": SYMBOLIC,
        "projection_id": "SPI-MOD-OP-FAMILY",
        "reason": "generic Mod call is not identified with the typed P²(MOD)(pq) edge",
    },
    "Sqrt": {
        "coverage_state": SYMBOLIC,
        "projection_id": "SPI-SQRT-OP-FAMILY",
        "reason": "root remains symbolic unless a registered exact radical profile closes",
    },
    "RealSurd": {
        "coverage_state": SYMBOLIC,
        "projection_id": "SPI-QROOT-0001",
        "reason": "registered root rule exists but a call requires domain/exponent context for exact collapse",
    },
}


class SPICorpusError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _line_column(source: str, offset: int) -> Dict[str, int]:
    line = source.count("\n", 0, offset) + 1
    previous = source.rfind("\n", 0, offset)
    column = offset + 1 if previous < 0 else offset - previous
    return {"line": line, "column": column}


def _span(source: str, start: int, end: int) -> Dict[str, Any]:
    return {
        "start": start,
        "end": end,
        "start_position": _line_column(source, start),
        "end_position": _line_column(source, end),
        "text_sha256": sha256(source[start:end].encode("utf-8")).hexdigest(),
    }


def discover_harmonicode_sources(repo_root: Path) -> Sequence[str]:
    repo_root = Path(repo_root)
    paths = []
    for path in repo_root.rglob("*.harmonicode"):
        if ".git" in path.parts:
            continue
        paths.append(path.relative_to(repo_root).as_posix())
    return tuple(sorted(paths))


def validate_source_inventory(repo_root: Path) -> Dict[str, Any]:
    repo_root = Path(repo_root)
    discovered = set(discover_harmonicode_sources(repo_root))
    expected = set(EXPECTED_HARMONICODE_SOURCES)
    errors = []
    if discovered != expected:
        missing = sorted(expected - discovered)
        unexpected = sorted(discovered - expected)
        if missing:
            errors.append(f"missing registered .harmonicode sources: {missing}")
        if unexpected:
            errors.append(f"unregistered .harmonicode sources: {unexpected}")

    records = []
    for relpath in sorted(expected):
        path = repo_root / relpath
        if not path.is_file():
            continue
        raw = path.read_bytes()
        try:
            source = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{relpath}: not valid UTF-8: {exc}")
            continue
        actual_sha = sha256(raw).hexdigest()
        spec = EXPECTED_HARMONICODE_SOURCES[relpath]
        if actual_sha != spec["sha256"]:
            errors.append(f"{relpath}: SHA-256 mismatch {actual_sha} != {spec['sha256']}")
        if len(raw) != spec["bytes"]:
            errors.append(f"{relpath}: byte length mismatch {len(raw)} != {spec['bytes']}")
        records.append({
            "path": relpath,
            "tier": spec["tier"],
            "bytes": len(raw),
            "sha256": actual_sha,
            "source": source,
        })

    by_sha: Dict[str, list[str]] = defaultdict(list)
    for record in records:
        by_sha[record["sha256"]].append(record["path"])
    duplicates = [
        {"sha256": key, "paths": sorted(paths)}
        for key, paths in sorted(by_sha.items())
        if len(paths) > 1
    ]
    canonical = next((r for r in records if r["path"] == CANONICAL_SOURCE_PATH), None)
    alias = next((r for r in records if r["path"] == CANONICAL_ALIAS_PATH), None)
    if canonical and alias and canonical["sha256"] != alias["sha256"]:
        errors.append("canonical source and canonical byte alias are not byte-identical")

    return {
        "schema": "HHS_SPI_HARMONICODE_SOURCE_INVENTORY_V1",
        "audited_main_sha": AUDITED_MAIN_SHA,
        "expected_path_count": len(EXPECTED_HARMONICODE_SOURCES),
        "discovered_path_count": len(discovered),
        "unique_source_hash_count": len(by_sha),
        "records": records,
        "duplicate_source_groups": duplicates,
        "errors": errors,
        "ok": not errors,
    }


def _alias_occurrences(source: str, registry: Mapping[str, Any]) -> Iterable[Dict[str, Any]]:
    for binding in _ALIAS_BINDINGS:
        proof_id = binding["proof_id"]
        proof = registry.get(proof_id)
        if proof is None:
            raise SPICorpusError(f"alias binding references missing registry proof {proof_id}")
        for variant in binding["variants"]:
            cursor = 0
            while True:
                start = source.find(variant, cursor)
                if start < 0:
                    break
                end = start + len(variant)
                yield {
                    "kind": "REGISTERED_FRAGMENT",
                    "expression": variant,
                    "start": start,
                    "end": end,
                    "coverage_state": proof.coverage_state,
                    "projection_id": proof_id,
                    "profile": proof.profile,
                    "binding_role": binding["role"],
                    "result": proof.to_dict().get("result"),
                    "reason": "source-bound registered scalar proof/profile",
                    "canonical_admission": False,
                }
                cursor = start + 1


def _find_balanced_end(source: str, opener_at: int) -> int | None:
    opener = source[opener_at]
    stack = [opener]
    quote = ""
    escaped = False
    for index in range(opener_at + 1, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
        elif char in "([":
            stack.append(char)
        elif char in ")]":
            expected = ")" if stack[-1] == "(" else "]"
            if char == expected:
                stack.pop()
                if not stack:
                    return index + 1
            else:
                return None
    return None


def _call_occurrences(source: str) -> Iterable[Dict[str, Any]]:
    for match in CALL_NAME_RE.finditer(source):
        name = match.group(1)
        opener_at = match.end() - 1
        end = _find_balanced_end(source, opener_at)
        if end is None:
            continue
        policy = SYMBOLIC_CALL_FAMILIES[name]
        yield {
            "kind": "FUNCTION_CALL",
            "expression": source[match.start():end],
            "start": match.start(),
            "end": end,
            "coverage_state": policy["coverage_state"],
            "projection_id": policy["projection_id"],
            "profile": "SYMBOLIC-FUNCTION-FAMILY-v1",
            "binding_role": "FUNCTION_FAMILY",
            "result": None,
            "reason": policy["reason"],
            "canonical_admission": False,
        }


def _radical_occurrences(source: str) -> Iterable[Dict[str, Any]]:
    for match in re.finditer(r"√\s*\(", source):
        opener_at = source.find("(", match.start(), match.end() + 1)
        if opener_at < 0:
            continue
        end = _find_balanced_end(source, opener_at)
        if end is None:
            continue
        yield {
            "kind": "RADICAL",
            "expression": source[match.start():end],
            "start": match.start(),
            "end": end,
            "coverage_state": SYMBOLIC,
            "projection_id": "SPI-SQRT-OP-FAMILY",
            "profile": "SYMBOLIC-RADICAL-FAMILY-v1",
            "binding_role": "FUNCTION_FAMILY",
            "result": None,
            "reason": "unicode radical remains symbolic until a registered exact radical profile closes",
            "canonical_admission": False,
        }


def _power_occurrences(source: str, registry: Mapping[str, Any]) -> Iterable[Dict[str, Any]]:
    alias_by_text: Dict[str, Dict[str, Any]] = {}
    for binding in _ALIAS_BINDINGS:
        proof = registry[binding["proof_id"]]
        for variant in binding["variants"]:
            alias_by_text[variant] = {
                "coverage_state": proof.coverage_state,
                "projection_id": proof.proof_id,
                "profile": proof.profile,
                "binding_role": binding["role"],
                "result": proof.to_dict().get("result"),
            }

    for regex in (ASCII_POWER_RE, SUPERSCRIPT_POWER_RE):
        for match in regex.finditer(source):
            text = match.group(0)
            binding = alias_by_text.get(text)
            if binding:
                state = binding["coverage_state"]
                projection_id = binding["projection_id"]
                profile = binding["profile"]
                role = binding["binding_role"]
                result = binding["result"]
                reason = "power token has registered scalar proof/profile"
            else:
                state = MISSING_PROJECTION
                projection_id = None
                profile = "UNREGISTERED-POWER-v1"
                role = "UNREGISTERED_SCALAR_CANDIDATE"
                result = None
                reason = "power token has no registered scalar projection proof"
            yield {
                "kind": "POWER",
                "expression": text,
                "start": match.start(),
                "end": match.end(),
                "coverage_state": state,
                "projection_id": projection_id,
                "profile": profile,
                "binding_role": role,
                "result": result,
                "reason": reason,
                "canonical_admission": False,
            }


def _integer_occurrences(source: str) -> Iterable[Dict[str, Any]]:
    for match in INTEGER_RE.finditer(source):
        text = match.group(0)
        value = int(text)
        yield {
            "kind": "INTEGER_LITERAL",
            "expression": text,
            "start": match.start(),
            "end": match.end(),
            "coverage_state": PROVEN,
            "projection_id": "EXACT-INTEGER-LITERAL-v1",
            "profile": "EXACT-INTEGER-LITERAL-v1",
            "binding_role": "LEXICAL_LITERAL",
            "result": value,
            "reason": "integer literal is its own exact scalar boundary value",
            "canonical_admission": False,
        }

    for match in SUPERSCRIPT_INTEGER_RE.finditer(source):
        text = match.group(0)
        value = int(text.translate(_SUPERSCRIPT_TO_ASCII))
        yield {
            "kind": "SUPERSCRIPT_INTEGER_LITERAL",
            "expression": text,
            "start": match.start(),
            "end": match.end(),
            "coverage_state": PROVEN,
            "projection_id": "EXACT-SUPERSCRIPT-INTEGER-LITERAL-v1",
            "profile": "EXACT-INTEGER-LITERAL-v1",
            "binding_role": "LEXICAL_LITERAL",
            "result": value,
            "reason": "superscript integer literal decodes exactly to an integer",
            "canonical_admission": False,
        }


def scalar_candidates(source: str, registry: Mapping[str, Any] | None = None) -> Sequence[Dict[str, Any]]:
    registry = dict(registry or build_registry())
    raw = []
    raw.extend(_alias_occurrences(source, registry))
    raw.extend(_call_occurrences(source))
    raw.extend(_radical_occurrences(source))
    raw.extend(_power_occurrences(source, registry))
    raw.extend(_integer_occurrences(source))

    seen = set()
    candidates = []
    for item in sorted(
        raw,
        key=lambda x: (
            int(x["start"]),
            int(x["end"]),
            str(x["kind"]),
            str(x.get("projection_id") or ""),
            str(x["expression"]),
        ),
    ):
        key = (
            item["start"],
            item["end"],
            item["kind"],
            item.get("projection_id"),
            item["expression"],
        )
        if key in seen:
            continue
        seen.add(key)
        body = dict(item)
        body["schema"] = CANDIDATE_SCHEMA
        body["span"] = _span(source, item["start"], item["end"])
        body["candidate_receipt_sha256"] = _digest({
            k: body[k]
            for k in sorted(body)
            if k != "candidate_receipt_sha256"
        })
        candidates.append(body)
    return tuple(candidates)


def source_coverage_record(
    path: str,
    source: str,
    *,
    tier: str,
    raw_sha256: str,
    registry: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    from native_projects.hhs_harmonicode_language.hhs_harmonicode_parser_v1 import parse_source

    registry = dict(registry or build_registry())
    ast = parse_source(source)
    parser_errors = [d for d in ast.get("diagnostics", []) if d.get("severity") == "ERROR"]
    candidates = scalar_candidates(source, registry)
    counts = Counter(item["coverage_state"] for item in candidates)
    record = {
        "schema": "HHS_SPI_CORPUS_SOURCE_COVERAGE_V1",
        "path": path,
        "tier": tier,
        "bytes": len(source.encode("utf-8")),
        "raw_sha256": raw_sha256,
        "parser_version": ast.get("parser_version"),
        "parser_source_sha256": ast.get("source_sha256"),
        "parser_node_count": len(ast.get("nodes", [])),
        "parser_diagnostics": ast.get("diagnostics", []),
        "parser_error_count": len(parser_errors),
        "source_spans_preserved": bool(ast.get("source_spans_preserved")),
        "nested_expression_ast_complete": False,
        "coverage_surface": "parser-bound exact source identity + lexical scalar-candidate grammar v1",
        "candidate_count": len(candidates),
        "candidate_counts": {
            state: counts.get(state, 0)
            for state in (PROVEN, SYMBOLIC, UNSUPPORTED_DOMAIN, MISSING_PROJECTION)
        },
        "all_unregistered_fail_closed": all(
            c["coverage_state"] != PROVEN or c.get("projection_id") is not None
            for c in candidates
        ),
        "canonical_admission_authority": False,
        "candidates": list(candidates),
    }
    record["record_sha256"] = _digest(record)
    return record


def repository_coverage_manifest(repo_root: Path) -> Dict[str, Any]:
    repo_root = Path(repo_root)
    registry = build_registry()
    inventory = validate_source_inventory(repo_root)
    if not inventory["ok"]:
        raise SPICorpusError(f"source inventory invalid: {inventory['errors']}")

    records_by_sha: Dict[str, Dict[str, Any]] = {}
    path_records = []
    for inventory_record in inventory["records"]:
        source = inventory_record["source"]
        source_sha = inventory_record["sha256"]
        if source_sha not in records_by_sha:
            records_by_sha[source_sha] = source_coverage_record(
                inventory_record["path"],
                source,
                tier=inventory_record["tier"],
                raw_sha256=source_sha,
                registry=registry,
            )
        coverage = records_by_sha[source_sha]
        path_records.append({
            "path": inventory_record["path"],
            "tier": inventory_record["tier"],
            "raw_sha256": source_sha,
            "coverage_record_sha256": coverage["record_sha256"],
            "deduplicated_to_path": coverage["path"],
        })

    unique_records = [records_by_sha[key] for key in sorted(records_by_sha)]
    total_counts = Counter()
    missing_groups: Dict[str, Dict[str, Any]] = {}
    for record in unique_records:
        for state, count in record["candidate_counts"].items():
            total_counts[state] += count
        for candidate in record["candidates"]:
            if candidate["coverage_state"] != MISSING_PROJECTION:
                continue
            expression = candidate["expression"]
            group = missing_groups.setdefault(expression, {
                "expression": expression,
                "count": 0,
                "paths": set(),
                "spans": [],
            })
            group["count"] += 1
            group["paths"].add(record["path"])
            group["spans"].append({
                "path": record["path"],
                "start": candidate["span"]["start"],
                "end": candidate["span"]["end"],
            })

    missing = []
    for expression in sorted(missing_groups):
        group = missing_groups[expression]
        missing.append({
            "expression": expression,
            "count": group["count"],
            "paths": sorted(group["paths"]),
            "spans": sorted(group["spans"], key=lambda v: (v["path"], v["start"], v["end"])),
        })

    parser_error_count = sum(r["parser_error_count"] for r in unique_records)
    candidate_counts = {
        state: total_counts.get(state, 0)
        for state in (PROVEN, SYMBOLIC, UNSUPPORTED_DOMAIN, MISSING_PROJECTION)
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "authority_boundary": {
            "projection_only": True,
            "canonical_admission_authority": False,
            "native_source_rewriting": False,
            "ordered_product_commutation": False,
            "hash72_hash216_canonical_minting": False,
        },
        "coverage_policy": {
            "nested_expression_ast_complete": False,
            "coverage_surface": "parser-bound exact source identity + lexical scalar-candidate grammar v1",
            "unregistered_candidates": MISSING_PROJECTION,
            "all_unregistered_fail_closed": True,
            "strict_complete_requires_missing_zero": True,
        },
        "inventory": {
            "path_count": inventory["discovered_path_count"],
            "unique_source_hash_count": inventory["unique_source_hash_count"],
            "expected_path_count": inventory["expected_path_count"],
            "duplicate_source_groups": inventory["duplicate_source_groups"],
        },
        "path_records": sorted(path_records, key=lambda v: v["path"]),
        "unique_source_records": unique_records,
        "candidate_counts": candidate_counts,
        "missing_projection_count": candidate_counts[MISSING_PROJECTION],
        "missing_projection_groups": missing,
        "parser_error_count": parser_error_count,
        "strict_complete": parser_error_count == 0 and candidate_counts[MISSING_PROJECTION] == 0,
    }
    manifest["manifest_sha256"] = _digest(manifest)
    return manifest


def validate_repository_corpus(repo_root: Path) -> Dict[str, Any]:
    try:
        manifest = repository_coverage_manifest(repo_root)
    except (OSError, SPICorpusError) as exc:
        return {
            "schema": "HHS_SPI_REPOSITORY_CORPUS_VALIDATION_V1",
            "ok": False,
            "errors": [str(exc)],
            "canonical_admission_authority": False,
        }

    errors = []
    if manifest["inventory"]["path_count"] != 6:
        errors.append("expected exactly six registered .harmonicode source paths")
    if manifest["inventory"]["unique_source_hash_count"] != 5:
        errors.append("expected exactly five unique .harmonicode source bodies")
    if manifest["parser_error_count"] != 0:
        errors.append(f"parser errors present: {manifest['parser_error_count']}")
    if not manifest["coverage_policy"]["all_unregistered_fail_closed"]:
        errors.append("unregistered candidates are not fail-closed")
    if any(
        candidate.get("canonical_admission")
        for record in manifest["unique_source_records"]
        for candidate in record["candidates"]
    ):
        errors.append("scalar candidate incorrectly claims canonical admission")
    return {
        "schema": "HHS_SPI_REPOSITORY_CORPUS_VALIDATION_V1",
        "ok": not errors,
        "errors": errors,
        "path_count": manifest["inventory"]["path_count"],
        "unique_source_hash_count": manifest["inventory"]["unique_source_hash_count"],
        "candidate_counts": manifest["candidate_counts"],
        "missing_projection_count": manifest["missing_projection_count"],
        "strict_complete": manifest["strict_complete"],
        "manifest_sha256": manifest["manifest_sha256"],
        "canonical_admission_authority": False,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Validate or emit repository-wide SPI corpus coverage")
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--manifest", action="store_true", help="emit deterministic repository corpus manifest")
    parser.add_argument("--validate", action="store_true", help="emit repository corpus validation summary")
    parser.add_argument(
        "--strict-complete",
        action="store_true",
        help="succeed only when no scalar candidate remains MISSING_PROJECTION",
    )
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()

    if args.manifest:
        print(json.dumps(repository_coverage_manifest(root), indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    result = validate_repository_corpus(root)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    if not result["ok"]:
        return 1
    if args.strict_complete and not result["strict_complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
