from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping

from .core import NFVError, NFVObject, TransitionPackage, hash72, hash216


@dataclass(frozen=True)
class ObjectRef:
    lineage_id: str
    object_index: str
    version: int
    generation: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "object_index": self.object_index,
            "version": self.version,
            "generation": self.generation,
        }


@dataclass(frozen=True)
class ReplayResult:
    final_object: NFVObject
    receipt_chain: tuple[str, ...]
    replay_hash72: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "final_object": self.final_object.to_dict(),
            "receipt_chain": list(self.receipt_chain),
            "replay_hash72": self.replay_hash72,
        }


class NFVStore:
    def __init__(self, *, max_lineages: int = 1024, max_versions_per_lineage: int = 4096) -> None:
        if max_lineages <= 0 or max_versions_per_lineage <= 0:
            raise NFVError("NFV_INVALID_STORE_BOUND", "store bounds must be positive")
        self.max_lineages = int(max_lineages)
        self.max_versions_per_lineage = int(max_versions_per_lineage)
        self._versions: dict[str, dict[tuple[int, int], NFVObject]] = {}
        self._heads: dict[str, ObjectRef] = {}

    def create(self, obj: NFVObject, *, lineage_id: str | None = None) -> ObjectRef:
        if obj.lifecycle != "COMMITTED":
            raise NFVError("NFV_UNCOMMITTED_OBJECT", "only committed objects may enter the authoritative store")
        lineage = lineage_id or hash216({
            "domain": "HHS-NFV-LINEAGE-V1",
            "creation_index": obj.object_index,
            "authority_root": obj.authority_root,
            "object_type": obj.object_type,
        })
        if lineage in self._versions:
            raise NFVError("NFV_LINEAGE_ALREADY_EXISTS", "lineage is already registered")
        if len(self._versions) >= self.max_lineages:
            raise NFVError("RESOURCE_BOUNDED", "maximum lineage count reached")
        ref = ObjectRef(lineage, obj.object_index, obj.version, obj.generation)
        self._versions[lineage] = {(obj.version, obj.generation): obj}
        self._heads[lineage] = ref
        return ref

    def head(self, lineage_id: str) -> ObjectRef:
        try:
            return self._heads[lineage_id]
        except KeyError as exc:
            raise NFVError("NFV_UNKNOWN_LINEAGE", "object lineage is not registered") from exc

    def open(self, ref: ObjectRef, *, historical: bool = False) -> NFVObject:
        if ref.lineage_id not in self._versions:
            raise NFVError("NFV_UNKNOWN_LINEAGE", "object lineage is not registered")
        if not historical and self._heads[ref.lineage_id] != ref:
            raise NFVError("NFV_STALE_OBJECT_REFERENCE", "object version or generation is stale")
        try:
            obj = self._versions[ref.lineage_id][(ref.version, ref.generation)]
        except KeyError as exc:
            raise NFVError("NFV_UNKNOWN_OBJECT_VERSION", "object version and generation are unavailable") from exc
        if obj.object_index != ref.object_index:
            raise NFVError("NFV_OBJECT_REFERENCE_MISMATCH", "object index does not match stored version")
        return obj

    def commit(
        self,
        ref: ObjectRef,
        package: TransitionPackage,
        *,
        vm81_admit: Callable[[NFVObject, Mapping[str, Any]], bool],
        copy_on_write: bool = False,
    ) -> tuple[ObjectRef, NFVObject, TransitionPackage]:
        current = self.open(ref)
        committed, closed = package.commit(current, vm81_admit=vm81_admit)
        generation = current.generation + 1 if copy_on_write else current.generation
        if generation != committed.generation:
            committed = NFVObject(
                object_type=committed.object_type,
                state=committed.state,
                constraints=committed.constraints,
                dependencies=committed.dependencies,
                authority_root=committed.authority_root,
                version=committed.version,
                generation=generation,
                receipt_head=committed.receipt_head,
                lifecycle=committed.lifecycle,
            )
        versions = self._versions[ref.lineage_id]
        if len(versions) >= self.max_versions_per_lineage:
            raise NFVError("RESOURCE_BOUNDED", "maximum versions per lineage reached")
        key = (committed.version, committed.generation)
        if key in versions:
            raise NFVError("NFV_VERSION_GENERATION_CONFLICT", "version and generation already exist")
        new_ref = ObjectRef(ref.lineage_id, committed.object_index, committed.version, committed.generation)
        versions[key] = committed
        self._heads[ref.lineage_id] = new_ref
        return new_ref, committed, closed

    def history(self, lineage_id: str) -> tuple[ObjectRef, ...]:
        if lineage_id not in self._versions:
            raise NFVError("NFV_UNKNOWN_LINEAGE", "object lineage is not registered")
        return tuple(
            ObjectRef(lineage_id, obj.object_index, version, generation)
            for (version, generation), obj in sorted(self._versions[lineage_id].items())
        )

    def manifest(self) -> dict[str, Any]:
        lineages = []
        for lineage_id in sorted(self._versions):
            head = self._heads[lineage_id]
            lineages.append({
                "lineage_id": lineage_id,
                "head": head.to_dict(),
                "versions": [ref.to_dict() for ref in self.history(lineage_id)],
            })
        return {
            "schema": "HHS_NFV_OBJECT_STORE_V1",
            "max_lineages": self.max_lineages,
            "max_versions_per_lineage": self.max_versions_per_lineage,
            "lineages": lineages,
            "manifest_hash216": hash216({"domain": "HHS-NFV-STORE-MANIFEST-V1", "lineages": lineages}),
        }


def replay_packages(
    initial: NFVObject,
    packages: Iterable[TransitionPackage],
    *,
    vm81_admit: Callable[[NFVObject, Mapping[str, Any]], bool],
) -> ReplayResult:
    current = initial
    receipts: list[str] = []
    for package in packages:
        current, closed = package.commit(current, vm81_admit=vm81_admit)
        receipts.append(closed.receipt)
    replay_hash = hash72({
        "domain": "HHS-NFV-REPLAY-V1",
        "initial": initial.to_dict(),
        "final": current.to_dict(),
        "receipts": receipts,
    })
    return ReplayResult(current, tuple(receipts), replay_hash)
