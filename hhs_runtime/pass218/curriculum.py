"""Pass 218 Iteration 1 deterministic curriculum manifest and restart cursor."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72


class CurriculumStage(IntEnum):
    GENESIS = 0
    REFERENCE = 1
    EXPOSITORY = 2
    SIMPLE_NARRATIVE = 3
    COMPLEX_SOCIAL_NARRATIVE = 4
    MYTHOPOETIC = 5
    CREATIVE_SYNTHESIS = 6


class Pass218CurriculumOrderError(RuntimeError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class CurriculumSource:
    source_id: str
    stage: CurriculumStage
    locator: str
    checksum_sha256: str
    rights_class: str
    source_authority: str
    media_type: str = "application/octet-stream"

    def record(self) -> dict[str, Any]:
        if len(self.checksum_sha256) != 64 or any(ch not in "0123456789abcdef" for ch in self.checksum_sha256):
            raise ValueError("P218_CURRICULUM_CHECKSUM_INVALID")
        return {
            "source_id": self.source_id,
            "stage": int(self.stage),
            "stage_name": self.stage.name,
            "locator": self.locator,
            "checksum_sha256": self.checksum_sha256,
            "rights_class": self.rights_class,
            "source_authority": self.source_authority,
            "media_type": self.media_type,
        }


@dataclass(frozen=True)
class CurriculumManifest:
    genesis_seed_hash72: str
    sources: tuple[Mapping[str, Any], ...]
    manifest_hash72: str
    curriculum_identity_hash72: str

    def record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-CURRICULUM-MANIFEST-I1-V1",
            "genesis_seed_hash72": self.genesis_seed_hash72,
            "sources": [dict(item) for item in self.sources],
            "manifest_hash72": self.manifest_hash72,
            "curriculum_identity_hash72": self.curriculum_identity_hash72,
        }

    def source_at(self, index: int) -> Mapping[str, Any]:
        return self.sources[index]


def build_curriculum_manifest(
    genesis_seed_hash72: str,
    sources: Iterable[CurriculumSource],
    *,
    compiler_version: str = "HHS-P218-CURRICULUM-I1-V1",
) -> CurriculumManifest:
    if not validate_hash72(genesis_seed_hash72):
        raise ValueError("P218_GENESIS_HASH72_INVALID")
    records = [source.record() for source in sources]
    records.sort(key=lambda item: (item["stage"], item["locator"], item["source_id"]))
    for ordinal, record in enumerate(records):
        record["ordinal"] = ordinal
    manifest_payload = {
        "schema": "HHS-P218-CURRICULUM-MANIFEST-I1-V1",
        "compiler_version": compiler_version,
        "genesis_seed_hash72": genesis_seed_hash72,
        "sources": records,
        "random_shuffle_authoritative": False,
    }
    manifest_hash72 = hash72_digest(
        {"domain": "HHS-P218-CURRICULUM-MANIFEST-I1-V1"}, manifest_payload
    )
    curriculum_identity = hash72_digest(
        {"domain": "HHS-P218-CURRICULUM-IDENTITY-I1-V1"},
        {
            "genesis_seed_hash72": genesis_seed_hash72,
            "manifest_hash72": manifest_hash72,
            "ordered_source_checksums": [item["checksum_sha256"] for item in records],
            "compiler_version": compiler_version,
        },
    )
    return CurriculumManifest(
        genesis_seed_hash72=genesis_seed_hash72,
        sources=tuple(records),
        manifest_hash72=manifest_hash72,
        curriculum_identity_hash72=curriculum_identity,
    )


@dataclass(frozen=True)
class CurriculumCursor:
    manifest_hash72: str
    curriculum_identity_hash72: str
    next_ordinal: int = 0
    last_closure_hash72: str | None = None

    def expected_source(self, manifest: CurriculumManifest) -> Mapping[str, Any] | None:
        self._validate_manifest(manifest)
        if self.next_ordinal >= len(manifest.sources):
            return None
        return manifest.sources[self.next_ordinal]

    def advance(
        self,
        manifest: CurriculumManifest,
        *,
        source_id: str,
        closure_hash72: str,
    ) -> tuple["CurriculumCursor", dict[str, Any]]:
        self._validate_manifest(manifest)
        if not validate_hash72(closure_hash72):
            raise ValueError("P218_SOURCE_CLOSURE_HASH72_INVALID")
        expected = self.expected_source(manifest)
        if expected is None:
            raise Pass218CurriculumOrderError("P218_CURRICULUM_ALREADY_COMPLETE")
        if source_id != expected["source_id"]:
            raise Pass218CurriculumOrderError("P218_OUT_OF_ORDER_AUTHORITATIVE_PROMOTION")
        transition = {
            "schema": "HHS-P218-CURRICULUM-ADVANCE-I1-V1",
            "manifest_hash72": manifest.manifest_hash72,
            "curriculum_identity_hash72": manifest.curriculum_identity_hash72,
            "ordinal": self.next_ordinal,
            "source_id": source_id,
            "source_stage": expected["stage"],
            "source_checksum_sha256": expected["checksum_sha256"],
            "previous_closure_hash72": self.last_closure_hash72,
            "source_closure_hash72": closure_hash72,
        }
        transition_hash72 = hash72_digest(
            {"domain": "HHS-P218-CURRICULUM-ADVANCE-I1-V1"}, transition
        )
        next_cursor = CurriculumCursor(
            manifest_hash72=self.manifest_hash72,
            curriculum_identity_hash72=self.curriculum_identity_hash72,
            next_ordinal=self.next_ordinal + 1,
            last_closure_hash72=closure_hash72,
        )
        receipt = {
            **transition,
            "transition_hash72": transition_hash72,
            "cursor_state_sha256": sha256(_canonical_bytes(next_cursor.record())).hexdigest(),
        }
        return next_cursor, receipt

    def record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-CURRICULUM-CURSOR-I1-V1",
            "manifest_hash72": self.manifest_hash72,
            "curriculum_identity_hash72": self.curriculum_identity_hash72,
            "next_ordinal": self.next_ordinal,
            "last_closure_hash72": self.last_closure_hash72,
        }

    @classmethod
    def for_manifest(cls, manifest: CurriculumManifest) -> "CurriculumCursor":
        return cls(
            manifest_hash72=manifest.manifest_hash72,
            curriculum_identity_hash72=manifest.curriculum_identity_hash72,
        )

    @classmethod
    def restore(cls, payload: Mapping[str, Any]) -> "CurriculumCursor":
        if payload.get("schema") != "HHS-P218-CURRICULUM-CURSOR-I1-V1":
            raise ValueError("P218_CURSOR_SCHEMA_INVALID")
        cursor = cls(
            manifest_hash72=str(payload["manifest_hash72"]),
            curriculum_identity_hash72=str(payload["curriculum_identity_hash72"]),
            next_ordinal=int(payload["next_ordinal"]),
            last_closure_hash72=(
                None if payload.get("last_closure_hash72") is None else str(payload["last_closure_hash72"])
            ),
        )
        if cursor.next_ordinal < 0:
            raise ValueError("P218_CURSOR_ORDINAL_INVALID")
        if not validate_hash72(cursor.manifest_hash72) or not validate_hash72(cursor.curriculum_identity_hash72):
            raise ValueError("P218_CURSOR_HASH72_INVALID")
        if cursor.last_closure_hash72 is not None and not validate_hash72(cursor.last_closure_hash72):
            raise ValueError("P218_CURSOR_CLOSURE_HASH72_INVALID")
        return cursor

    def _validate_manifest(self, manifest: CurriculumManifest) -> None:
        if self.manifest_hash72 != manifest.manifest_hash72:
            raise Pass218CurriculumOrderError("P218_CURSOR_MANIFEST_MISMATCH")
        if self.curriculum_identity_hash72 != manifest.curriculum_identity_hash72:
            raise Pass218CurriculumOrderError("P218_CURSOR_IDENTITY_MISMATCH")
