"""Pass 220 model-weight hydration into the unified Lane 5 graph.

Weight bytes are analyzed through the inherited Pass 165 5,184-bit projection
and Hash216 lineage but are never committed as learning epochs. This keeps
native open-model and Hugging Face weights available to the same knowledge
graph without promoting external floating-point parameters into VM81 authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
from typing import Any, Iterator, Mapping, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import canonical_bytes, hash216
from hhs_runtime.hhs_pass220_lane5_unified_corpus_v1 import (
    Lane5UnifiedCorpus,
    RAW_CHUNK_BYTES,
    UnifiedCorpusError,
    file_sha256,
)

WEIGHT_MANIFEST_SCHEMA = "HHS_PASS220_LANE5_UNIFIED_MODEL_WEIGHT_MANIFEST_V1"
WEIGHT_SUFFIXES = (
    ".safetensors",
    ".bin",
    ".pt",
    ".pth",
    ".onnx",
    ".gguf",
    ".ggml",
    ".litertlm",
)


def _validate_revision(value: str, label: str) -> str:
    value = str(value).strip().lower()
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise UnifiedCorpusError(f"PASS220_IMMUTABLE_REVISION_REQUIRED:{label}")
    return value


def _validate_sha(value: str, label: str) -> str:
    value = str(value).strip().lower()
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise UnifiedCorpusError(f"PASS220_WEIGHT_SHA256_INVALID:{label}")
    return value


def _safe_tensor_metadata(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() != ".safetensors":
        return []
    with path.open("rb") as handle:
        raw = handle.read(8)
        if len(raw) != 8:
            raise UnifiedCorpusError(f"PASS220_SAFETENSORS_HEADER_TRUNCATED:{path.name}")
        header_length = int.from_bytes(raw, "little")
        if header_length <= 0 or header_length > 128 * 1024 * 1024:
            raise UnifiedCorpusError(f"PASS220_SAFETENSORS_HEADER_BOUND:{path.name}")
        header = handle.read(header_length)
        if len(header) != header_length:
            raise UnifiedCorpusError(f"PASS220_SAFETENSORS_HEADER_TRUNCATED:{path.name}")
    try:
        metadata = json.loads(header)
    except json.JSONDecodeError as exc:
        raise UnifiedCorpusError(f"PASS220_SAFETENSORS_HEADER_INVALID:{path.name}") from exc
    if not isinstance(metadata, dict):
        raise UnifiedCorpusError(f"PASS220_SAFETENSORS_HEADER_INVALID:{path.name}")
    tensors: list[dict[str, Any]] = []
    for name in sorted(metadata):
        if name == "__metadata__":
            continue
        item = metadata[name]
        if not isinstance(item, dict):
            raise UnifiedCorpusError(f"PASS220_SAFETENSORS_TENSOR_INVALID:{name}")
        tensors.append({
            "name": name,
            "dtype": item.get("dtype"),
            "shape": item.get("shape"),
            "data_offsets": item.get("data_offsets"),
        })
    return tensors


def _chunks(path: Path) -> Iterator[tuple[int, int, bytes]]:
    offset = 0
    index = 0
    with path.open("rb") as handle:
        while True:
            raw = handle.read(RAW_CHUNK_BYTES)
            if not raw:
                break
            yield index, offset, raw
            offset += len(raw)
            index += 1


def _download_snapshot(
    repo_id: str,
    revision: str,
    *,
    allow_patterns: Sequence[str],
    cache_dir: Path | None,
) -> Path:
    revision = _validate_revision(revision, repo_id)
    try:
        from huggingface_hub import snapshot_download
    except Exception as exc:
        raise UnifiedCorpusError("PASS220_HUGGINGFACE_HUB_REQUIRED") from exc
    resolved = snapshot_download(
        repo_id=repo_id,
        revision=revision,
        allow_patterns=list(allow_patterns),
        cache_dir=str(cache_dir) if cache_dir else None,
    )
    return Path(resolved)


def _download_file(
    repo_id: str,
    revision: str,
    filename: str,
    *,
    cache_dir: Path | None,
) -> Path:
    revision = _validate_revision(revision, repo_id)
    try:
        from huggingface_hub import hf_hub_download
    except Exception as exc:
        raise UnifiedCorpusError("PASS220_HUGGINGFACE_HUB_REQUIRED") from exc
    resolved = hf_hub_download(
        repo_id=repo_id,
        revision=revision,
        filename=filename,
        cache_dir=str(cache_dir) if cache_dir else None,
    )
    return Path(resolved)


class UnifiedModelWeightHydrator:
    def __init__(self, corpus: Lane5UnifiedCorpus) -> None:
        self.corpus = corpus

    def process_file(
        self,
        path: Path,
        *,
        model_id: str,
        source_kind: str,
        corpus_root: str,
        provenance: Mapping[str, Any],
        expected_sha256: str | None = None,
        expected_size_bytes: int | None = None,
    ) -> str:
        path = Path(path)
        if not path.is_file():
            raise UnifiedCorpusError(f"PASS220_WEIGHT_FILE_MISSING:{path}")
        size = path.stat().st_size
        if expected_size_bytes is not None and size != int(expected_size_bytes):
            raise UnifiedCorpusError(f"PASS220_WEIGHT_SIZE_MISMATCH:{model_id}:{path.name}")
        digest = file_sha256(path)
        if expected_sha256 is not None and digest != _validate_sha(expected_sha256, model_id):
            raise UnifiedCorpusError(f"PASS220_WEIGHT_SHA256_MISMATCH:{model_id}:{path.name}")

        weight_node = self.corpus.graph.add_node(
            "MODEL_WEIGHT_FILE",
            {
                "model_id": model_id,
                "source_kind": source_kind,
                "filename": path.name,
                "size_bytes": size,
                "sha256": digest,
                "provenance": dict(provenance),
                "weight_bytes_are_data_not_execution_authority": True,
                "candidate_only": True,
            },
        )
        self.corpus.graph.add_edge(corpus_root, weight_node, "CONTAINS_MODEL_WEIGHT_FILE")

        for tensor in _safe_tensor_metadata(path):
            tensor_node = self.corpus.graph.add_node(
                "MODEL_TENSOR_METADATA",
                {
                    "model_id": model_id,
                    "weight_file_sha256": digest,
                    **tensor,
                    "values_not_scalarized_by_metadata_parser": True,
                    "candidate_only": True,
                },
            )
            self.corpus.graph.add_edge(weight_node, tensor_node, "DECLARES_TENSOR")

        for chunk_index, offset, raw in _chunks(path):
            chunk_sha = sha256(raw).hexdigest()
            key = f"model-weight:{model_id}:{digest}:{chunk_index}:{offset}:{chunk_sha}"
            if key in self.corpus.graph.completed:
                continue
            node = self.corpus.candidate(
                raw,
                "BINARY_OBJECT",
                (
                    f"pass220:model-weight:{model_id}:{path.name}:sha256:{digest}:"
                    f"chunk:{chunk_index}:offset:{offset}"
                ),
                "MODEL_WEIGHT_HYDRATION_CANDIDATE",
                {
                    "model_id": model_id,
                    "weight_file_sha256": digest,
                    "chunk_index": chunk_index,
                    "byte_offset": offset,
                    "byte_length": len(raw),
                    "source_kind": source_kind,
                    "candidate_only": True,
                },
            )
            self.corpus.graph.add_edge(weight_node, node, "HAS_5184_WEIGHT_HYDRATION_CANDIDATE")
            self.corpus.graph.complete(
                key,
                {"model_id": model_id, "file": path.name, "chunk": chunk_index},
            )
        return weight_node

    def run_manifest(
        self,
        manifest_path: Path,
        *,
        corpus_root: str,
        hf_cache_dir: Path | None = None,
        native_model_path: Path | None = None,
        download_hf: bool = True,
    ) -> dict[str, Any]:
        manifest = json.loads(Path(manifest_path).read_text("utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema") != WEIGHT_MANIFEST_SCHEMA:
            raise UnifiedCorpusError("PASS220_WEIGHT_MANIFEST_SCHEMA_INVALID")
        nodes: list[str] = []

        for spec in manifest.get("native_open_models", []):
            if not isinstance(spec, Mapping):
                raise UnifiedCorpusError("PASS220_NATIVE_WEIGHT_SPEC_INVALID")
            model_id = str(spec.get("model_id") or "").strip()
            if not model_id:
                raise UnifiedCorpusError("PASS220_NATIVE_MODEL_ID_REQUIRED")
            path = native_model_path
            env_name = str(spec.get("local_path_env") or "").strip()
            if path is None and env_name and os.environ.get(env_name):
                path = Path(os.environ[env_name])
            fallback = spec.get("hugging_face_fallback")
            if path is None:
                if not download_hf or not isinstance(fallback, Mapping):
                    raise UnifiedCorpusError(f"PASS220_NATIVE_MODEL_WEIGHT_UNAVAILABLE:{model_id}")
                repo_id = str(fallback.get("repo_id") or "").strip()
                revision = str(fallback.get("revision") or "")
                filename = str(fallback.get("filename") or "").strip()
                if not repo_id or not filename:
                    raise UnifiedCorpusError("PASS220_NATIVE_HF_FALLBACK_INVALID")
                path = _download_file(
                    repo_id,
                    revision,
                    filename,
                    cache_dir=hf_cache_dir,
                )
            nodes.append(
                self.process_file(
                    path,
                    model_id=model_id,
                    source_kind="NATIVE_OPEN_MODEL",
                    corpus_root=corpus_root,
                    provenance={
                        "deployment_alias": spec.get("deployment_alias"),
                        "local_path_env": env_name or None,
                        "hugging_face_fallback": fallback,
                    },
                    expected_sha256=spec.get("expected_sha256"),
                    expected_size_bytes=spec.get("expected_size_bytes"),
                )
            )

        for spec in manifest.get("hugging_face_models", []):
            if not isinstance(spec, Mapping):
                raise UnifiedCorpusError("PASS220_HF_WEIGHT_SPEC_INVALID")
            model_id = str(spec.get("model_id") or "").strip()
            repo_id = str(spec.get("repo_id") or "").strip()
            revision = str(spec.get("revision") or "")
            patterns = tuple(str(x) for x in spec.get("allow_patterns", []) if str(x))
            if not model_id or not repo_id or not patterns:
                raise UnifiedCorpusError("PASS220_HF_WEIGHT_SPEC_INVALID")
            if not download_hf:
                raise UnifiedCorpusError(f"PASS220_HF_DOWNLOAD_REQUIRED:{model_id}")
            snapshot = _download_snapshot(
                repo_id,
                revision,
                allow_patterns=patterns,
                cache_dir=hf_cache_dir,
            )
            files = sorted(
                path
                for path in snapshot.rglob("*")
                if path.is_file() and path.suffix.lower() in WEIGHT_SUFFIXES
            )
            if not files:
                raise UnifiedCorpusError(f"PASS220_HF_WEIGHT_FILES_EMPTY:{model_id}")
            for path in files:
                resolved_snapshot = snapshot.resolve()
                resolved_path = path.resolve()
                try:
                    relative = resolved_path.relative_to(resolved_snapshot).as_posix()
                except ValueError as exc:
                    raise UnifiedCorpusError("PASS220_HF_WEIGHT_PATH_ESCAPE") from exc
                nodes.append(
                    self.process_file(
                        path,
                        model_id=model_id,
                        source_kind="HUGGING_FACE_MODEL",
                        corpus_root=corpus_root,
                        provenance={
                            "provider": "HUGGING_FACE",
                            "repo_id": repo_id,
                            "revision": _validate_revision(revision, model_id),
                            "relative_path": relative,
                            "license_id": spec.get("license_id"),
                        },
                    )
                )

        receipt = {
            "schema": "HHS_PASS220_LANE5_MODEL_WEIGHT_HYDRATION_RECEIPT_V1",
            "manifest_hash216": hash216(
                "pass220-weight-manifest",
                canonical_bytes(manifest),
            ),
            "model_weight_nodes": nodes,
            "model_weight_node_count": len(nodes),
            "graph_root_hash216": self.corpus.graph.root_hash216(),
            "weights_candidate_only": True,
            "canonical_learning_commit_invoked": False,
            "canonical_authority_widened": False,
        }
        receipt["receipt_hash216"] = hash216(
            "pass220-model-weight-receipt",
            canonical_bytes(receipt),
        )
        return receipt
