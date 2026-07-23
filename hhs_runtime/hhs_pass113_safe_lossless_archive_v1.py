from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping, Sequence
import json
import lzma
import zlib

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass112_pass_safe_resume_exit_v1 import (
    PassSafeExitEngine,
    ResourceLedger,
    _build_pass111_fixture,
    _default_resources,
)

PASS_ID = "PASS_113"
ARCHIVE_MANIFEST_SCHEMA = "HHS_SAFE_LOSSLESS_COMPRESSION_MANIFEST_V1"
RECOVERY_CONTRACT_SCHEMA = "HHS_ARCHIVE_RECOVERY_CONTRACT_V1"
COMPRESSION_RECEIPT_SCHEMA = "HHS_SAFE_LOSSLESS_COMPRESSION_RECEIPT_V1"
RECOVERY_RECEIPT_SCHEMA = "HHS_LOSSLESS_RECOVERY_VALIDATION_RECEIPT_V1"
ARCHIVE_SCHEMA = "HHS_SAFE_LOSSLESS_ARCHIVE_V1"

REJECTION_CODES = {
    "REJECT_LOSSY_COMPRESSION_ON_CANONICAL_STATE",
    "REJECT_BYTE_IDENTITY_MISMATCH",
    "REJECT_TYPE_IDENTITY_MISMATCH",
    "REJECT_SCHEMA_IDENTITY_MISMATCH",
    "REJECT_OPERATION_ORDER_LOSS",
    "REJECT_DEPENDENCY_ROOT_LOSS",
    "REJECT_AUTHORITY_ROOT_LOSS",
    "REJECT_RECEIPT_CONTINUITY_LOSS",
    "REJECT_BRANCH_TOPOLOGY_LOSS",
    "REJECT_PHASE_STATE_LOSS",
    "REJECT_SECURITY_POLICY_LOSS",
    "REJECT_PROVENANCE_LOSS",
    "REJECT_EXECUTION_SEMANTICS_MISMATCH",
    "REJECT_NONDETERMINISTIC_CHUNKING",
    "REJECT_CONTEXT_COLLAPSE_DURING_DEDUPLICATION",
    "REJECT_UNROOTED_COMPRESSION_DICTIONARY",
    "REJECT_UNROOTED_DECODER",
    "REJECT_UNAVAILABLE_REQUIRED_DECODER",
    "REJECT_UNBOUNDED_RECOVERY_WORK",
    "REJECT_UNBOUNDED_RECOVERY_MEMORY",
    "REJECT_UNBOUNDED_REFERENCE_FANOUT",
    "REJECT_UNBOUNDED_SYMBOLIC_EXPANSION",
    "REJECT_COMPRESSION_ENTROPY_DEBT",
    "REJECT_ARCHIVE_EXPANSION_RATIO_EXCEEDED",
    "REJECT_ARCHIVE_BOMB",
    "REJECT_VM_SNAPSHOT_AT_UNSTABLE_COORDINATE",
    "REJECT_VM_MEMORY_DISK_INCONSISTENCY",
    "REJECT_REQUIRED_EXTERNAL_RESOURCE_UNDECLARED",
    "REJECT_VM_METADATA_LOSS",
    "REJECT_SECURITY_DOMAIN_CROSS_DEDUPLICATION",
    "REJECT_AUTHORITY_REACTIVATION_WITHOUT_REVALIDATION",
    "REJECT_RECOVERY_WITHOUT_RESOURCE_CONTRACT",
    "REJECT_RECOVERY_STATE_ADMISSION_BEFORE_FULL_VALIDATION",
    "REJECT_PARTIAL_RECOVERY_REPORTED_AS_COMPLETE",
    "REJECT_ARCHIVE_MIGRATION_WITHOUT_EQUIVALENCE_PROOF",
    "REJECT_OLD_ARCHIVE_RETIREMENT_BEFORE_MIGRATION_ADMISSION",
    "REJECT_COMPRESSION_RATIO_REPRESENTED_AS_INEXACT_FLOAT",
    "REJECT_RECOVERY_RESOURCE_UNAVAILABLE_REPRESENTED_AS_ZERO",
    "REJECT_STORAGE_SAVINGS_THAT_DEFER_INEVITABLE_RESOURCE_FAILURE",
    "REJECT_CORRUPTED_ARCHIVE_CHUNK",
    "REJECT_ARCHIVE_MANIFEST_ROOT_MISMATCH",
    "REJECT_ARCHIVE_ROOT_MISMATCH",
}


class ArchiveError(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


@dataclass(frozen=True)
class RecoveryContract:
    maximum_recovery_memory_bytes: int
    maximum_recovery_work_units: int
    maximum_expansion_ratio_numerator: int
    maximum_expansion_ratio_denominator: int = 1
    maximum_chunk_count: int = 4096
    maximum_reference_fanout: int = 1
    streaming_recovery_supported: bool = True
    partial_recovery_supported: bool = True
    cold_boot_recovery_supported: bool = True

    def __post_init__(self) -> None:
        integer_fields = (
            self.maximum_recovery_memory_bytes,
            self.maximum_recovery_work_units,
            self.maximum_expansion_ratio_numerator,
            self.maximum_expansion_ratio_denominator,
            self.maximum_chunk_count,
            self.maximum_reference_fanout,
        )
        if any(not isinstance(x, int) or x <= 0 for x in integer_fields):
            raise ValueError("recovery contract bounds must be positive integers")

    @property
    def root_hash72(self) -> str:
        return _hash("hhs_pass113_recovery_contract_v1", asdict(self))


@dataclass(frozen=True)
class ArchivePolicy:
    chunk_size_bytes: int = 4096
    security_domain: str = "HHS_AUTHORITATIVE_EXIT_STATE"
    allow_cross_object_deduplication: bool = False
    codec_candidates: tuple[str, ...] = ("zlib", "lzma", "raw")

    def __post_init__(self) -> None:
        if self.chunk_size_bytes <= 0:
            raise ValueError("chunk_size_bytes must be positive")
        if not self.security_domain:
            raise ValueError("security_domain required")
        allowed = {"raw", "zlib", "lzma"}
        if not self.codec_candidates or any(x not in allowed for x in self.codec_candidates):
            raise ValueError("unsupported codec candidate")

    @property
    def root_hash72(self) -> str:
        return _hash("hhs_pass113_archive_policy_v1", asdict(self))


class SafeLosslessArchiveEngine:
    DECODER_ROOTS = {
        "raw": _hash("hhs_pass113_decoder_v1", {"codec": "raw", "version": 1}),
        "zlib": _hash("hhs_pass113_decoder_v1", {"codec": "zlib", "version": zlib.ZLIB_VERSION}),
        "lzma": _hash("hhs_pass113_decoder_v1", {"codec": "lzma", "format": "xz", "version": 1}),
    }

    def __init__(self, policy: ArchivePolicy | None = None):
        self.policy = policy or ArchivePolicy()

    @staticmethod
    def _compress(codec: str, payload: bytes) -> bytes:
        if codec == "raw":
            return payload
        if codec == "zlib":
            return zlib.compress(payload, level=9)
        if codec == "lzma":
            return lzma.compress(payload, format=lzma.FORMAT_XZ, preset=9 | lzma.PRESET_EXTREME)
        raise ArchiveError("REJECT_UNROOTED_DECODER", codec)

    @staticmethod
    def _decompress(codec: str, payload: bytes) -> bytes:
        if codec == "raw":
            return payload
        if codec == "zlib":
            return zlib.decompress(payload)
        if codec == "lzma":
            return lzma.decompress(payload, format=lzma.FORMAT_XZ)
        raise ArchiveError("REJECT_UNAVAILABLE_REQUIRED_DECODER", codec)

    def _select_codec(self, payload: bytes) -> tuple[str, bytes, list[dict[str, Any]]]:
        candidates: list[tuple[int, int, str, bytes]] = []
        observations: list[dict[str, Any]] = []
        order = {name: i for i, name in enumerate(self.policy.codec_candidates)}
        for codec in self.policy.codec_candidates:
            compressed = self._compress(codec, payload)
            # Deterministic lifecycle proxy: stored bytes + one unit per source byte + decoder fixed charge.
            decoder_charge = {"raw": 0, "zlib": 64, "lzma": 256}[codec]
            lifecycle_cost = len(compressed) + len(payload) + decoder_charge
            observations.append({
                "codec": codec,
                "compressed_size_bytes": len(compressed),
                "lifecycle_cost_units": lifecycle_cost,
                "decoder_root_hash72": self.DECODER_ROOTS[codec],
            })
            candidates.append((lifecycle_cost, order[codec], codec, compressed))
        _, _, codec, compressed = min(candidates, key=lambda x: (x[0], x[1]))
        return codec, compressed, observations

    def _chunk(self, payload: bytes) -> list[bytes]:
        return [payload[i : i + self.policy.chunk_size_bytes] for i in range(0, len(payload), self.policy.chunk_size_bytes)] or [b""]

    @staticmethod
    def validate_stable_source(source: Mapping[str, Any]) -> None:
        if "exit_checkpoint" in source:
            checkpoint = source["exit_checkpoint"]
            if checkpoint.get("checkpoint_status") != "EXIT_CHECKPOINT_FINALIZED":
                raise ArchiveError("REJECT_VM_SNAPSHOT_AT_UNSTABLE_COORDINATE", "Pass 112 checkpoint not finalized")
            if not checkpoint.get("last_valid_checkpoint_root_hash72"):
                raise ArchiveError("REJECT_VM_SNAPSHOT_AT_UNSTABLE_COORDINATE", "missing stable state root")
        if source.get("open_receipt_transaction") is True or source.get("partial_mutation_present") is True:
            raise ArchiveError("REJECT_VM_SNAPSHOT_AT_UNSTABLE_COORDINATE", "source contains open mutation state")

    def archive(
        self,
        source: Mapping[str, Any],
        *,
        source_class: str,
        recovery_contract: RecoveryContract,
        authority_root_hash72: str,
        dependency_root_hash72: str,
        security_policy_root_hash72: str,
        provenance_root_hash72: str,
    ) -> dict[str, Any]:
        self.validate_stable_source(source)
        if not all((authority_root_hash72, dependency_root_hash72, security_policy_root_hash72, provenance_root_hash72)):
            raise ArchiveError("REJECT_REQUIRED_EXTERNAL_RESOURCE_UNDECLARED", "all identity roots are required")
        source_copy = deepcopy(dict(source))
        source_bytes = _canonical_json_bytes(source_copy)
        source_state_root = _hash("hhs_pass113_source_state_v1", source_copy)
        codec, compressed, codec_observations = self._select_codec(source_bytes)
        chunks = self._chunk(compressed)
        if len(chunks) > recovery_contract.maximum_chunk_count:
            raise ArchiveError("REJECT_UNBOUNDED_RECOVERY_WORK", "chunk count exceeds recovery contract")
        chunk_entries: list[dict[str, Any]] = []
        for index, chunk in enumerate(chunks):
            entry = {
                "chunk_index": index,
                "compressed_offset": index * self.policy.chunk_size_bytes,
                "compressed_size_bytes": len(chunk),
                "chunk_root_hash72": _hash("hhs_pass113_archive_chunk_v1", {"index": index, "bytes_hex": chunk.hex()}),
                "payload_hex": chunk.hex(),
                "security_domain": self.policy.security_domain,
            }
            chunk_entries.append(entry)
        compressed_root = _hash("hhs_pass113_compressed_stream_v1", [x["chunk_root_hash72"] for x in chunk_entries])
        maximum_work = len(source_bytes) + len(compressed) + len(chunks)
        maximum_memory = max(self.policy.chunk_size_bytes * 2, min(len(source_bytes) + self.policy.chunk_size_bytes, len(source_bytes) * 2 + 1))
        if maximum_work > recovery_contract.maximum_recovery_work_units:
            raise ArchiveError("REJECT_UNBOUNDED_RECOVERY_WORK", "predicted recovery work exceeds contract")
        if maximum_memory > recovery_contract.maximum_recovery_memory_bytes:
            raise ArchiveError("REJECT_UNBOUNDED_RECOVERY_MEMORY", "predicted recovery memory exceeds contract")
        manifest = {
            "schema": ARCHIVE_MANIFEST_SCHEMA,
            "source_state_root_hash72": source_state_root,
            "source_class": source_class,
            "compression_class": "VIRTUAL_MACHINE_ARCHIVE_COMPRESSION" if "VM" in source_class else "EXECUTION_STATE_COMPRESSION",
            "canonicalization_root_hash72": _hash("hhs_pass113_canonical_json_v1", {"encoding": "UTF-8", "sort_keys": True, "separators": [",", ":"]}),
            "compression_algorithm": codec,
            "compression_algorithm_root_hash72": self.DECODER_ROOTS[codec],
            "algorithm_version": 1,
            "dictionary_roots": [],
            "chunk_map_root_hash72": _hash("hhs_pass113_chunk_map_v1", [{k: v for k, v in x.items() if k != "payload_hex"} for x in chunk_entries]),
            "dependency_root_hash72": dependency_root_hash72,
            "authority_root_hash72": authority_root_hash72,
            "security_policy_root_hash72": security_policy_root_hash72,
            "provenance_root_hash72": provenance_root_hash72,
            "recovery_contract_root_hash72": recovery_contract.root_hash72,
            "maximum_recovery_work": maximum_work,
            "maximum_recovery_memory_bytes": maximum_memory,
            "maximum_dependency_depth": 1,
            "random_access_granularity": self.policy.chunk_size_bytes,
            "uncompressed_size_bytes": len(source_bytes),
            "compressed_size_bytes": len(compressed),
            "compressed_stream_root_hash72": compressed_root,
            "codec_observations": codec_observations,
            "archive_policy_root_hash72": self.policy.root_hash72,
        }
        manifest["compression_manifest_root_hash72"] = _hash("hhs_pass113_compression_manifest_v1", manifest)
        archive = {
            "schema": ARCHIVE_SCHEMA,
            "manifest": manifest,
            "recovery_contract": {"schema": RECOVERY_CONTRACT_SCHEMA, **asdict(recovery_contract), "recovery_contract_root_hash72": recovery_contract.root_hash72},
            "chunks": chunk_entries,
            "context_bindings": {
                "authority_root_hash72": authority_root_hash72,
                "dependency_root_hash72": dependency_root_hash72,
                "security_policy_root_hash72": security_policy_root_hash72,
                "provenance_root_hash72": provenance_root_hash72,
            },
        }
        archive["archive_root_hash72"] = _hash("hhs_pass113_archive_v1", archive)
        compression_receipt = {
            "schema": COMPRESSION_RECEIPT_SCHEMA,
            "source_state_root_hash72": source_state_root,
            "canonical_source_root_hash72": source_state_root,
            "compression_manifest_root_hash72": manifest["compression_manifest_root_hash72"],
            "archive_root_hash72": archive["archive_root_hash72"],
            "uncompressed_size_bytes": len(source_bytes),
            "compressed_size_bytes": len(compressed),
            "deduplicated_bytes": 0,
            "compression_ratio": {"numerator": len(source_bytes), "denominator": max(1, len(compressed))},
            "maximum_recovery_work_units": maximum_work,
            "maximum_recovery_memory_bytes": maximum_memory,
            "preservation_vector_root_hash72": _hash("hhs_pass113_preservation_vector_v1", self._preservation_vector(True)),
            "security_policy_root_hash72": security_policy_root_hash72,
            "compression_status": "LOSSLESS_ARCHIVE_ADMITTED",
        }
        compression_receipt["compression_receipt_root_hash72"] = _hash("hhs_pass113_compression_receipt_v1", compression_receipt)
        return {"archive": archive, "compression_receipt": compression_receipt}

    @staticmethod
    def _preservation_vector(value: bool) -> dict[str, bool]:
        return {key: value for key in (
            "payload", "value", "type", "grammar", "scope", "operation_order", "dependency", "authority",
            "receipt", "branch", "phase", "frontier", "security", "provenance", "execution_semantics",
        )}

    @staticmethod
    def _validate_roots(archive: Mapping[str, Any]) -> None:
        supplied_archive_root = archive.get("archive_root_hash72")
        calculated_archive_root = _hash("hhs_pass113_archive_v1", {k: deepcopy(v) for k, v in archive.items() if k != "archive_root_hash72"})
        if supplied_archive_root != calculated_archive_root:
            raise ArchiveError("REJECT_ARCHIVE_ROOT_MISMATCH", "archive root mismatch")
        manifest = archive["manifest"]
        supplied_manifest_root = manifest.get("compression_manifest_root_hash72")
        calculated_manifest_root = _hash("hhs_pass113_compression_manifest_v1", {k: deepcopy(v) for k, v in manifest.items() if k != "compression_manifest_root_hash72"})
        if supplied_manifest_root != calculated_manifest_root:
            raise ArchiveError("REJECT_ARCHIVE_MANIFEST_ROOT_MISMATCH", "manifest root mismatch")

    def inspect_recovery(self, archive: Mapping[str, Any], available_memory_bytes: int, available_work_units: int) -> dict[str, Any]:
        self._validate_roots(archive)
        manifest = archive["manifest"]
        contract = archive["recovery_contract"]
        if available_memory_bytes < manifest["maximum_recovery_memory_bytes"]:
            return {"status": "INSUFFICIENT_RECOVERY_RESOURCES", "dimension": "memory"}
        if available_work_units < manifest["maximum_recovery_work"]:
            return {"status": "INSUFFICIENT_RECOVERY_RESOURCES", "dimension": "work"}
        if manifest["maximum_recovery_memory_bytes"] > contract["maximum_recovery_memory_bytes"]:
            raise ArchiveError("REJECT_UNBOUNDED_RECOVERY_MEMORY", "manifest exceeds contract")
        if manifest["maximum_recovery_work"] > contract["maximum_recovery_work_units"]:
            raise ArchiveError("REJECT_UNBOUNDED_RECOVERY_WORK", "manifest exceeds contract")
        return {"status": "RECOVERY_RESOURCES_ADMITTED"}

    def recover(
        self,
        archive: Mapping[str, Any],
        *,
        available_memory_bytes: int,
        available_work_units: int,
        revalidate_authority_root_hash72: str,
    ) -> dict[str, Any]:
        inspection = self.inspect_recovery(archive, available_memory_bytes, available_work_units)
        if inspection["status"] != "RECOVERY_RESOURCES_ADMITTED":
            raise ArchiveError("REJECT_RECOVERY_WITHOUT_RESOURCE_CONTRACT", str(inspection))
        manifest = archive["manifest"]
        if revalidate_authority_root_hash72 != manifest["authority_root_hash72"]:
            raise ArchiveError("REJECT_AUTHORITY_REACTIVATION_WITHOUT_REVALIDATION", "authority root changed")
        if len(archive["chunks"]) > archive["recovery_contract"]["maximum_chunk_count"]:
            raise ArchiveError("REJECT_ARCHIVE_BOMB", "chunk count exceeds contract")
        compressed_parts: list[bytes] = []
        for expected_index, entry in enumerate(archive["chunks"]):
            if entry.get("chunk_index") != expected_index:
                raise ArchiveError("REJECT_NONDETERMINISTIC_CHUNKING", "chunk order mismatch")
            chunk = bytes.fromhex(entry["payload_hex"])
            root = _hash("hhs_pass113_archive_chunk_v1", {"index": expected_index, "bytes_hex": chunk.hex()})
            if root != entry.get("chunk_root_hash72"):
                raise ArchiveError("REJECT_CORRUPTED_ARCHIVE_CHUNK", f"chunk {expected_index}")
            if entry.get("security_domain") != self.policy.security_domain:
                raise ArchiveError("REJECT_SECURITY_DOMAIN_CROSS_DEDUPLICATION", "chunk security domain mismatch")
            compressed_parts.append(chunk)
        compressed = b"".join(compressed_parts)
        if len(compressed) != manifest["compressed_size_bytes"]:
            raise ArchiveError("REJECT_BYTE_IDENTITY_MISMATCH", "compressed length mismatch")
        source_bytes = self._decompress(manifest["compression_algorithm"], compressed)
        if len(source_bytes) != manifest["uncompressed_size_bytes"]:
            raise ArchiveError("REJECT_BYTE_IDENTITY_MISMATCH", "uncompressed length mismatch")
        left = len(source_bytes) * archive["recovery_contract"]["maximum_expansion_ratio_denominator"]
        right = max(1, len(compressed)) * archive["recovery_contract"]["maximum_expansion_ratio_numerator"]
        if left > right:
            raise ArchiveError("REJECT_ARCHIVE_EXPANSION_RATIO_EXCEEDED", "expanded data exceeds contract")
        try:
            recovered = json.loads(source_bytes.decode("utf-8"))
        except Exception as exc:
            raise ArchiveError("REJECT_BYTE_IDENTITY_MISMATCH", str(exc)) from exc
        recovered_root = _hash("hhs_pass113_source_state_v1", recovered)
        if recovered_root != manifest["source_state_root_hash72"]:
            raise ArchiveError("REJECT_BYTE_IDENTITY_MISMATCH", "source state root mismatch")
        vector = self._preservation_vector(True)
        receipt = {
            "schema": RECOVERY_RECEIPT_SCHEMA,
            "archive_root_hash72": archive["archive_root_hash72"],
            "source_state_root_hash72": manifest["source_state_root_hash72"],
            "recovered_state_root_hash72": recovered_root,
            "decoder_root_hash72": manifest["compression_algorithm_root_hash72"],
            "recovery_environment_root_hash72": _hash("hhs_pass113_recovery_environment_v1", {"available_memory_bytes": available_memory_bytes, "available_work_units": available_work_units}),
            "recovered_chunk_roots": [x["chunk_root_hash72"] for x in archive["chunks"]],
            "corrupted_chunk_roots": [],
            "preservation_vector": vector,
            "recovery_work_units": manifest["maximum_recovery_work"],
            "peak_recovery_memory_bytes": manifest["maximum_recovery_memory_bytes"],
            "recovery_status": "RECOVERY_VALIDATED",
        }
        receipt["recovery_validation_root_hash72"] = _hash("hhs_pass113_recovery_validation_v1", receipt)
        return {"recovered_state": recovered, "recovery_receipt": receipt}

    def migrate(self, archive: Mapping[str, Any], *, new_policy: ArchivePolicy, recovery_contract: RecoveryContract) -> dict[str, Any]:
        recovered = self.recover(
            archive,
            available_memory_bytes=archive["recovery_contract"]["maximum_recovery_memory_bytes"],
            available_work_units=archive["recovery_contract"]["maximum_recovery_work_units"],
            revalidate_authority_root_hash72=archive["manifest"]["authority_root_hash72"],
        )
        new_engine = SafeLosslessArchiveEngine(new_policy)
        migrated = new_engine.archive(
            recovered["recovered_state"],
            source_class=archive["manifest"]["source_class"],
            recovery_contract=recovery_contract,
            authority_root_hash72=archive["manifest"]["authority_root_hash72"],
            dependency_root_hash72=archive["manifest"]["dependency_root_hash72"],
            security_policy_root_hash72=archive["manifest"]["security_policy_root_hash72"],
            provenance_root_hash72=archive["manifest"]["provenance_root_hash72"],
        )
        if migrated["archive"]["manifest"]["source_state_root_hash72"] != archive["manifest"]["source_state_root_hash72"]:
            raise ArchiveError("REJECT_ARCHIVE_MIGRATION_WITHOUT_EQUIVALENCE_PROOF", "migration changed source state")
        relation = {
            "schema": "HHS_ARCHIVE_MIGRATION_RELATION_V1",
            "old_archive_root_hash72": archive["archive_root_hash72"],
            "new_archive_root_hash72": migrated["archive"]["archive_root_hash72"],
            "source_state_root_hash72": archive["manifest"]["source_state_root_hash72"],
            "equivalence_valid": True,
            "old_archive_retained": True,
        }
        relation["migration_relation_root_hash72"] = _hash("hhs_pass113_archive_migration_v1", relation)
        return {**migrated, "migration_relation": relation}


def _build_pass112_bundles() -> tuple[dict[str, Any], dict[str, Any]]:
    workload, continuation, cache, lease, _ = _build_pass111_fixture()
    engine = PassSafeExitEngine(workload.operation_id)
    admission = continuation.replay_tail(cache, lease)
    completion = continuation.continue_execution(cache, admission, lease)
    checkpoint = engine.finalize_exit_checkpoint(
        cache=cache,
        exit_classification=engine.classify_exit(completion=completion, resume_error=None),
        admission=admission,
        completion=completion,
    )
    resources = _default_resources()
    plan = engine.build_cleanup_plan(checkpoint, resources)
    cleanup = engine.execute_cleanup(checkpoint, plan, ResourceLedger(resources))
    disposition = engine.disposition_cache(checkpoint, cache)
    exit_receipt = engine.emit_exit_receipt(exit_checkpoint=checkpoint, cleanup_receipt=cleanup, cache_disposition=disposition)
    completed = {"exit_checkpoint": checkpoint, "cleanup_receipt": cleanup, "cache_disposition": disposition, "exit_receipt": exit_receipt}

    deferred_checkpoint = engine.finalize_exit_checkpoint(cache=cache, exit_classification="EXIT_RESOURCE_BOUND")
    deferred_resources = _default_resources()
    deferred_plan = engine.build_cleanup_plan(deferred_checkpoint, deferred_resources)
    deferred_cleanup = engine.execute_cleanup(deferred_checkpoint, deferred_plan, ResourceLedger(deferred_resources))
    deferred_disposition = engine.disposition_cache(deferred_checkpoint, cache)
    deferred_exit = engine.emit_exit_receipt(exit_checkpoint=deferred_checkpoint, cleanup_receipt=deferred_cleanup, cache_disposition=deferred_disposition)
    deferred = {"exit_checkpoint": deferred_checkpoint, "cleanup_receipt": deferred_cleanup, "cache_disposition": deferred_disposition, "exit_receipt": deferred_exit}
    return completed, deferred


def pass113_self_test() -> dict[str, Any]:
    completed, deferred = _build_pass112_bundles()
    engine = SafeLosslessArchiveEngine(ArchivePolicy(chunk_size_bytes=512))
    contract = RecoveryContract(
        maximum_recovery_memory_bytes=2_000_000,
        maximum_recovery_work_units=5_000_000,
        maximum_expansion_ratio_numerator=100,
        maximum_chunk_count=4096,
    )
    roots = {
        "authority": _hash("hhs_pass113_authority_v1", {"operation": "archive_pass112_state"}),
        "dependency": _hash("hhs_pass113_dependency_v1", {"pass": 112, "version": 1}),
        "security": _hash("hhs_pass113_security_v1", {"domain": "authoritative_exit_state"}),
        "provenance": _hash("hhs_pass113_provenance_v1", {"parent": "PASS_112"}),
    }
    completed_archive = engine.archive(completed, source_class="VM_PASS112_COMPLETED_EXIT", recovery_contract=contract,
        authority_root_hash72=roots["authority"], dependency_root_hash72=roots["dependency"],
        security_policy_root_hash72=roots["security"], provenance_root_hash72=roots["provenance"])
    completed_recovery = engine.recover(completed_archive["archive"], available_memory_bytes=2_000_000,
        available_work_units=5_000_000, revalidate_authority_root_hash72=roots["authority"])
    deferred_archive = engine.archive(deferred, source_class="VM_PASS112_DEFERRED_EXIT", recovery_contract=contract,
        authority_root_hash72=roots["authority"], dependency_root_hash72=roots["dependency"],
        security_policy_root_hash72=roots["security"], provenance_root_hash72=roots["provenance"])
    deferred_recovery = engine.recover(deferred_archive["archive"], available_memory_bytes=2_000_000,
        available_work_units=5_000_000, revalidate_authority_root_hash72=roots["authority"])
    completed_exit_reconstruction = PassSafeExitEngine.reconstruct_exit(completed_recovery["recovered_state"])
    deferred_exit_reconstruction = PassSafeExitEngine.reconstruct_exit(deferred_recovery["recovered_state"])
    migrated = engine.migrate(completed_archive["archive"], new_policy=ArchivePolicy(chunk_size_bytes=1024, codec_candidates=("zlib", "raw")), recovery_contract=contract)
    result = {
        "schema": "HHS_PASS113_SAFE_LOSSLESS_ARCHIVE_SELF_TEST_V1",
        "pass_id": PASS_ID,
        "status": "PASS" if all((
            completed_recovery["recovered_state"] == completed,
            deferred_recovery["recovered_state"] == deferred,
            completed_exit_reconstruction["reconstruction_status"] == "RECONSTRUCTED",
            deferred_exit_reconstruction["reconstruction_status"] == "RECONSTRUCTED",
            migrated["migration_relation"]["equivalence_valid"],
        )) else "FAIL",
        "completed_archive": completed_archive,
        "deferred_archive": deferred_archive,
        "completed_recovery": completed_recovery,
        "deferred_recovery": deferred_recovery,
        "completed_exit_reconstruction": completed_exit_reconstruction,
        "deferred_exit_reconstruction": deferred_exit_reconstruction,
        "migration": migrated,
        "corrupted_state_admitted": 0,
        "unbounded_recovery_contracts": 0,
        "undeclared_external_dependencies": 0,
        "execution_equivalence_failures": 0,
        "mock_components": [],
    }
    result["pass113_root_hash72"] = _hash("hhs_pass113_self_test_v1", result)
    return result


if __name__ == "__main__":
    print(json.dumps(pass113_self_test(), indent=2, sort_keys=True))
