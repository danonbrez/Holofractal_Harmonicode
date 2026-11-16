"""Source-preserving HARMONICODE mathematical proof-span discovery.

This indexes statements *inside* the existing full indexed corpus, not just
file paths. Every emitted excerpt is verbatim, position-addressed and source
SHA-256 bound. The scanner is an additive retrieval projection; proof status
and mathematical authority belong to the inherited source and runtime gates.

Do not infer nonexistence of a theorem from a scanner miss. Source omissions,
binary files, oversized files and read failures remain visible in the receipt.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

SCHEMA = "HHS_PASS220_CUMULATIVE_PROOF_SOURCE_SPAN_INDEX_V1"
TEXT_SUFFIXES = frozenset({
    ".md", ".txt", ".rst", ".adoc", ".tex", ".lean", ".v", ".wl",
    ".py", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".json",
    ".harmonicode", ".yaml", ".yml",
})
NAMED = re.compile(
    r"^\s*(?:(?:#{1,6})\s+)?"
    r"(?:Lemma|Theorem|Proof|Derivation|Corollary|Proposition|"
    r"Identity|Claim|Axiom|Invariant|Definition)\b",
    re.IGNORECASE,
)
FORMAL = re.compile(
    r"^\s*(?:theorem|lemma|example|def|instance|"
    r"Theorem|Lemma|Corollary|Proposition|Definition)\s+"
    r"[A-Za-z_\u00c0-\uffff][\w'.\u00c0-\uffff]*",
)
MODULE = re.compile(r"^\s*#\s+Module\s+\d+\b", re.IGNORECASE)
MATH_MARKER = re.compile(
    r"(?<![=])(?:==|:=|≡|⇒|⟹|↔|≤|≥|∈|∉|⊢|∴|"
    r"\\(?:frac|sqrt|equiv|Rightarrow|implies|vdash|forall|exists)\b)"
)
HEADING = re.compile(r"^#{1,6}\s+")
FENCE = re.compile(r"^\s*(?:```|~~~)")
MAX_SOURCE_BYTES = 8_000_000


class ProofSpanIndexError(ValueError):
    pass


def _seal(obj: object) -> str:
    return sha256(json.dumps(
        obj, sort_keys=True, ensure_ascii=False,
        allow_nan=False, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()


def extract_source_spans(
    *, path: str, source_text: str, source_git_blob: str | None = None,
) -> dict[str, Any]:
    """Index exact named proof spans and mathematical expression carriers.

    Each named marker includes its following body through the next named marker
    or markdown section boundary. Mathematical lines are separate provenance
    references: they are not scalarized, rewritten, or independently certified.
    """
    if not path or not isinstance(path, str) or not isinstance(source_text, str):
        raise ProofSpanIndexError("INVALID_SOURCE")
    lines = source_text.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))
    entries: list[dict[str, Any]] = []
    named_starts: list[int] = []
    module = ""
    for i, raw in enumerate(lines):
        stripped = raw.rstrip("\r\n")
        if MODULE.match(stripped):
            module = stripped.strip()
        if NAMED.match(stripped) or (
            Path(path).suffix.lower() in {".lean", ".v"}
            and FORMAL.match(stripped)
        ):
            named_starts.append(i)
        # Don't parse formulas: preserve exact user text and positions.
        if MATH_MARKER.search(stripped) and stripped.strip():
            entries.append({
                "kind": "MATHEMATICAL_SOURCE_LINE",
                "start_line": i + 1, "end_line": i + 1,
                "start_char": starts[i], "end_char": starts[i+1],
                "source_text": raw,
                "module_heading": module,
            })
    for pos, begin in enumerate(named_starts):
        limit = named_starts[pos + 1] if pos + 1 < len(named_starts) else len(lines)
        if begin + 1 < limit:
            for j in range(begin + 1, limit):
                if HEADING.match(lines[j]) and not MODULE.match(lines[j]):
                    limit = j
                    break
                if MODULE.match(lines[j]):
                    limit = j
                    break
        # The complete designated span is retained, never only the name.
        entries.append({
            "kind": "NAMED_PROOF_SPAN",
            "start_line": begin + 1, "end_line": limit,
            "start_char": starts[begin], "end_char": starts[limit],
            "source_text": "".join(lines[begin:limit]),
            "module_heading": next(
                (lines[k].strip() for k in range(begin, -1, -1)
                 if MODULE.match(lines[k])), "",
            ),
        })
    entries.sort(key=lambda e: (
        e["start_char"], 0 if e["kind"] == "NAMED_PROOF_SPAN" else 1,
        e["end_char"],
    ))
    for entry in entries:
        entry["source_span_sha256"] = sha256(
            entry["source_text"].encode("utf-8")).hexdigest()
        entry["proof_admission_inferred"] = False
    result = {
        "schema": SCHEMA,
        "path": path, "source_git_blob": source_git_blob,
        "source_sha256": sha256(source_text.encode("utf-8")).hexdigest(),
        "source_line_count": len(lines),
        "named_proof_span_count": sum(
            e["kind"] == "NAMED_PROOF_SPAN" for e in entries),
        "mathematical_source_line_count": sum(
            e["kind"] == "MATHEMATICAL_SOURCE_LINE" for e in entries),
        "entries": entries,
        "candidate_only": True, "source_text_preserved": True,
        "exhaustive_proof_claim": False,
    }
    result["index_sha256"] = _seal(result)
    return result


def build_repository_proof_span_index(
    root: Path, dependency_graph: Mapping[str, Any],
) -> dict[str, Any]:
    """Scan every eligible text file in the existing indexed graph.

    Never silently drop inaccessible/oversized or unreadable sources.
    """
    files = dependency_graph.get("files")
    if not isinstance(files, list):
        raise ProofSpanIndexError("REPOSITORY_GRAPH_FILES_REQUIRED")
    out = []
    unavailable = []
    examined = 0
    for record in sorted(files, key=lambda r: str(r.get("path", ""))):
        path = str(record.get("path", ""))
        if not path or Path(path).is_absolute() or ".." in Path(path).parts:
            raise ProofSpanIndexError("INVALID_INDEXED_PATH")
        if Path(path).suffix.lower() not in TEXT_SUFFIXES:
            continue
        file_path = root / path
        if not file_path.is_file():
            unavailable.append({"path": path, "reason": "SOURCE_NOT_AVAILABLE"})
            continue
        if file_path.stat().st_size > MAX_SOURCE_BYTES:
            unavailable.append({"path": path, "reason": "SOURCE_EXCEEDS_SCAN_LIMIT"})
            continue
        try:
            source = file_path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            unavailable.append({"path": path, "reason": "SOURCE_DECODE_FAILED"})
            continue
        examined += 1
        projection = extract_source_spans(
            path=path, source_text=source,
            source_git_blob=record.get("git_blob"),
        )
        if projection["entries"]:
            out.append(projection)
    result = {
        "schema": SCHEMA + "_REPOSITORY",
        "source_dependency_graph_root_hash216": dependency_graph.get(
            "roots", {}).get("graph_root_hash216"),
        "indexed_file_count": len(files),
        "examined_text_files": examined,
        "files_with_discoverable_spans": len(out),
        "named_proof_span_count": sum(
            p["named_proof_span_count"] for p in out),
        "mathematical_source_line_count": sum(
            p["mathematical_source_line_count"] for p in out),
        "source_indexes": out,
        "unavailable_sources": unavailable,
        "candidate_only": True,
        "all_proofs_discovered": False,
        "no_missing_source_interpreted_as_absence": True,
    }
    result["index_sha256"] = _seal(result)
    return result
