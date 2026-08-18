"""Pass 219 I116 inherited Pass 209 runtime-bootstrap gateway membrane."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass210 import pass210_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS209_NUMBER = 209
PASS209_CLASSIFICATION = "WIRED"
PASS209_BIND_SYMBOL = "hhs_exact_pass219_bind_pass209_runtime_bootstrap_gateway"
PASS209_SURFACE_ID = "runtime:pass209.runtime-bootstrap-gateway"
PASS209_RESTART_PATH = Path("docs/pass209/RESTART_RECORD.md")
PASS209_CACHE_PATH = Path("hhs_backend/runtime_bootstrap_cache.py")
PASS209_PROBE_PATH = Path("hhs_backend/runtime_status_probe.py")
PASS209_GATEWAY_PATH = Path("hhs_backend/cached_visual_server.py")
PASS209_PRODUCTION_GATEWAY_PATH = Path("hhs_backend/production_visual_server.py")
PASS209_RUNTIME_OS_BRIDGE_PATH = Path("hhs_backend/runtime_os_visual_server.py")
PASS209_SERVICE_PATH = Path("deploy/digitalocean/hhs-pass196-integrated-environment.service")
PASS210_CONTRACT_PATH = Path("contracts/pass210/PASS_210_CONTRACT.json")

PRODUCTION_STATUS_PATHS = (
    "/api/runtime/authority/status",
    "/api/runtime/integration/status",
    "/api/runtime/calibration/status",
    "/api/runtime/calibration-registry/status",
    "/api/runtime/distributed-calibration/status",
    "/api/runtime/optimization-authority/status",
    "/api/runtime/optimization-canary/status",
    "/api/runtime/optimization-active/status",
    "/api/public/status",
)

REQUIRED_OPERATIONS = (
    "RuntimeStatusCache.put",
    "RuntimeStatusCache.lookup",
    "RuntimeStatusCache.snapshot",
    "runtime_status_probe.invoke_get",
    "RuntimeBootstrapGateway.bootstrap_status",
    "RuntimeBootstrapGateway.status_proxy",
    "ProductionRuntimeBootstrapGateway.direct_status_intercept",
)

FROZEN = {
    "validated_branch_head": "f14a03d1d7dee552efd8133b01dda63063b4a32e",
    "main_merge_head": "c05cf860e4be5a0865813529baf9ad99e50dbe02",
    "branch_validation_run": 31012056789,
    "branch_validation_job": 92326490304,
    "restart_blob": "c0810c39f1aaeaf350512811b7390770986d223f",
    "cache_blob": "7efcf952aede8894162d54ecb0575a5aecd7cb83",
    "probe_blob": "5fcce879fe4a435da743e64d35e48c0132416d4f",
    "gateway_blob": "c8b81218a84dc25ddc6b4d2b28b696085edbf707",
    "production_gateway_blob": "4b2c4c0d8fa6bc75acd57a29cf1fbbd2bff3b25b",
    "service_blob": "d0ef21446e56602c2cea242622dbcc707fb59c1b",
    "gateway_test_blob": "97f515056afb71fed25314402d74894ee4534170",
    "production_test_blob": "9de2afc05a3814167f69e7dcefedc738c6c93cfe",
    "validation_workflow_blob": "c0816b71a7e4fd61ea6ad2025f1fdf6f84b16b24",
    "pass210_contract_blob": "ac46a61f568b0443794f854cf84e5a3cfc1bf908",
}


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads(_text(path))
    if not isinstance(value, dict):
        raise RuntimeError("PASS209_OBJECT_REQUIRED")
    return value


def pass209_membrane_source_evidence() -> Dict[str, Any]:
    restart = _text(PASS209_RESTART_PATH)
    cache = _text(PASS209_CACHE_PATH)
    probe = _text(PASS209_PROBE_PATH)
    gateway = _text(PASS209_GATEWAY_PATH)
    production = _text(PASS209_PRODUCTION_GATEWAY_PATH)
    runtime_os_bridge = _text(PASS209_RUNTIME_OS_BRIDGE_PATH)
    service = _text(PASS209_SERVICE_PATH)
    successor_contract = _load(PASS210_CONTRACT_PATH)
    successor = pass210_membrane_source_evidence()

    for token in (
        "production bootstrap latency, direct status caching, and writable state-root closure",
        "Persistent stale-while-revalidate cache",
        "Immediate warming responses for cold cache misses",
        "External writable state roots",
        "writes do not mutate the Git checkout",
    ):
        if token not in restart:
            raise RuntimeError("PASS209_RESTART_BOUNDARY_DRIFT:" + token)

    for token in (
        "class RuntimeStatusCache",
        "values are never canonical authority",
        'state="MISS"',
        'state = "HIT"',
        'else "STALE"',
        "os.replace(temporary, self.path)",
        "def put(",
        "def lookup(",
        "def snapshot(",
    ):
        if token not in cache:
            raise RuntimeError("PASS209_CACHE_GUARD_DRIFT:" + token)

    probe_normalized = " ".join(probe.split())
    for token in (
        "invokes status routes sequentially",
        "never mutates canonical runtime state",
        "async def invoke_get",
        "async def run",
        "HHS_RUNTIME_STATUS_PROBE_RECORD_V1",
    ):
        if token not in probe_normalized:
            raise RuntimeError("PASS209_PROBE_GUARD_DRIFT:" + token)

    for token in (
        "class RuntimeBootstrapGateway",
        "HHS_RUNTIME_STATUS_WARMING_V1",
        "INVALID_STATUS_PROXY_PATH",
        '"canonical_runtime_mutated": False',
        "RuntimeStatusCache",
        "hhs:browser:ready",
    ):
        if token not in gateway:
            raise RuntimeError("PASS209_GATEWAY_GUARD_DRIFT:" + token)

    for path in PRODUCTION_STATUS_PATHS:
        if path not in production:
            raise RuntimeError("PASS209_STATUS_CATALOG_DRIFT:" + path)
    for token in (
        "class ProductionRuntimeBootstrapGateway",
        "lookup = self.cache.lookup(path)",
        "HHS_RUNTIME_STATUS_WARMING_V1",
        "await self._send_json",
        "status_paths=PRODUCTION_STATUS_PATHS",
    ):
        if token not in production:
            raise RuntimeError("PASS209_PRODUCTION_GATEWAY_DRIFT:" + token)

    direct_visual = "from hhs_backend.visual_server import app as authoritative_app" in production
    runtime_os_visual = "from hhs_backend.runtime_os_visual_server import app as authoritative_app" in production
    if not (direct_visual or runtime_os_visual):
        raise RuntimeError("PASS209_AUTHORITATIVE_BACKEND_BRIDGE_DRIFT")
    if runtime_os_visual:
        for token in (
            "from hhs_backend.visual_server import app as inherited_app",
            "app = inherited_app",
            "backend/pass authority remains owned by the inherited HHS runtime",
        ):
            if token not in runtime_os_bridge:
                raise RuntimeError("PASS209_RUNTIME_OS_BACKEND_PRESERVATION_DRIFT:" + token)

    for token in (
        "StateDirectory=hhs",
        "HHS_RUNTIME_STATUS_CACHE=/var/lib/hhs/runtime-bootstrap/status-cache.json",
        "HHS_DATA_DIR=/var/lib/hhs/data",
        "HHS_RUNTIME_OUTPUT_DIR=/var/lib/hhs/data/runtime",
        "HHS_FILESYSTEM_LEDGER_PATH=/var/lib/hhs/data/runtime/hhs_filesystem_ledger.json",
        "ReadWritePaths=/var/lib/hhs",
        "hhs_backend.production_visual_server:app",
    ):
        if token not in service:
            raise RuntimeError("PASS209_SERVICE_BOUNDARY_DRIFT:" + token)
    readwrite_lines = [line.strip() for line in service.splitlines() if line.strip().startswith("ReadWritePaths=")]
    if readwrite_lines != ["ReadWritePaths=/var/lib/hhs"]:
        raise RuntimeError("PASS209_REPOSITORY_WRITE_BOUNDARY_DRIFT")

    if successor_contract.get("pass") != 210 or successor_contract.get("schema") != "HHS_PASS_210_HOLOGRAPHIC_FRAME_COMPRESSION_CONTRACT_V1":
        raise RuntimeError("PASS209_PASS210_CONTRACT_DRIFT")
    inherited_scope = str(successor_contract.get("inherited_scope") or "")
    if "through Pass 209" not in inherited_scope:
        raise RuntimeError("PASS209_PASS210_SUCCESSOR_DRIFT")
    if successor.get("contract", {}).get("pass") != 210:
        raise RuntimeError("PASS209_PASS210_MEMBRANE_DRIFT")

    return {
        "restart": restart,
        "successor_pass210": successor,
        "status_catalog": list(PRODUCTION_STATUS_PATHS),
        "current_runtime_os_projection": runtime_os_visual,
        **FROZEN,
    }


def pass209_surface_declaration() -> Dict[str, Any]:
    pass209_membrane_source_evidence()
    return {
        "surface_id": PASS209_SURFACE_ID,
        "surface_type": "RUNTIME_GATEWAY",
        "module": "hhs_backend.production_visual_server",
        "symbol": "ProductionRuntimeBootstrapGateway",
        "invariant_ids": ["HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS_RUNTIME_BOOTSTRAP_CACHE_V1", "HHS_RUNTIME_BOOTSTRAP_GATEWAY_V1"],
        "witness_schemas": ["HHS_PASS219_PASS209_RUNTIME_BOOTSTRAP_WITNESS_V1"],
        "validators": [PASS209_BIND_SYMBOL, "RuntimeStatusCache.lookup", "ProductionRuntimeBootstrapGateway.__call__"],
        "guards": [
            "pass209_cache_projection_noncanonical",
            "pass209_isolated_status_probe",
            "pass209_cold_miss_warming_projection",
            "pass209_external_state_roots",
            "pass209_repository_checkout_readonly",
            "pass209_pass210_successor_gate",
        ],
        "rejection_codes": ["INVALID_STATUS_PROXY_PATH", "RUNTIME_STATUS_PENDING"],
        "mutation_policy": "NONCANONICAL_STATUS_PROJECTION_ONLY",
        "persistence_policy": "EXTERNAL_RUNTIME_STATE_ROOTS_ONLY",
        "boundedness_policy": "PASS_209_STATUS_CATALOG_9_SEQUENTIAL_PROBE_V1",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass209_membrane_manifest() -> Dict[str, Any]:
    source = pass209_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS209_NUMBER,
        "classification": PASS209_CLASSIFICATION,
        "pass219_c_abi_surface": PASS209_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass209RuntimeBootstrapGateway",
        "runtime_surface": "ProductionRuntimeBootstrapGateway",
        "required_operations": list(REQUIRED_OPERATIONS),
        "main_merge_head": FROZEN["main_merge_head"],
        "status_catalog_count": len(source["status_catalog"]),
        "persistent_status_cache_bound": True,
        "isolated_sequential_probe_bound": True,
        "cold_miss_warming_projection_bound": True,
        "external_state_roots_bound": True,
        "canonical_backend_authority_preserved": True,
        "cache_projection_noncanonical": True,
        "current_runtime_os_projection": source["current_runtime_os_projection"],
        "pass210_successor_bound": True,
        "pass219_new_canonical_mutation_authority": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "next_pass_to_census": 208,
    }


def preflight_pass209_membrane(*, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    pass209_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    declaration = pass209_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation, cache=decision_cache) for operation in REQUIRED_OPERATIONS]
    return {"schema": "HHS_PASS219_PASS209_PREFLIGHT_V1", "ok": all(row.get("ok") is True for row in rows), "operations": rows}
