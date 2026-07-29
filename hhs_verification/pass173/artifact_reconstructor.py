from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import hashlib
import json

from hhs_installer.canonical import installation_identity, hash216, stable


@dataclass(frozen=True)
class ArtifactDigest:
    relative_path: str
    size: int
    sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def file_digest(path: str | Path, *, relative_to: str | Path | None = None) -> ArtifactDigest:
    target = Path(path)
    digest = hashlib.sha256()
    size = 0
    with target.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            size += len(block)
    relative = target.name if relative_to is None else str(target.resolve().relative_to(Path(relative_to).resolve())).replace("\\", "/")
    return ArtifactDigest(relative, size, digest.hexdigest())


def tree_manifest(root: str | Path, *, excluded_parts: Iterable[str] = (".git", "__pycache__", ".pytest_cache")) -> tuple[ArtifactDigest, ...]:
    base = Path(root).resolve()
    excluded = set(excluded_parts)
    records: list[ArtifactDigest] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or excluded.intersection(path.parts):
            continue
        records.append(file_digest(path, relative_to=base))
    return tuple(records)


class ArtifactReconstructor:
    @staticmethod
    def source_identity(root: str | Path, *, declared_manifest: str | Path | None = None) -> dict[str, Any]:
        records = tree_manifest(root)
        observed = [item.to_dict() for item in records]
        observed_identity = hash216(observed, domain="HHS-P173-SOURCE-TREE-MANIFEST-V1")
        result: dict[str, Any] = {
            "observed_identity": observed_identity,
            "file_count": len(records),
            "records": observed,
            "declared_match": None,
        }
        if declared_manifest:
            payload = json.loads(Path(declared_manifest).read_text(encoding="utf-8"))
            declared_records = payload.get("files", payload.get("records", []))
            declared_identity = hash216(declared_records, domain="HHS-P173-SOURCE-TREE-MANIFEST-V1")
            result["declared_identity"] = declared_identity
            result["declared_match"] = declared_identity == observed_identity
        return result

    @staticmethod
    def reconstruct_installation_identity(components: Mapping[str, Any]) -> str:
        return installation_identity(components)

    @staticmethod
    def compare_installation_identity(components: Mapping[str, Any], claimed_identity: str) -> dict[str, Any]:
        reconstructed = installation_identity(components)
        return {
            "claimed_identity": claimed_identity,
            "reconstructed_identity": reconstructed,
            "matches": reconstructed == claimed_identity,
            "classification": "P173_HASH216_INSTALLATION_IDENTITY_RECONSTRUCTED" if reconstructed == claimed_identity else "P173_HASH216_INSTALLATION_IDENTITY_MISMATCH",
        }

    @staticmethod
    def native_surface(symbols: Iterable[str], *, platform: str, architecture: str, artifact_digest: ArtifactDigest) -> dict[str, Any]:
        normalized_symbols = sorted(set(str(symbol) for symbol in symbols))
        payload = {
            "platform": platform,
            "architecture": architecture,
            "artifact": artifact_digest.to_dict(),
            "symbols": normalized_symbols,
        }
        payload["surface_identity"] = hash216(payload, domain="HHS-P173-NATIVE-ABI-SURFACE-V1")
        return stable(payload)
