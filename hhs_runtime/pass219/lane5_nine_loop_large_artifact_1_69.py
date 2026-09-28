"""Pass 219 Lane 5 1.69 — streaming large-artifact attestation.

No foreign archive is executed or extracted. NPZ members are opened with
allow_pickle=False, gzip comparison records are streamed line by line, and ZIP
metadata are inspected without extraction.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA = "HHS_PASS219_LANE5_NINE_LOOP_LARGE_ARTIFACT_1_69"
P1 = 2147483647
P2 = 2147483629
EXPECTED_MATRIX_SHAPE = (424, 5431)
EXPECTED_COMPARISON_ROWS = 107053
EXPECTED_NONZERO_COORDINATE_UNION = 1018297
EXPECTED_CERTIFIED_RATIONAL_COORDINATES = 1014476
EXPECTED_TWO_PRIME_ONLY_COORDINATES = 3821
EXPECTED_TWO_PRIME_ONLY_COMPARISON = 3401
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

FROZEN_SOURCE_SHA256 = {
    "p1": "75a52ebb4526bdb788ae8101e4908d52579637b6aaca1a308e4d783b4a8afe86",
    "p2": "13c231664403d35e8ad68747302c7bc26bcc9b1b567d0da0d65444c980c8eb97",
    "comparison": "d01e62885b74d13650b44baf8da3e42d15bab35c99f6ee778e66df4059ecf37d",
    "septuple": "082abcea6a66fb434b24938236f443f2703e7e76ded8911f46ffffa292a2c5e1",
}
FROZEN_SHARED_MEMBER_SHA256 = {
    "L": "cbbd5f990c53684d7ae650b40fcb5656e02261b53da5f6a7d8c819c92f2828f8",
    "V": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "log": "00dd2aa118f9c3d0e8fdf5126ce151b66af4888a9faba53877d0dd72a35844b2",
    "n": "b0bd73e6922c0d2496dbcb99eac08eb5870090e59f6e06b1eb477d540002a5cd",
    "pivots": "8a6f1d9e21942787fd002748da6753e5a057662c95189112df00b8953df18bd6",
}
FROZEN_ARRAY_NAMES = {
    "E0", "L", "V", "fix_note", "log", "n", "p", "pivots", "tau_N3LL"
}
FROZEN_COMPARISON_NORMALIZED_SHA256 = (
    "884b05ed4118ed372329c8b002b895dfa98bd92fe72cdd0f88b47cef94448d11"
)
FROZEN_SEPTUPLE_STRUCTURE_SHA256 = (
    "606c5db22ac881a92835cf12e7077d0093c8b599b5205d3e0752be91e82c3967"
)


class Lane5NineLoopLargeArtifactError(ValueError):
    pass


def stream_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(manifest_text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in manifest_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        digest, rel = parts
        digest = digest.lower()
        rel = rel.lstrip("*").lstrip("./")
        if not _SHA256_RE.fullmatch(digest):
            raise Lane5NineLoopLargeArtifactError("manifest contains invalid SHA-256")
        if rel in out and out[rel] != digest:
            raise Lane5NineLoopLargeArtifactError("manifest contains conflicting duplicate path")
        out[rel] = digest
    return out


def resolve_manifest_digest(
    manifest: Mapping[str, str],
    *,
    relative_path: str,
) -> str:
    relative_path = relative_path.lstrip("./")
    exact = manifest.get(relative_path)
    if exact is not None:
        return exact
    basename = Path(relative_path).name
    matches = [(path, digest) for path, digest in manifest.items() if Path(path).name == basename]
    if len(matches) != 1:
        raise Lane5NineLoopLargeArtifactError(
            f"expected one manifest entry for {relative_path}, got {len(matches)}"
        )
    return matches[0][1]


def attest_manifest_member(
    path: str | Path,
    *,
    manifest: Mapping[str, str],
    relative_path: str,
) -> dict[str, Any]:
    p = Path(path)
    digest = stream_sha256(p)
    expected = resolve_manifest_digest(manifest, relative_path=relative_path)
    if digest != expected:
        raise Lane5NineLoopLargeArtifactError(
            f"SHA-256 mismatch for {relative_path}: {digest} != {expected}"
        )
    return {
        "relative_path": relative_path,
        "sha256": digest,
        "bytes": p.stat().st_size,
        "manifest_member_verified": True,
    }


def inspect_npz(path: str | Path) -> dict[str, Any]:
    import numpy as np

    arrays: list[dict[str, Any]] = []
    found_matrix_shape = False
    dense_nnz = None
    sparse_shape = None
    sparse_nnz = None

    with np.load(path, allow_pickle=False) as archive:
        for key in sorted(archive.files):
            arr = archive[key]
            shape = tuple(int(v) for v in arr.shape)
            record = {
                "name": key,
                "shape": list(shape),
                "dtype": str(arr.dtype),
                "size": int(arr.size),
                "nbytes": int(arr.nbytes),
                "content_sha256": hashlib.sha256(
                    arr.tobytes(order="C")
                ).hexdigest(),
            }
            if arr.size <= 16:
                scalar_values = arr.reshape(-1).tolist()
                record["small_values"] = [
                    value.item() if hasattr(value, "item") else value
                    for value in scalar_values
                ]
            arrays.append(record)

            if shape == EXPECTED_MATRIX_SHAPE:
                found_matrix_shape = True
                mask = np.asarray(arr != 0, dtype=np.uint8)
                dense_nnz = int(np.count_nonzero(mask))
                record["nonzero_support_sha256"] = hashlib.sha256(
                    np.packbits(mask.reshape(-1), bitorder="little").tobytes()
                ).hexdigest()

            if key.lower() == "shape" and arr.size == 2:
                candidate = tuple(int(v) for v in arr.reshape(-1).tolist())
                if candidate == EXPECTED_MATRIX_SHAPE:
                    sparse_shape = candidate
                    found_matrix_shape = True

        names = {item["name"] for item in arrays}
        if {"data", "indices", "indptr"}.issubset(names):
            data = archive["data"]
            sparse_nnz = int(data.size)

    if not found_matrix_shape:
        raise Lane5NineLoopLargeArtifactError(
            "NPZ does not expose the expected 424 x 5431 matrix shape"
        )

    logical = {
        "arrays": arrays,
        "expected_matrix_shape_verified": True,
        "dense_nnz": dense_nnz,
        "sparse_shape": list(sparse_shape) if sparse_shape is not None else None,
        "sparse_nnz": sparse_nnz,
        "allow_pickle": False,
    }
    canonical = json.dumps(logical, sort_keys=True, separators=(",", ":")).encode()
    logical["structure_sha256"] = hashlib.sha256(canonical).hexdigest()
    return logical


def inspect_comparison_gzip(path: str | Path) -> dict[str, Any]:
    data_rows = 0
    comments = 0
    blanks = 0
    field_histogram: Counter[int] = Counter()
    token_class_histogram: Counter[str] = Counter()
    normalized = hashlib.sha256()
    first_rows: list[str] = []
    last_row = ""
    mismatch_marker_count = 0

    with gzip.open(path, "rt", encoding="utf-8", errors="strict") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped:
                blanks += 1
                continue
            if stripped.startswith("#"):
                comments += 1
                normalized.update(("#" + stripped.lstrip("#").strip() + "\n").encode())
                continue

            lowered = stripped.lower()
            if "mismatch" in lowered and not any(
                marker in lowered for marker in ("mismatches: 0", "mismatch=0", "mismatch 0")
            ):
                mismatch_marker_count += 1

            fields = stripped.split()
            field_histogram[len(fields)] += 1
            classes = []
            for token in fields:
                if token.lstrip("+-").isdigit():
                    classes.append("I")
                elif "/" in token:
                    n, _, d = token.partition("/")
                    classes.append(
                        "R" if n.lstrip("+-").isdigit() and d.isdigit() else "S"
                    )
                elif token in {"ah","bh","ch","dh","eh","fh","yu","yv","yw"}:
                    classes.append("L")
                else:
                    classes.append("S")
            token_class_histogram["".join(classes)] += 1
            normalized.update((" ".join(fields) + "\n").encode())
            if len(first_rows) < 3:
                first_rows.append(" ".join(fields))
            last_row = " ".join(fields)
            data_rows += 1

    if data_rows != EXPECTED_COMPARISON_ROWS:
        raise Lane5NineLoopLargeArtifactError(
            f"comparison row count {data_rows} != {EXPECTED_COMPARISON_ROWS}"
        )
    if mismatch_marker_count:
        raise Lane5NineLoopLargeArtifactError(
            f"comparison contains {mismatch_marker_count} mismatch markers"
        )

    return {
        "comparison_rows": data_rows,
        "comment_lines": comments,
        "blank_lines": blanks,
        "field_count_histogram": dict(sorted(field_histogram.items())),
        "token_class_histogram": dict(sorted(token_class_histogram.items())),
        "normalized_sha256": normalized.hexdigest(),
        "first_row_sha256": hashlib.sha256(first_rows[0].encode()).hexdigest()
            if first_rows else None,
        "last_row_sha256": hashlib.sha256(last_row.encode()).hexdigest()
            if last_row else None,
        "mismatch_marker_count": mismatch_marker_count,
        "streaming_only": True,
    }


def inspect_zip_metadata(path: str | Path) -> dict[str, Any]:
    members: list[dict[str, Any]] = []
    total_uncompressed = 0
    with zipfile.ZipFile(path, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise Lane5NineLoopLargeArtifactError(f"ZIP CRC failure at member {bad}")
        for info in sorted(archive.infolist(), key=lambda x: x.filename):
            if info.is_dir():
                continue
            if info.filename.startswith("/") or ".." in Path(info.filename).parts:
                raise Lane5NineLoopLargeArtifactError("unsafe ZIP member path")
            total_uncompressed += int(info.file_size)
            members.append({
                "name": info.filename,
                "compressed_bytes": int(info.compress_size),
                "uncompressed_bytes": int(info.file_size),
                "crc32": f"{info.CRC:08x}",
            })

    logical = {
        "member_count": len(members),
        "total_uncompressed_bytes": total_uncompressed,
        "members": members,
        "archive_extracted": False,
    }
    canonical = json.dumps(logical, sort_keys=True, separators=(",", ":")).encode()
    logical["structure_sha256"] = hashlib.sha256(canonical).hexdigest()
    return logical


def discover_large_artifact_schema(
    *,
    manifest_text: str,
    p1_npz: str | Path,
    p2_npz: str | Path,
    comparison_gz: str | Path,
    septuple_zip: str | Path,
) -> dict[str, Any]:
    """Observe each foreign representation independently before equivalence is frozen."""
    manifest = parse_manifest(manifest_text)
    targets = {
        "p1": ("amplitude/E9_symbol_complete_mod2147483647.npz", Path(p1_npz)),
        "p2": ("amplitude/E9_symbol_complete_mod2147483629.npz", Path(p2_npz)),
        "comparison": (
            "validation/records/09_septuple_vs_quintuple_107053_words.txt.gz",
            Path(comparison_gz),
        ),
        "septuple": ("MHV9/MHV9septuples.zip", Path(septuple_zip)),
    }

    source = {
        key: attest_manifest_member(path, manifest=manifest, relative_path=rel)
        for key, (rel, path) in targets.items()
    }
    p1 = inspect_npz(p1_npz)
    p2 = inspect_npz(p2_npz)
    comparison = inspect_comparison_gzip(comparison_gz)
    septuple = inspect_zip_metadata(septuple_zip)

    discovery = {
        "schema": SCHEMA + "_SCHEMA_DISCOVERY",
        "source": source,
        "prime_lanes": {
            str(P1): p1,
            str(P2): p2,
        },
        "comparison": comparison,
        "septuple_archive": septuple,
        "published_relations": {
            "quintuple_count": 424,
            "weight13_dimension": 5431,
            "nonzero_coordinate_union": EXPECTED_NONZERO_COORDINATE_UNION,
            "certified_rational_coordinates": EXPECTED_CERTIFIED_RATIONAL_COORDINATES,
            "two_prime_only_coordinates": EXPECTED_TWO_PRIME_ONLY_COORDINATES,
            "comparison_rows": EXPECTED_COMPARISON_ROWS,
            "two_prime_only_comparison_rows": EXPECTED_TWO_PRIME_ONLY_COMPARISON,
        },
        "cross_prime_container_identity_required": False,
        "logical_equivalence_contract_frozen": False,
        "native_hash216_composition_frozen": False,
        "candidate_only": True,
        "full_materialization": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_canonical_authority": False,
    }
    canonical = json.dumps(discovery, sort_keys=True, separators=(",", ":")).encode()
    discovery["discovery_sha256"] = hashlib.sha256(canonical).hexdigest()
    return discovery


def _array_map(lane: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    arrays = lane.get("arrays", [])
    result = {str(record["name"]): record for record in arrays}
    if set(result) != FROZEN_ARRAY_NAMES:
        raise Lane5NineLoopLargeArtifactError(
            "prime-lane NPZ member roles differ from the observed 1.69 inventory"
        )
    return result


def derive_public_logical_equivalence(discovery: Mapping[str, Any]) -> dict[str, Any]:
    """Derive the frozen relation between exact, source-attested prime lanes."""
    source = discovery.get("source", {})
    for role, expected_sha in FROZEN_SOURCE_SHA256.items():
        record = source.get(role)
        if not isinstance(record, Mapping) or record.get("sha256") != expected_sha:
            raise Lane5NineLoopLargeArtifactError(
                f"frozen public source identity mismatch for {role}"
            )
        if record.get("manifest_member_verified") is not True:
            raise Lane5NineLoopLargeArtifactError(
                f"manifest membership missing for {role}"
            )

    lanes = discovery.get("prime_lanes", {})
    lane1 = lanes.get(str(P1))
    lane2 = lanes.get(str(P2))
    if not isinstance(lane1, Mapping) or not isinstance(lane2, Mapping):
        raise Lane5NineLoopLargeArtifactError("both prime lanes are required")

    a1 = _array_map(lane1)
    a2 = _array_map(lane2)

    e1, e2 = a1["E0"], a2["E0"]
    for record in (e1, e2):
        if record.get("shape") != [424, 5431] or record.get("dtype") != "int64":
            raise Lane5NineLoopLargeArtifactError("E0 geometry/type mismatch")
        if int(record.get("size", -1)) != 424 * 5431:
            raise Lane5NineLoopLargeArtifactError("E0 size mismatch")
    if lane1.get("dense_nnz") != EXPECTED_NONZERO_COORDINATE_UNION:
        raise Lane5NineLoopLargeArtifactError("p1 E0 nonzero count mismatch")
    if lane2.get("dense_nnz") != EXPECTED_NONZERO_COORDINATE_UNION:
        raise Lane5NineLoopLargeArtifactError("p2 E0 nonzero count mismatch")

    support1 = e1.get("nonzero_support_sha256")
    support2 = e2.get("nonzero_support_sha256")
    if not support1 or support1 != support2:
        raise Lane5NineLoopLargeArtifactError(
            "prime-lane E0 nonzero support geometry does not match"
        )

    for name, expected_sha in FROZEN_SHARED_MEMBER_SHA256.items():
        if a1[name].get("content_sha256") != expected_sha:
            raise Lane5NineLoopLargeArtifactError(
                f"p1 shared member {name} identity mismatch"
            )
        if a2[name].get("content_sha256") != expected_sha:
            raise Lane5NineLoopLargeArtifactError(
                f"p2 shared member {name} identity mismatch"
            )

    if a1["L"].get("small_values") != [9] or a2["L"].get("small_values") != [9]:
        raise Lane5NineLoopLargeArtifactError("L loop scalar mismatch")
    if a1["n"].get("small_values") != [13] or a2["n"].get("small_values") != [13]:
        raise Lane5NineLoopLargeArtifactError("n basis scalar mismatch")
    if a1["p"].get("small_values") != [P1]:
        raise Lane5NineLoopLargeArtifactError("p1 lane provenance mismatch")
    if a2["p"].get("small_values") != [P2]:
        raise Lane5NineLoopLargeArtifactError("p2 lane provenance mismatch")

    for lane_arrays in (a1, a2):
        fix = lane_arrays["fix_note"]
        if fix.get("shape") != [] or not str(fix.get("dtype", "")).startswith("<U"):
            raise Lane5NineLoopLargeArtifactError("fix_note metadata role mismatch")
        tau = lane_arrays["tau_N3LL"]
        if tau.get("shape") != [1] or tau.get("dtype") != "int64":
            raise Lane5NineLoopLargeArtifactError("tau_N3LL lane role mismatch")
        pivots = lane_arrays["pivots"]
        if pivots.get("shape") != [424, 5] or pivots.get("dtype") != "int64":
            raise Lane5NineLoopLargeArtifactError("pivot geometry mismatch")

    comparison = discovery.get("comparison", {})
    if comparison.get("comparison_rows") != EXPECTED_COMPARISON_ROWS:
        raise Lane5NineLoopLargeArtifactError("comparison cardinality mismatch")
    if comparison.get("normalized_sha256") != FROZEN_COMPARISON_NORMALIZED_SHA256:
        raise Lane5NineLoopLargeArtifactError("comparison normalized identity mismatch")
    if comparison.get("mismatch_marker_count") != 0:
        raise Lane5NineLoopLargeArtifactError("comparison reports mismatches")

    septuple = discovery.get("septuple_archive", {})
    if septuple.get("structure_sha256") != FROZEN_SEPTUPLE_STRUCTURE_SHA256:
        raise Lane5NineLoopLargeArtifactError("septuple archive structure mismatch")
    if septuple.get("archive_extracted") is not False:
        raise Lane5NineLoopLargeArtifactError("septuple archive extraction is forbidden")

    relation = {
        "schema": SCHEMA + "_LOGICAL_EQUIVALENCE",
        "source_identities_frozen": True,
        "matrix_geometry": [424, 5431],
        "matrix_dtype": "int64",
        "nonzero_coordinate_count": EXPECTED_NONZERO_COORDINATE_UNION,
        "nonzero_support_sha256": support1,
        "shared_invariant_members": sorted(FROZEN_SHARED_MEMBER_SHA256),
        "prime_dependent_members": ["E0", "fix_note", "p", "tau_N3LL"],
        "p1": P1,
        "p2": P2,
        "comparison_rows": EXPECTED_COMPARISON_ROWS,
        "comparison_normalized_sha256": FROZEN_COMPARISON_NORMALIZED_SHA256,
        "septuple_structure_sha256": FROZEN_SEPTUPLE_STRUCTURE_SHA256,
        "literal_container_identity_required": False,
        "logical_equivalence_contract_frozen": True,
        "native_hash216_composition_frozen": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_canonical_authority": False,
    }
    canonical = json.dumps(relation, sort_keys=True, separators=(",", ":")).encode()
    relation["relation_sha256"] = hashlib.sha256(canonical).hexdigest()
    return relation


def build_large_artifact_receipt(*args: Any, **kwargs: Any) -> dict[str, Any]:
    raise Lane5NineLoopLargeArtifactError(
        "1.69 logical-equivalence contract is not frozen; "
        "run discover_large_artifact_schema first"
    )
