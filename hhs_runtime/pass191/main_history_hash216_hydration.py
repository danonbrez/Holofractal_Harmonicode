"""Deployment-time hydration of main-admitted PR invariant/contract logic.

This module scans the exact first-parent commit lineage of a requested Git ref,
selects PR-attributed changes that carry invariant/contract/enforcement logic,
and stores the exact selected unified-diff bytes as reversible 5,184-bit
(648-byte) encrypted Hash216 vector objects.

The vector store is an inherited Pass 174 persistence surface only. This module
does not mint a second VM81 authority, Hash72 commit clock, or mutation path.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass174.runtime import Hash216Array, Pass174Error
from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore

SCHEMA = "HHS_MAIN_HISTORY_GREEN_PR_HASH216_HYDRATION_V1"
FRAME_BYTES = 648
FRAME_HEADER_BYTES = 8
FRAME_PAYLOAD_BYTES = FRAME_BYTES - FRAME_HEADER_BYTES
ZERO_SHA256 = "0" * 64
GENESIS_IDENTITY = sha256(b"HHS-MAIN-HISTORY-HASH216-GENESIS-V1").hexdigest()
LEGACY_FOUNDATION_ROOT = sha256(
    b"HHS-MAIN-HISTORY-HASH216-FOUNDATION-V1"
).hexdigest()

_PR_PATTERNS = (
    re.compile(r"(?im)^Merge (?:pull request|PR) #(?P<number>[0-9]+)\b"),
    re.compile(r"(?m)\(#(?P<number>[0-9]+)\)\s*$"),
    re.compile(r"(?im)\bPR #(?P<number>[0-9]+)\b"),
)
_POLICY_PREFIXES = (
    ".github/workflows/",
    "contracts/",
    "deployment/",
    "deploy/",
    "schemas/",
    "tests/",
)
_POLICY_PATH_RE = re.compile(
    r"(?:contract|invariant|enforc|guard|verif|validat|authority|security|"
    r"receipt|membrane|constraint|rollback|promotion|admission|hash216|hash72|vm81)",
    re.IGNORECASE,
)
_LOGIC_RE = re.compile(
    rb"(?:invariant|contract|enforc|guard|admit|reject|fail[-_ ]?closed|"
    rb"authority|validat|verif|hash216|hash72|vm81|receipt|membrane|constraint|"
    rb"rollback|promotion|security|canonical|single.{0,12}authority)",
    re.IGNORECASE,
)
_TEXT_LOGIC_SUFFIXES = {
    ".c", ".cc", ".cpp", ".h", ".hpp", ".go", ".js", ".json", ".mjs", ".md",
    ".py", ".rs", ".rst", ".sh", ".sql", ".toml", ".ts", ".tsx", ".txt",
    ".yaml", ".yml",
}


class MainHistoryHydrationError(RuntimeError):
    """Fail-closed error for historical hydration."""


@dataclass(frozen=True)
class HydrationBounds:
    max_commits: int = 100_000
    max_artifact_bytes: int = 4 * 1024 * 1024
    max_total_logic_bytes: int = 256 * 1024 * 1024
    max_frames: int = 500_000
    max_manifest_bytes: int = 128 * 1024 * 1024

    def validate(self) -> "HydrationBounds":
        for name, value in self.__dict__.items():
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise MainHistoryHydrationError(f"HHS_HISTORY_BOUND_INVALID:{name}")
        return self


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _hash216(domain: str, payload: Any) -> str:
    previous = hash72_digest({"domain": domain, "lane": "PREVIOUS"}, payload)
    change = hash72_digest({"domain": domain, "lane": "CHANGE"}, payload)
    receipt = hash72_digest(
        {"domain": domain, "lane": "RECEIPT"},
        {"previous": previous, "change": change, "payload": payload},
    )
    combined = previous + change + receipt
    if len(combined) != 216:
        raise MainHistoryHydrationError("HHS_HISTORY_HASH216_LENGTH")
    return combined


def encode_frame(payload: bytes) -> bytes:
    body = bytes(payload)
    if len(body) > FRAME_PAYLOAD_BYTES:
        raise MainHistoryHydrationError("HHS_HISTORY_FRAME_PAYLOAD_TOO_LARGE")
    return (
        len(body).to_bytes(FRAME_HEADER_BYTES, "big")
        + body
        + bytes(FRAME_PAYLOAD_BYTES - len(body))
    )


def decode_frame(frame: bytes) -> bytes:
    raw = bytes(frame)
    if len(raw) != FRAME_BYTES:
        raise MainHistoryHydrationError("HHS_HISTORY_FRAME_LENGTH")
    length = int.from_bytes(raw[:FRAME_HEADER_BYTES], "big")
    if length > FRAME_PAYLOAD_BYTES:
        raise MainHistoryHydrationError("HHS_HISTORY_FRAME_HEADER")
    payload = raw[FRAME_HEADER_BYTES:FRAME_HEADER_BYTES + length]
    padding = raw[FRAME_HEADER_BYTES + length:]
    if any(padding):
        raise MainHistoryHydrationError("HHS_HISTORY_FRAME_NONZERO_PADDING")
    return payload


def _chunks(payload: bytes) -> Iterable[bytes]:
    if not payload:
        yield b""
        return
    for offset in range(0, len(payload), FRAME_PAYLOAD_BYTES):
        yield payload[offset:offset + FRAME_PAYLOAD_BYTES]


def _run_git(root: Path, *args: str, text: bool = False) -> bytes | str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise MainHistoryHydrationError(
            f"HHS_HISTORY_GIT_FAILED:{' '.join(args)}:{detail}"
        )
    if text:
        return completed.stdout.decode("utf-8", errors="surrogateescape").strip()
    return completed.stdout


def _resolve_commit(root: Path, ref: str) -> str:
    value = str(_run_git(root, "rev-parse", f"{ref}^{{commit}}", text=True))
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise MainHistoryHydrationError("HHS_HISTORY_REF_NOT_EXACT_COMMIT")
    return value


def _first_parent_commits(root: Path, commit: str, bounds: HydrationBounds) -> list[str]:
    raw = str(
        _run_git(root, "rev-list", "--reverse", "--first-parent", commit, text=True)
    )
    commits = [line for line in raw.splitlines() if line]
    if len(commits) > bounds.max_commits:
        raise MainHistoryHydrationError(
            f"HHS_HISTORY_COMMIT_LIMIT:{len(commits)}>{bounds.max_commits}"
        )
    return commits


def _parents(root: Path, commit: str) -> list[str]:
    raw = str(_run_git(root, "rev-list", "--parents", "-n", "1", commit, text=True))
    fields = raw.split()
    if not fields or fields[0] != commit:
        raise MainHistoryHydrationError("HHS_HISTORY_PARENT_PARSE")
    return fields[1:]


def _message(root: Path, commit: str) -> str:
    return str(_run_git(root, "show", "-s", "--format=%B", commit, text=True))


def _pr_number(message: str) -> int | None:
    for pattern in _PR_PATTERNS:
        match = pattern.search(message)
        if match:
            return int(match.group("number"))
    return None


def _changed_paths(root: Path, parent: str, commit: str) -> list[str]:
    raw = bytes(
        _run_git(
            root,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "-z",
            parent,
            commit,
        )
    )
    return [
        item.decode("utf-8", errors="surrogateescape")
        for item in raw.split(b"\0")
        if item
    ]


def _patch(root: Path, parent: str, commit: str, path: str) -> bytes:
    return bytes(
        _run_git(
            root,
            "diff",
            "--no-color",
            "--no-ext-diff",
            "--unified=3",
            "--find-renames",
            parent,
            commit,
            "--",
            path,
        )
    )


def _selection_reason(path: str, patch: bytes) -> str | None:
    lower = path.lower()
    if any(lower.startswith(prefix) for prefix in _POLICY_PREFIXES):
        return "POLICY_SURFACE_PATH"
    if _POLICY_PATH_RE.search(path):
        return "POLICY_PATH_TOKEN"
    if Path(path).suffix.lower() in _TEXT_LOGIC_SUFFIXES and _LOGIC_RE.search(patch):
        return "INVARIANT_CONTRACT_ENFORCEMENT_CONTENT"
    return None


def _operation_key(
    *,
    commit: str,
    pr_number: int,
    path: str,
    artifact_sha256: str,
    chunk_index: int,
    chunk_count: int,
) -> str:
    body = {
        "schema": SCHEMA,
        "commit": commit,
        "pr_number": pr_number,
        "path": path,
        "artifact_sha256": artifact_sha256,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
    }
    return sha256(b"HHS-MAIN-HISTORY-OPERATION-KEY-V1\0" + _canonical(body)).hexdigest()


def _expected_vector(
    *,
    operation_key: str,
    logical_step: int,
    frame: bytes,
    artifact: Mapping[str, Any],
    chunk_index: int,
    previous_object_id: str | None,
) -> tuple[str, str, str, Hash216Array]:
    predecessor = hash72_digest(
        {
            "domain": "HHS-MAIN-HISTORY-PREDECESSOR-V1",
            "previous_object_id": previous_object_id or ZERO_SHA256,
        },
        operation_key,
    )
    current = hash72_digest(
        {
            "domain": "HHS-MAIN-HISTORY-CURRENT-V1",
            "artifact_sha256": artifact["artifact_sha256"],
            "chunk_index": chunk_index,
        },
        frame,
    )
    successor = hash72_digest(
        {
            "domain": "HHS-MAIN-HISTORY-SUCCESSOR-V1",
            "commit": artifact["commit"],
            "pr_number": artifact["pr_number"],
            "path": artifact["path"],
            "chunk_index": chunk_index,
        },
        artifact["artifact_sha256"],
    )
    operation_identity = sha256(
        b"HHS-MAIN-HISTORY-OPERATION-IDENTITY-V1\0"
        + bytes.fromhex(operation_key)
        + bytes.fromhex(artifact["artifact_sha256"])
        + frame
    ).hexdigest()
    hash216 = Hash216Array.build(
        predecessor,
        current,
        successor,
        genesis_identity=GENESIS_IDENTITY,
        logical_step=logical_step,
        operation_identity=operation_identity,
        legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
    )
    return current, operation_identity, predecessor, hash216


def _admit_or_reuse(
    store: PersistentEncryptedVectorStore,
    *,
    operation_key: str,
    logical_step: int,
    frame: bytes,
    artifact: Mapping[str, Any],
    chunk_index: int,
    previous_object_id: str | None,
) -> tuple[str, bool]:
    current, operation_identity, predecessor, hash216 = _expected_vector(
        operation_key=operation_key,
        logical_step=logical_step,
        frame=frame,
        artifact=artifact,
        chunk_index=chunk_index,
        previous_object_id=previous_object_id,
    )
    try:
        existing, restored = store.retrieve(
            operation_key,
            legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
            genesis_identity=GENESIS_IDENTITY,
        )
    except Pass174Error as exc:
        if exc.classification != "HHS_P174_VECTOR_MISS":
            raise
    else:
        if restored != frame:
            raise MainHistoryHydrationError("HHS_HISTORY_REUSE_FRAME_MISMATCH")
        if existing.logical_step != logical_step:
            raise MainHistoryHydrationError("HHS_HISTORY_REUSE_LOGICAL_STEP_MISMATCH")
        if existing.operation_identity_sha256 != operation_identity:
            raise MainHistoryHydrationError("HHS_HISTORY_REUSE_OPERATION_IDENTITY_MISMATCH")
        if existing.hash216.logical_identity_sha256 != hash216.logical_identity_sha256:
            raise MainHistoryHydrationError("HHS_HISTORY_REUSE_HASH216_MISMATCH")
        if existing.parent_object_id != previous_object_id:
            raise MainHistoryHydrationError("HHS_HISTORY_REUSE_PARENT_MISMATCH")
        return existing.object_id, True

    admitted = store.admit(
        operation_key=operation_key,
        logical_step=logical_step,
        input_hash72=predecessor,
        output_hash72=current,
        operation_identity_sha256=operation_identity,
        hash216=hash216,
        output_snapshot=frame,
        legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
        genesis_identity=GENESIS_IDENTITY,
        direct_cost_units=max(1, len(decode_frame(frame))),
        changed_bits=sum(byte.bit_count() for byte in frame),
        parent_object_id=previous_object_id,
    )
    return admitted.object_id, False


def verify_manifest(
    store: PersistentEncryptedVectorStore,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    reconstructed = 0
    total_bytes = 0
    previous_object_id: str | None = None
    for artifact in manifest["artifacts"]:
        payload = bytearray()
        for operation_key, expected_object_id in zip(
            artifact["operation_keys"], artifact["object_ids"]
        ):
            obj, frame = store.retrieve(
                operation_key,
                legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
                genesis_identity=GENESIS_IDENTITY,
            )
            if obj.object_id != expected_object_id:
                raise MainHistoryHydrationError("HHS_HISTORY_VERIFY_OBJECT_ID_MISMATCH")
            if obj.parent_object_id != previous_object_id:
                raise MainHistoryHydrationError("HHS_HISTORY_VERIFY_CHAIN_MISMATCH")
            obj.hash216.verify()
            payload.extend(decode_frame(frame))
            previous_object_id = obj.object_id
        actual = bytes(payload)
        if sha256(actual).hexdigest() != artifact["artifact_sha256"]:
            raise MainHistoryHydrationError("HHS_HISTORY_VERIFY_ARTIFACT_HASH_MISMATCH")
        if len(actual) != artifact["bytes"]:
            raise MainHistoryHydrationError("HHS_HISTORY_VERIFY_ARTIFACT_LENGTH_MISMATCH")
        reconstructed += 1
        total_bytes += len(actual)
    return {
        "classification": "HHS_MAIN_HISTORY_HASH216_RECONSTRUCTION_VERIFIED",
        "artifacts_reconstructed": reconstructed,
        "bytes_reconstructed": total_bytes,
        "final_history_object_id": previous_object_id,
    }


def hydrate_main_history(
    *,
    repository_root: str | Path,
    ref: str = "HEAD",
    state_root: str | Path,
    vector_database: str | Path,
    vector_key: str | Path,
    bounds: HydrationBounds | None = None,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    if not (root / ".git").exists():
        raise MainHistoryHydrationError("HHS_HISTORY_GIT_METADATA_REQUIRED")
    resolved_bounds = (bounds or HydrationBounds()).validate()
    resolved_commit = _resolve_commit(root, ref)
    commits = _first_parent_commits(root, resolved_commit, resolved_bounds)

    state = Path(state_root).resolve()
    state.mkdir(parents=True, exist_ok=True)
    manifest_path = state / "manifest.json"

    artifacts: list[dict[str, Any]] = []
    total_logic_bytes = 0
    pr_commit_count = 0
    non_pr_commit_count = 0
    frame_count = 0
    new_frames = 0
    reused_frames = 0
    logical_step = 0
    previous_object_id: str | None = None

    store = PersistentEncryptedVectorStore(
        vector_database,
        key_path=vector_key,
        active_suffix_limit=72,
    )
    try:
        for commit in commits:
            parents = _parents(root, commit)
            message = _message(root, commit)
            pr_number = _pr_number(message)
            if pr_number is None or not parents:
                non_pr_commit_count += 1
                continue
            pr_commit_count += 1
            parent = parents[0]
            for path in _changed_paths(root, parent, commit):
                patch = _patch(root, parent, commit, path)
                reason = _selection_reason(path, patch)
                if reason is None:
                    continue
                if len(patch) > resolved_bounds.max_artifact_bytes:
                    raise MainHistoryHydrationError(
                        f"HHS_HISTORY_ARTIFACT_LIMIT:{commit}:{path}:{len(patch)}"
                    )
                artifact_sha = sha256(patch).hexdigest()
                total_logic_bytes += len(patch)
                if total_logic_bytes > resolved_bounds.max_total_logic_bytes:
                    raise MainHistoryHydrationError(
                        "HHS_HISTORY_TOTAL_LOGIC_BYTES_LIMIT"
                    )
                chunks = list(_chunks(patch))
                if frame_count + len(chunks) > resolved_bounds.max_frames:
                    raise MainHistoryHydrationError("HHS_HISTORY_FRAME_LIMIT")
                artifact = {
                    "commit": commit,
                    "parent": parent,
                    "pr_number": pr_number,
                    "path": path,
                    "selection_reason": reason,
                    "artifact_sha256": artifact_sha,
                    "bytes": len(patch),
                    "chunk_count": len(chunks),
                    "operation_keys": [],
                    "object_ids": [],
                }
                for chunk_index, chunk in enumerate(chunks):
                    logical_step += 1
                    frame = encode_frame(chunk)
                    operation_key = _operation_key(
                        commit=commit,
                        pr_number=pr_number,
                        path=path,
                        artifact_sha256=artifact_sha,
                        chunk_index=chunk_index,
                        chunk_count=len(chunks),
                    )
                    object_id, reused = _admit_or_reuse(
                        store,
                        operation_key=operation_key,
                        logical_step=logical_step,
                        frame=frame,
                        artifact=artifact,
                        chunk_index=chunk_index,
                        previous_object_id=previous_object_id,
                    )
                    previous_object_id = object_id
                    artifact["operation_keys"].append(operation_key)
                    artifact["object_ids"].append(object_id)
                    frame_count += 1
                    if reused:
                        reused_frames += 1
                    else:
                        new_frames += 1
                artifacts.append(artifact)

        manifest: dict[str, Any] = {
            "schema": SCHEMA,
            "source_authority": "GIT_FIRST_PARENT_MAIN_HISTORY",
            "admission_basis": "PR_ATTRIBUTED_COMMIT_REACHABLE_ON_EXACT_FIRST_PARENT_MAIN",
            "historical_ci_status_requeried": False,
            "historical_identity_rewritten": False,
            "canonical_mutation_authority": False,
            "canonical_hash72_commit_authority": False,
            "vector_store_role": "READ_ONLY_HYDRATED_LOGIC_INDEX",
            "repository_root": str(root),
            "requested_ref": ref,
            "resolved_commit": resolved_commit,
            "first_parent_commit_count": len(commits),
            "pr_commit_count": pr_commit_count,
            "non_pr_or_root_commit_count": non_pr_commit_count,
            "artifact_count": len(artifacts),
            "frame_count": frame_count,
            "new_frames": new_frames,
            "reused_frames": reused_frames,
            "exact_logic_bytes": total_logic_bytes,
            "frame_bytes": FRAME_BYTES,
            "frame_payload_bytes": FRAME_PAYLOAD_BYTES,
            "genesis_identity_sha256": GENESIS_IDENTITY,
            "legacy_foundation_root_sha256": LEGACY_FOUNDATION_ROOT,
            "selection_policy": {
                "policy_prefixes": list(_POLICY_PREFIXES),
                "path_token_regex": _POLICY_PATH_RE.pattern,
                "content_regex": _LOGIC_RE.pattern.decode("ascii"),
                "whole_selected_unified_diff_preserved": True,
            },
            "artifacts": artifacts,
            "store": store.storage_status(),
        }
        manifest["verification"] = verify_manifest(store, manifest)
        unsigned = _canonical(manifest)
        manifest["manifest_sha256"] = sha256(
            b"HHS-MAIN-HISTORY-MANIFEST-V1\0" + unsigned
        ).hexdigest()
        manifest["manifest_hash216"] = _hash216(
            "HHS-MAIN-HISTORY-MANIFEST-V1", manifest
        )
        encoded = json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8") + b"\n"
        if len(encoded) > resolved_bounds.max_manifest_bytes:
            raise MainHistoryHydrationError("HHS_HISTORY_MANIFEST_SIZE_LIMIT")
        temporary = manifest_path.with_suffix(".json.tmp")
        with temporary.open("wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, manifest_path)
        directory_fd = os.open(state, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return {
            "classification": "HHS_MAIN_HISTORY_GREEN_PR_HASH216_HYDRATED",
            "resolved_commit": resolved_commit,
            "manifest_path": str(manifest_path),
            "manifest_sha256": manifest["manifest_sha256"],
            "manifest_hash216": manifest["manifest_hash216"],
            "artifact_count": len(artifacts),
            "frame_count": frame_count,
            "new_frames": new_frames,
            "reused_frames": reused_frames,
            "exact_logic_bytes": total_logic_bytes,
            "store_root_sha256": manifest["store"]["logical_root_sha256"],
            "verification": manifest["verification"],
        }
    finally:
        store.close()
