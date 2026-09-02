"""Pass 196 serialized-parallel repository integration and encrypted VM memory."""
from __future__ import annotations

import json
import os
import platform
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256, sha512
from pathlib import Path
from typing import Any, Iterable, Mapping

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_runtime.pass163.vmrc import SNAPSHOT_BYTES
from hhs_runtime.pass174.runtime import Hash216Array
from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore

VERSION = "HHS_PASS_196_SERIALIZED_PARALLEL_INTEGRATED_ENVIRONMENT_V1"
CONTRACT = "HHS-P196-SPIRAH-EVDB-LINUX-TOOLSERVER-VIDE-VM81-H72-H216"
CLASSIFICATION = "HHS_PASS_196_REPOSITORY_INTEGRATION_DEEP_SCAN_RUNTIME"
MANIFEST_SCHEMA = "HHS_PASS_196_INTEGRATION_MANIFEST_V1"
STATUS_SCHEMA = "HHS_PASS_196_INTEGRATED_ENVIRONMENT_STATUS_V1"
TOOL_SCHEMA = "HHS_PASS_196_API_TOOL_REGISTRY_V1"
MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_SCAN_FILES = 100_000
EXCLUDED = {".git", ".hg", ".svn", ".hhs", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build", "coverage"}
PASS_HEADER = re.compile(r"(?im)^#\s*HHS\s+PASS\s+0*([0-9]{1,4})\b")
PASS_PATH = re.compile(r"(?i)(?:^|[/_.-])pass[_-]?0*([0-9]{1,4})(?:[/_.-]|$)")
ROOT_CONTRACT = re.compile(r"(?i)^HHS_PASS_0*([0-9]{1,4})(?:_|\.)")
SURFACES = ("contract", "runtime", "api", "operation_registry", "hydration", "vector_store", "linux", "tool_server", "visual_ide", "test", "ci", "deployment", "evidence")
MANDATORY = ("runtime", "api", "operation_registry", "hydration", "vector_store", "linux", "tool_server", "visual_ide", "test", "ci")


class Pass196Error(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False, default=str).encode()


def _roles(path: str, text: str) -> list[str]:
    lower = path.lower()
    found: set[str] = set()
    if (Path(path).name.upper().startswith("HHS_PASS_") or "/docs/pass" in f"/{lower}") and lower.endswith(".md"):
        found.add("contract")
    checks = {
        "runtime": ("/runtime/", "hhs_runtime", "runtime_", "_runtime"),
        "api": ("/api/", "routes.py", "openapi", "server.py"),
        "operation_registry": ("registry", "operation_fabric"),
        "hydration": ("hydrat", "ingest", "token"),
        "vector_store": ("vector", "memristor", "vmrc"),
        "linux": ("linux", "systemd", ".service", "digitalocean", "nginx"),
        "tool_server": ("tool_server", "tool-server", "mcp", "service_registry"),
        "visual_ide": ("visual", "harmonizer", "ide", "frontend", "applications/", ".tsx", ".mjs"),
        "test": ("/test", "tests/", "test_", "_test."),
        "deployment": ("/deploy/", "dockerfile", "compose", ".service"),
        "evidence": ("/evidence/", "receipt", "restart_record"),
    }
    for role, tokens in checks.items():
        if any(token in lower for token in tokens):
            found.add(role)
    if ".github/workflows" in lower or lower.endswith((".yml", ".yaml")) and "workflow" in lower:
        found.add("ci")
    if "APIRouter(" in text or "FastAPI(" in text:
        found.add("api")
    if "PersistentEncryptedVectorStore" in text or "AESGCM" in text:
        found.add("vector_store")
    if "HHSServiceRegistry" in text or "tools/invoke" in text:
        found.add("tool_server")
    return [role for role in SURFACES if role in found]


def _pass(path: str, text: str) -> int | None:
    for match in (ROOT_CONTRACT.match(Path(path).name), PASS_PATH.search(path), PASS_HEADER.search(text)):
        if match:
            return int(match.group(1))
    return None


def _observe(root: Path, path: Path) -> dict[str, Any]:
    relative = path.relative_to(root).as_posix()
    digest = sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    text = ""
    text_scanned = False
    if size <= MAX_TEXT_BYTES:
        try:
            text = path.read_text(encoding="utf-8")
            text_scanned = True
        except (UnicodeDecodeError, OSError):
            pass
    roles = _roles(relative, text)
    pass_number = _pass(relative, text)
    body = {"path": relative, "size_bytes": size, "sha256": digest.hexdigest(), "primary_pass": pass_number, "surfaces": roles}
    return {**body, "hash72": hash72("pass196.repository.file", body), "text_scanned": text_scanned}


def _files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and not any(part in EXCLUDED for part in path.relative_to(root).parts):
            result.append(path)
            if len(result) > MAX_SCAN_FILES:
                raise Pass196Error(f"repository exceeds bounded scan limit {MAX_SCAN_FILES}")
    return sorted(result, key=lambda item: item.relative_to(root).as_posix())


def _snapshot(payload: Mapping[str, Any]) -> bytes:
    canonical = _canonical(payload)
    seed = sha512(b"HHS-PASS196-VM5184\0" + canonical).digest()
    output = bytearray()
    counter = 0
    while len(output) < SNAPSHOT_BYTES:
        output.extend(sha512(seed + counter.to_bytes(8, "big") + canonical[:4096]).digest())
        counter += 1
    return bytes(output[:SNAPSHOT_BYTES])


def _changed(left: bytes, right: bytes) -> int:
    return sum((a ^ b).bit_count() for a, b in zip(left, right))


class Pass196IntegratedEnvironment:
    def __init__(self, repository_root: str | Path | None = None, *, state_root: str | Path | None = None, workers: int | None = None) -> None:
        default_root = Path(__file__).resolve().parents[2]
        self.repository_root = Path(repository_root or os.getenv("HHS_REPOSITORY_ROOT") or default_root).resolve()
        self.state_root = Path(state_root or os.getenv("HHS_PASS196_STATE_ROOT") or self.repository_root / ".hhs" / "pass196").resolve()
        self.vector_database = self.state_root / "integrated_vectors.sqlite3"
        self.vector_key = self.state_root / "integrated_vectors.key"
        self.workers = max(1, min(int(workers or os.cpu_count() or 4), 32))
        self._lock = threading.RLock()
        self._manifest: dict[str, Any] | None = None
        self._last_snapshot = bytes(SNAPSHOT_BYTES)
        self._last_vector_object_id: str | None = None
        self._phase = "UNSCANNED"

    def _pass_matrix(self, observations: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
        grouped: dict[int, list[dict[str, Any]]] = {}
        for item in observations:
            if item["primary_pass"] is not None:
                grouped.setdefault(item["primary_pass"], []).append(item)
        maximum = max(grouped, default=0)
        matrix = []
        for number in range(1, maximum + 1):
            items = grouped.get(number, [])
            surfaces = [role for role in SURFACES if any(role in item["surfaces"] for item in items)]
            contracts = [item["path"] for item in items if "contract" in item["surfaces"]]
            executable = any(role in surfaces for role in ("runtime", "api", "operation_registry", "hydration"))
            state = "UNRESOLVED" if not items else "CONTRACT_ONLY" if contracts and not executable else "INTEGRATED" if executable and any(role in surfaces for role in ("test", "evidence")) else "PARTIAL"
            matrix.append({"pass_number": number, "state": state, "artifact_count": len(items), "surfaces": surfaces, "contracts": contracts, "artifact_root_hash72": hash72("pass196.pass.artifacts", [item["hash72"] for item in items])})
        return matrix, maximum

    @staticmethod
    def _surface_matrix(observations: Iterable[dict[str, Any]]) -> dict[str, Any]:
        paths = {role: [] for role in SURFACES}
        for item in observations:
            for role in item["surfaces"]:
                paths[role].append(item["path"])
        counts = {role: len(values) for role, values in paths.items()}
        missing = [role for role in MANDATORY if counts[role] == 0]
        return {"counts": counts, "missing_mandatory_surfaces": missing, "complete": not missing, "examples": {role: values[:8] for role, values in paths.items() if values}}

    def scan(self, *, vm81_receipt_hash72: str | None = None, persist_vector: bool = True) -> dict[str, Any]:
        with self._lock:
            self._phase = "PARALLEL_OBSERVATION"
            paths = _files(self.repository_root)
            with ThreadPoolExecutor(max_workers=self.workers, thread_name_prefix="hhs-pass196") as pool:
                observations = sorted(pool.map(lambda path: _observe(self.repository_root, path), paths), key=lambda item: item["path"])
            self._phase = "SERIALIZED_CLASSIFICATION"
            pass_matrix, maximum = self._pass_matrix(observations)
            surface_matrix = self._surface_matrix(observations)
            counts = {state: sum(item["state"] == state for item in pass_matrix) for state in ("INTEGRATED", "PARTIAL", "CONTRACT_ONLY", "UNRESOLVED")}
            body = {
                "schema": MANIFEST_SCHEMA, "version": VERSION, "contract": CONTRACT, "classification": CLASSIFICATION,
                "repository_root": str(self.repository_root), "parallel_worker_count": self.workers,
                "parallel_observation_serialized_commit": True, "file_count": len(observations),
                "byte_count": sum(item["size_bytes"] for item in observations), "maximum_discovered_pass": maximum,
                "pass_state_counts": counts, "pass_matrix": pass_matrix, "surface_matrix": surface_matrix,
                "files": observations, "vm81_receipt_hash72": vm81_receipt_hash72,
                "authority": {"observer_threads_are_authority": False, "vector_store_is_source_authority": False, "api_is_mutation_authority": False, "ide_is_mutation_authority": False, "canonical_admission": "VM81_AUTHORIZED_TICK_AND_HASH72_RECEIPT"},
            }
            current = hash72("pass196.integration.manifest", body)
            manifest = {**body, "manifest_hash72": current, "manifest_hash216": "".join(hash72(f"pass196.integration.manifest:{lane}", body) for lane in ("minus", "center", "plus"))}
            snapshot = _snapshot(manifest)
            vector_status: dict[str, Any] = {"persisted": False, "authenticated_encryption": "AES_GCM", "snapshot_bytes": SNAPSHOT_BYTES}
            if persist_vector:
                self._phase = "ENCRYPTED_VECTOR_ADMISSION"
                self.state_root.mkdir(parents=True, exist_ok=True)
                store = PersistentEncryptedVectorStore(self.vector_database, key_path=self.vector_key)
                try:
                    predecessor = self._manifest["manifest_hash72"] if self._manifest else "0" * 72
                    successor = hash72("pass196.integration.successor", {"manifest_hash72": current, "file_count": len(observations)})
                    operation = sha256(b"HHS-PASS196-INTEGRATION-SCAN-V1").hexdigest()
                    genesis = sha256(b"HHS-GENESIS-PASS196").hexdigest()
                    legacy = sha256(_canonical({"maximum_discovered_pass": maximum, "pass_state_counts": counts, "surface_matrix": surface_matrix})).hexdigest()
                    lanes = Hash216Array.build(predecessor, current, successor, genesis_identity=genesis, logical_step=maximum, operation_identity=operation, legacy_foundation_root=legacy)
                    vector = store.admit(operation_key="pass196.repository.integration", logical_step=maximum, input_hash72=predecessor, output_hash72=current, operation_identity_sha256=operation, hash216=lanes, output_snapshot=snapshot, legacy_foundation_root=legacy, genesis_identity=genesis, direct_cost_units=max(1, len(observations)), changed_bits=_changed(self._last_snapshot, snapshot), parent_object_id=self._last_vector_object_id)
                    self._last_vector_object_id = vector.object_id
                    vector_status = {**store.storage_status(), "persisted": True, "vector_object_id": vector.object_id, "snapshot_bytes": SNAPSHOT_BYTES, "plaintext_manifest_persisted": False}
                finally:
                    store.close()
            self._manifest = {**manifest, "vector": vector_status}
            self._last_snapshot = snapshot
            unresolved = counts["PARTIAL"] + counts["CONTRACT_ONLY"] + counts["UNRESOLVED"]
            self._phase = "CLOSED" if surface_matrix["complete"] and unresolved == 0 else "DEGRADED"
            return self.status(include_manifest=True)

    def status(self, *, include_manifest: bool = False) -> dict[str, Any]:
        with self._lock:
            result = {
                "schema": STATUS_SCHEMA, "version": VERSION, "contract": CONTRACT, "classification": CLASSIFICATION,
                "phase": self._phase, "scanned": self._manifest is not None, "repository_root": str(self.repository_root),
                "state_root": str(self.state_root),
                "linux_environment": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(), "python": platform.python_version(), "service_unit": "deploy/digitalocean/hhs-pass196-integrated-environment.service"},
                "api_tool_server": {"base": "/api/runtime/integration", "registry": "/api/runtime/integration/tools", "invoke": "/api/runtime/integration/tools/invoke"},
                "visual_ide": {"application": "/", "projection_module": "applications/holofractal_harmonizer/src/pass196-integration.mjs"},
            }
            if not self._manifest:
                return {**result, "ok": False}
            manifest = self._manifest
            closed = manifest["surface_matrix"]["complete"] and all(item["state"] == "INTEGRATED" for item in manifest["pass_matrix"])
            result.update({key: manifest[key] for key in ("manifest_hash72", "manifest_hash216", "file_count", "byte_count", "maximum_discovered_pass", "pass_state_counts", "surface_matrix", "vector")})
            result.update({"operational": manifest["surface_matrix"]["complete"], "integration_closed": closed, "ok": closed})
            if include_manifest:
                result["manifest"] = manifest
            return result

    def manifest(self) -> dict[str, Any]:
        if self._manifest is None:
            raise Pass196Error("integration manifest is not available; run scan first")
        return json.loads(json.dumps(self._manifest, sort_keys=True))

    def gaps(self) -> dict[str, Any]:
        manifest = self.manifest()
        unresolved = [item for item in manifest["pass_matrix"] if item["state"] != "INTEGRATED"]
        return {"schema": "HHS_PASS_196_INTEGRATION_GAP_REPORT_V1", "manifest_hash72": manifest["manifest_hash72"], "unresolved_pass_count": len(unresolved), "unresolved_passes": unresolved, "missing_mandatory_surfaces": manifest["surface_matrix"]["missing_mandatory_surfaces"], "complete": not unresolved and manifest["surface_matrix"]["complete"]}

    @staticmethod
    def tools() -> dict[str, Any]:
        return {"schema": TOOL_SCHEMA, "tools": [
            {"name": "integration.status", "method": "GET", "path": "/api/runtime/integration/status", "mutation": False},
            {"name": "integration.scan", "method": "POST", "path": "/api/runtime/integration/scan", "mutation": True},
            {"name": "integration.manifest", "method": "GET", "path": "/api/runtime/integration/manifest", "mutation": False},
            {"name": "integration.gaps", "method": "GET", "path": "/api/runtime/integration/gaps", "mutation": False},
        ], "tool_server_is_authority": False, "mutation_requires_vm81_authorized_tick": True}


PASS196_INTEGRATED_ENVIRONMENT = Pass196IntegratedEnvironment()
