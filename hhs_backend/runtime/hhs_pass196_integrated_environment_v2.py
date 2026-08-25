"""Pass 196 I130 repair-forward runtime.

V1 remains immutable historical provenance.  This V2 surface repairs the
reviewed repository-observation, manifest-identity, admission, restart-lineage,
and fail-closed status boundaries without creating a new mutation authority.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

from hhs_backend.runtime.hhs_pass196_integrated_environment_v1 import (
    CLASSIFICATION,
    CONTRACT,
    MANDATORY,
    MANIFEST_SCHEMA,
    MAX_TEXT_BYTES,
    STATUS_SCHEMA,
    SURFACES,
    TOOL_SCHEMA,
    Pass196Error,
    Pass196IntegratedEnvironment,
    _canonical,
    _changed,
    _files,
    _pass,
    _roles,
    _snapshot,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_runtime.pass163.vmrc import SNAPSHOT_BYTES
from hhs_runtime.pass174.runtime import Hash216Array
from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore

VERSION = "HHS_PASS_196_SERIALIZED_PARALLEL_INTEGRATED_ENVIRONMENT_V2_I130_REPAIR"
REPAIR_SCHEMA = "HHS_PASS_196_I130_REPAIR_V1"
VECTOR_OPERATION_KEY = "pass196.repository.integration"


def _require_hash72_receipt(value: str | None) -> str:
    if not isinstance(value, str) or len(value) != 72:
        raise Pass196Error("PASS196_VM81_HASH72_RECEIPT_REQUIRED_FOR_PERSISTENCE")
    return value


def _observe_exact(root: Path, path: Path) -> dict[str, Any]:
    """Hash and classify one immutable byte observation.

    The text used by role/pass classification is decoded from the exact bytes
    that produced the SHA-256.  A metadata change across the read fails closed
    rather than combining two different file versions into one observation.
    """
    relative = path.relative_to(root).as_posix()
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    if (
        before.st_size != after.st_size
        or before.st_mtime_ns != after.st_mtime_ns
        or after.st_size != len(data)
    ):
        raise Pass196Error(f"PASS196_FILE_CHANGED_DURING_SCAN:{relative}")

    text = ""
    text_scanned = False
    if len(data) <= MAX_TEXT_BYTES:
        try:
            text = data.decode("utf-8")
            text_scanned = True
        except UnicodeDecodeError:
            pass

    roles = _roles(relative, text)
    pass_number = _pass(relative, text)
    body = {
        "path": relative,
        "size_bytes": len(data),
        "sha256": sha256(data).hexdigest(),
        "primary_pass": pass_number,
        "surfaces": roles,
    }
    return {
        **body,
        "hash72": hash72("pass196.repository.file", body),
        "text_scanned": text_scanned,
    }


def _support_artifact(item: dict[str, Any]) -> bool:
    path = str(item["path"]).lower()
    roles = set(item["surfaces"])
    return (
        "test" in roles
        or "evidence" in roles
        or "contract" in roles
        or path.startswith("tests/")
        or path.startswith("evidence/")
        or path.startswith("docs/")
        or path.startswith(".github/workflows/")
    )


class Pass196IntegratedEnvironmentV2(Pass196IntegratedEnvironment):
    """Repair-forward Pass 196 implementation used by I130 production wiring."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._last_good_manifest: dict[str, Any] | None = None
        self._last_failure: dict[str, Any] | None = None

    def _pass_matrix(self, observations: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
        grouped: dict[int, list[dict[str, Any]]] = {}
        for item in observations:
            if item["primary_pass"] is not None:
                grouped.setdefault(int(item["primary_pass"]), []).append(item)
        maximum = max(grouped, default=0)
        matrix: list[dict[str, Any]] = []
        for number in range(1, maximum + 1):
            items = grouped.get(number, [])
            surfaces = [role for role in SURFACES if any(role in item["surfaces"] for item in items)]
            contracts = [item["path"] for item in items if "contract" in item["surfaces"]]
            executable_paths = [
                item["path"]
                for item in items
                if not _support_artifact(item)
                and any(role in item["surfaces"] for role in ("runtime", "api", "operation_registry", "hydration"))
            ]
            support_paths = [
                item["path"]
                for item in items
                if any(role in item["surfaces"] for role in ("test", "evidence"))
            ]
            if not items:
                state = "UNRESOLVED"
            elif contracts and not executable_paths:
                state = "CONTRACT_ONLY"
            elif executable_paths and support_paths:
                state = "INTEGRATED"
            else:
                state = "PARTIAL"
            matrix.append(
                {
                    "pass_number": number,
                    "state": state,
                    "artifact_count": len(items),
                    "surfaces": surfaces,
                    "contracts": contracts,
                    "executable_artifacts": executable_paths,
                    "support_artifacts": support_paths,
                    "artifact_root_hash72": hash72(
                        "pass196.pass.artifacts", [item["hash72"] for item in items]
                    ),
                }
            )
        return matrix, maximum

    def _canonical_manifest_body(
        self,
        observations: list[dict[str, Any]],
        pass_matrix: list[dict[str, Any]],
        surface_matrix: dict[str, Any],
        maximum: int,
        counts: dict[str, int],
    ) -> dict[str, Any]:
        # Host path, CPU/worker count, platform diagnostics, and admission receipt
        # intentionally remain outside this identity body.
        return {
            "schema": MANIFEST_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "repair_schema": REPAIR_SCHEMA,
            "parallel_observation_serialized_commit": True,
            "same_bytes_hash_and_classification": True,
            "file_count": len(observations),
            "byte_count": sum(int(item["size_bytes"]) for item in observations),
            "maximum_discovered_pass": maximum,
            "pass_state_counts": counts,
            "pass_matrix": pass_matrix,
            "surface_matrix": surface_matrix,
            "files": observations,
            "authority": {
                "observer_threads_are_authority": False,
                "vector_store_is_source_authority": False,
                "api_is_mutation_authority": False,
                "ide_is_mutation_authority": False,
                "canonical_admission": "VM81_AUTHORIZED_TICK_AND_HASH72_RECEIPT",
            },
        }

    @staticmethod
    def _restore_vector_lineage(
        store: PersistentEncryptedVectorStore,
    ) -> tuple[str, str | None]:
        previous = [obj for obj in store.objects() if obj.operation_key == VECTOR_OPERATION_KEY]
        if not previous:
            return "0" * 72, None
        latest = previous[-1]
        return latest.output_hash72, latest.object_id

    def _quarantine(self, exc: BaseException) -> None:
        if self._manifest is not None:
            self._last_good_manifest = json.loads(json.dumps(self._manifest, sort_keys=True))
        self._manifest = None
        self._phase = "QUARANTINED"
        self._last_failure = {
            "schema": "HHS_PASS_196_SCAN_FAILURE_QUARANTINE_V1",
            "reason": str(exc),
            "failure_type": type(exc).__name__,
        }

    def scan(self, *, vm81_receipt_hash72: str | None = None, persist_vector: bool = True) -> dict[str, Any]:
        with self._lock:
            try:
                receipt = _require_hash72_receipt(vm81_receipt_hash72) if persist_vector else vm81_receipt_hash72
                self._phase = "PARALLEL_OBSERVATION"
                paths = _files(self.repository_root)
                from concurrent.futures import ThreadPoolExecutor

                with ThreadPoolExecutor(max_workers=self.workers, thread_name_prefix="hhs-pass196-v2") as pool:
                    observations = sorted(
                        pool.map(lambda path: _observe_exact(self.repository_root, path), paths),
                        key=lambda item: item["path"],
                    )

                self._phase = "SERIALIZED_CLASSIFICATION"
                pass_matrix, maximum = self._pass_matrix(observations)
                surface_matrix = self._surface_matrix(observations)
                counts = {
                    state: sum(item["state"] == state for item in pass_matrix)
                    for state in ("INTEGRATED", "PARTIAL", "CONTRACT_ONLY", "UNRESOLVED")
                }
                body = self._canonical_manifest_body(
                    observations, pass_matrix, surface_matrix, maximum, counts
                )
                current = hash72("pass196.integration.manifest", body)
                manifest = {
                    **body,
                    "manifest_hash72": current,
                    "manifest_hash216": "".join(
                        hash72(f"pass196.integration.manifest:{lane}", body)
                        for lane in ("minus", "center", "plus")
                    ),
                    "observation_diagnostics": {
                        "repository_root": str(self.repository_root),
                        "parallel_worker_count": self.workers,
                    },
                    "vm81_receipt_hash72": receipt,
                }
                snapshot = _snapshot(body)
                vector_status: dict[str, Any] = {
                    "persisted": False,
                    "authenticated_encryption": "AES_GCM",
                    "snapshot_bytes": SNAPSHOT_BYTES,
                }

                if persist_vector:
                    self._phase = "ENCRYPTED_VECTOR_ADMISSION"
                    self.state_root.mkdir(parents=True, exist_ok=True)
                    store = PersistentEncryptedVectorStore(
                        self.vector_database, key_path=self.vector_key
                    )
                    try:
                        predecessor, parent_object_id = self._restore_vector_lineage(store)
                        successor = hash72(
                            "pass196.integration.successor",
                            {
                                "manifest_hash72": current,
                                "vm81_receipt_hash72": receipt,
                                "file_count": len(observations),
                            },
                        )
                        operation = sha256(b"HHS-PASS196-INTEGRATION-SCAN-V1").hexdigest()
                        genesis = sha256(b"HHS-GENESIS-PASS196").hexdigest()
                        legacy = sha256(
                            _canonical(
                                {
                                    "maximum_discovered_pass": maximum,
                                    "pass_state_counts": counts,
                                    "surface_matrix": surface_matrix,
                                }
                            )
                        ).hexdigest()
                        lanes = Hash216Array.build(
                            predecessor,
                            current,
                            successor,
                            genesis_identity=genesis,
                            logical_step=maximum,
                            operation_identity=operation,
                            legacy_foundation_root=legacy,
                        )
                        vector = store.admit(
                            operation_key=VECTOR_OPERATION_KEY,
                            logical_step=maximum,
                            input_hash72=predecessor,
                            output_hash72=current,
                            operation_identity_sha256=operation,
                            hash216=lanes,
                            output_snapshot=snapshot,
                            legacy_foundation_root=legacy,
                            genesis_identity=genesis,
                            direct_cost_units=max(1, len(observations)),
                            changed_bits=_changed(self._last_snapshot, snapshot),
                            parent_object_id=parent_object_id,
                        )
                        self._last_vector_object_id = vector.object_id
                        vector_status = {
                            **store.storage_status(),
                            "persisted": True,
                            "vector_object_id": vector.object_id,
                            "parent_object_id": parent_object_id,
                            "input_hash72": predecessor,
                            "snapshot_bytes": SNAPSHOT_BYTES,
                            "plaintext_manifest_persisted": False,
                            "vm81_receipt_bound": True,
                        }
                    finally:
                        store.close()

                self._manifest = {**manifest, "vector": vector_status}
                self._last_good_manifest = json.loads(json.dumps(self._manifest, sort_keys=True))
                self._last_failure = None
                self._last_snapshot = snapshot
                unresolved = counts["PARTIAL"] + counts["CONTRACT_ONLY"] + counts["UNRESOLVED"]
                self._phase = "CLOSED" if surface_matrix["complete"] and unresolved == 0 else "DEGRADED"
                return self.status(include_manifest=True)
            except Exception as exc:
                self._quarantine(exc)
                raise

    def status(self, *, include_manifest: bool = False) -> dict[str, Any]:
        result = super().status(include_manifest=include_manifest)
        result["version"] = VERSION
        result["repair_schema"] = REPAIR_SCHEMA
        if self._phase == "QUARANTINED":
            result.update(
                {
                    "phase": "QUARANTINED",
                    "scanned": False,
                    "operational": False,
                    "integration_closed": False,
                    "ok": False,
                    "failure": dict(self._last_failure or {}),
                    "last_good_manifest_hash72": (
                        self._last_good_manifest or {}
                    ).get("manifest_hash72"),
                    "last_good_is_historical_only": self._last_good_manifest is not None,
                }
            )
        return result

    def manifest(self) -> dict[str, Any]:
        if self._phase == "QUARANTINED":
            raise Pass196Error("PASS196_CURRENT_MANIFEST_QUARANTINED")
        return super().manifest()

    @staticmethod
    def tools() -> dict[str, Any]:
        result = super(Pass196IntegratedEnvironmentV2, Pass196IntegratedEnvironmentV2).tools()
        result["version"] = VERSION
        result["tool_arguments"] = {
            "integration.scan": {"persist_vector": {"type": "boolean", "default": True}}
        }
        return result


PASS196_INTEGRATED_ENVIRONMENT = Pass196IntegratedEnvironmentV2()
