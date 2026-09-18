"""Universal Pass 219 Lane 5 interposition for HHS ABI and Linux-host traffic.

This module is an enforcement membrane.  It does not itself own VM81, Hash72,
Hash216, persistence, PQC keys, clocks, or Linux-kernel authority.

Every HHS-controlled runtime/host crossing receives:
- Pass 036 zero-bypass interposition;
- current mandatory Lane 5 capability visibility;
- a BLOCK_DIRECT -> LANE5_REMEDIATION_REQUIRED classification for any
  state-affecting dispatch;
- fail-closed downstream authorization requiring RNA/C++ + signed PQC evidence.

The Linux-host class covers traffic initiated by the HHS runtime/process tree.
It makes no claim over unrelated operating-system processes.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from threading import RLock
from typing import Any, Mapping

from hhs_runtime.hhs_zero_bypass_runtime_interposer_v1 import (
    interpose_runtime_surface,
    verify_interposition_token,
)
from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher import (
    MANDATORY_LANE5_LINEAGE,
    Pass219Lane5LatencyCompositionAgent,
)
from hhs_runtime.pass219.lane5_interceptor_sandbox_cache import (
    BYTE_ORDER as CACHE_BYTE_ORDER,
    RECORD_BYTES as CACHE_RECORD_BYTES,
    SERIAL_BITS as CACHE_SERIAL_BITS,
    default_sandbox_cache,
)

SCHEMA = "HHS_PASS219_UNIVERSAL_ABI_LINUX_KERNEL_LANE5_INTERCEPT_V1"
VERSION = "1.0.0"

TRAFFIC_RUNTIME_ABI = "runtime.abi"
TRAFFIC_LINUX_KERNEL_ABI = "linux.kernel.abi"
TRAFFIC_CTYPES_NATIVE = "native.ctypes"
TRAFFIC_SUBPROCESS_NATIVE = "native.subprocess"
TRAFFIC_FILE_IO = "linux.file.io"
TRAFFIC_SOCKET_IO = "linux.socket.io"
TRAFFIC_VMRC_COMPAT = "vmrc.compatibility"
TRAFFIC_CACHE_REPLAY = "cache.replay.commit"
TRAFFIC_HTTP_API = "api.runtime"
TRAFFIC_WEBSOCKET = "websocket.runtime"
TRAFFIC_PLUGIN = "plugin.runtime"
TRAFFIC_GPU_WORKER = "gpu.worker"

TRAFFIC_CLASSES = (
    TRAFFIC_RUNTIME_ABI,
    TRAFFIC_LINUX_KERNEL_ABI,
    TRAFFIC_CTYPES_NATIVE,
    TRAFFIC_SUBPROCESS_NATIVE,
    TRAFFIC_FILE_IO,
    TRAFFIC_SOCKET_IO,
    TRAFFIC_VMRC_COMPAT,
    TRAFFIC_CACHE_REPLAY,
    TRAFFIC_HTTP_API,
    TRAFFIC_WEBSOCKET,
    TRAFFIC_PLUGIN,
    TRAFFIC_GPU_WORKER,
)

BLOCK_DIRECT = "BLOCK_DIRECT"
REDIRECT_REQUIRED = "LANE5_REMEDIATION_REQUIRED"
OBSERVE_THROUGH_LANE5 = "OBSERVE_THROUGH_LANE5"
ADMIT_DOWNSTREAM = "ADMIT_DOWNSTREAM_AFTER_LANE5_PQC"
REJECT_DOWNSTREAM = "REJECT_DOWNSTREAM_FAIL_CLOSED"

_CAPABILITY_CACHE: dict[str, Any] | None = None
_CAPABILITY_LOCK = RLock()


class Lane5UniversalTrafficError(RuntimeError):
    pass


def _stable(value: Any) -> Any:
    return json.loads(
        json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    )


def _digest(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
        _stable(dict(value)),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(b"HHS-PASS219-UNIVERSAL-ABI-KERNEL-V1\0" + raw).hexdigest()


def _mandatory_capability_snapshot() -> dict[str, Any]:
    global _CAPABILITY_CACHE
    with _CAPABILITY_LOCK:
        if _CAPABILITY_CACHE is not None:
            return dict(_CAPABILITY_CACHE)
        with Pass219Lane5LatencyCompositionAgent() as agent:
            status = dict(agent.status())
        lineage = tuple(status.get("mandatory_lineage") or MANDATORY_LANE5_LINEAGE)
        if not lineage:
            raise Lane5UniversalTrafficError(
                "LANE5_MANDATORY_CAPABILITY_LINEAGE_EMPTY"
            )
        _CAPABILITY_CACHE = {
            "mandatory_lineage": list(lineage),
            "mandatory_lineage_count": len(lineage),
            "dispatcher": "Pass219Lane5LatencyCompositionAgent",
            "mandatory_optimization_dispatch": True,
            "canonical_admission_export": status.get(
                "canonical_admission_export",
                "hhs_exact_pass219_vm81_environment_admit_signed",
            ),
            "raw_environmental_admission_exported": bool(
                status.get("raw_environmental_admission_exported", False)
            ),
            "rlm20_lane5_internal_state_closure": status.get(
                "rlm20_lane5_internal_state_closure"
            ),
        }
        if _CAPABILITY_CACHE["raw_environmental_admission_exported"]:
            raise Lane5UniversalTrafficError(
                "LANE5_RAW_ENVIRONMENTAL_ADMISSION_MUST_REMAIN_HIDDEN"
            )
        return dict(_CAPABILITY_CACHE)


@dataclass(frozen=True)
class Lane5UniversalTrafficEnvelope:
    schema: str
    version: str
    traffic_class: str
    operation: str
    read_only: bool
    state_affecting: bool
    direct_dispatch_action: str
    redirect_action: str
    redirected_through_lane5: bool
    zero_bypass_interposed: bool
    zero_bypass_token_digest72: str
    mandatory_optimization_dispatch: bool
    mandatory_capability_count: int
    mandatory_capability_lineage: tuple[str, ...]
    sandbox_queued: bool
    sandbox_queue_ticket: str
    sandbox_queue_optimized: bool
    sandbox_queue_reordered: bool
    sandbox_cache_hit: bool
    sandbox_cache_capacity_records: int
    sandbox_cache_capacity_bytes: int
    sandbox_cache_calibration: str
    sandbox_cache_production_calibrated: bool
    sandbox_serial_bits: int
    sandbox_record_bytes: int
    sandbox_byte_order: str
    rna_cpp_cell_wall_required: bool
    signed_environmental_pqc_required: bool
    singleton_vm81_required_for_canonical_mutation: bool
    linux_host_result_is_external_evidence: bool
    canonical_mutation_authority: bool
    hash72_authority: bool
    hash216_authority: bool
    canonical_persistence_authority: bool
    pqc_key_authority: bool
    receipt_clock_authority: bool
    floating_point_canonical_authority: bool
    envelope_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def intercept_abi_traffic(
    *,
    traffic_class: str,
    operation: str,
    payload: Mapping[str, Any] | None = None,
    read_only: bool = False,
) -> dict[str, Any]:
    """Intercept every HHS-controlled runtime/Linux-host crossing.

    A state-affecting request is deliberately *not* authorized here.  The
    envelope records BLOCK_DIRECT and requires the downstream Lane5/RNA/PQC
    authorization proof before host/runtime dispatch may occur.
    """
    if traffic_class not in TRAFFIC_CLASSES:
        raise Lane5UniversalTrafficError(
            f"LANE5_UNREGISTERED_TRAFFIC_CLASS:{traffic_class}"
        )
    if not isinstance(operation, str) or not operation.strip():
        raise Lane5UniversalTrafficError("LANE5_OPERATION_REQUIRED")

    state_affecting = not bool(read_only)
    request_payload = {
        "schema": SCHEMA,
        "traffic_class": traffic_class,
        "operation": operation,
        "read_only": bool(read_only),
        "state_affecting": state_affecting,
        "payload": _stable(dict(payload or {})),
    }
    interposed = interpose_runtime_surface(
        surface=traffic_class,
        request_class="canonical_full_witness_chain",
        payload=request_payload,
    )
    if interposed.get("propagation_allowed") is not True:
        raise Lane5UniversalTrafficError(
            "LANE5_ZERO_BYPASS_INTERPOSITION_REJECTED:"
            + str(interposed.get("status"))
        )
    token = dict(interposed.get("interposition_token") or {})
    token_check = verify_interposition_token(token, surface=traffic_class)
    if token_check.get("ok") is not True:
        raise Lane5UniversalTrafficError(
            "LANE5_ZERO_BYPASS_TOKEN_INVALID:"
            + str(token_check.get("status"))
        )

    caps = _mandatory_capability_snapshot()
    sandbox = default_sandbox_cache()
    queue_enqueue = sandbox.enqueue(
        traffic_class=traffic_class,
        operation=operation,
        payload=dict(payload or {}),
        read_only=bool(read_only),
    )
    queue_optimized = sandbox.optimize_until(str(queue_enqueue["ticket"]))
    sandbox_status = sandbox.status()
    body = {
        "schema": SCHEMA,
        "version": VERSION,
        "traffic_class": traffic_class,
        "operation": operation,
        "read_only": bool(read_only),
        "state_affecting": state_affecting,
        "direct_dispatch_action": (
            OBSERVE_THROUGH_LANE5 if read_only else BLOCK_DIRECT
        ),
        "redirect_action": (
            OBSERVE_THROUGH_LANE5 if read_only else REDIRECT_REQUIRED
        ),
        "redirected_through_lane5": True,
        "zero_bypass_interposed": True,
        "zero_bypass_token_digest72": str(token.get("token_digest72") or ""),
        "mandatory_optimization_dispatch": bool(
            caps["mandatory_optimization_dispatch"]
        ),
        "mandatory_capability_count": int(caps["mandatory_lineage_count"]),
        "mandatory_capability_lineage": tuple(caps["mandatory_lineage"]),
        "sandbox_queued": bool(queue_enqueue.get("queued")),
        "sandbox_queue_ticket": str(queue_enqueue.get("ticket") or ""),
        "sandbox_queue_optimized": bool(
            queue_optimized.get("lane5_queue_optimized")
        ),
        "sandbox_queue_reordered": bool(
            queue_optimized.get("lane5_reordered")
        ),
        "sandbox_cache_hit": bool(queue_optimized.get("cache_hit")),
        "sandbox_cache_capacity_records": int(
            sandbox_status["capacity_records"]
        ),
        "sandbox_cache_capacity_bytes": int(
            sandbox_status["capacity_bytes"]
        ),
        "sandbox_cache_calibration": str(
            sandbox_status["calibration"]["classification"]
        ),
        "sandbox_cache_production_calibrated": bool(
            sandbox_status["production_calibrated"]
        ),
        "sandbox_serial_bits": CACHE_SERIAL_BITS,
        "sandbox_record_bytes": CACHE_RECORD_BYTES,
        "sandbox_byte_order": CACHE_BYTE_ORDER,
        "rna_cpp_cell_wall_required": state_affecting,
        "signed_environmental_pqc_required": state_affecting,
        "singleton_vm81_required_for_canonical_mutation": state_affecting,
        "linux_host_result_is_external_evidence": (
            traffic_class
            in {
                TRAFFIC_LINUX_KERNEL_ABI,
                TRAFFIC_SUBPROCESS_NATIVE,
                TRAFFIC_FILE_IO,
                TRAFFIC_SOCKET_IO,
            }
        ),
        "canonical_mutation_authority": False,
        "hash72_authority": False,
        "hash216_authority": False,
        "canonical_persistence_authority": False,
        "pqc_key_authority": False,
        "receipt_clock_authority": False,
        "floating_point_canonical_authority": False,
    }
    envelope = Lane5UniversalTrafficEnvelope(
        **body,
        envelope_sha256=_digest(body),
    )
    return {
        "envelope": envelope.to_dict(),
        "zero_bypass": interposed,
        "capability_snapshot": caps,
        "queue_enqueue": queue_enqueue,
        "queue_optimization": queue_optimized,
        "sandbox_status": sandbox_status,
    }


def authorize_downstream_dispatch(
    intercept_record: Mapping[str, Any],
    *,
    lane5_receipt: Mapping[str, Any] | None = None,
    pqc_receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Authorize the *downstream* runtime/Linux dispatch after mediation.

    Read-only traffic needs the valid universal envelope only.  State-affecting
    traffic additionally requires explicit Lane5/RNA and signed-PQC evidence.
    """
    envelope = dict(intercept_record.get("envelope") or {})
    if envelope.get("schema") != SCHEMA:
        raise Lane5UniversalTrafficError("LANE5_INTERCEPT_ENVELOPE_REQUIRED")
    traffic_class = str(envelope.get("traffic_class") or "")
    if traffic_class not in TRAFFIC_CLASSES:
        raise Lane5UniversalTrafficError("LANE5_INTERCEPT_TRAFFIC_CLASS_DRIFT")
    if envelope.get("redirected_through_lane5") is not True:
        raise Lane5UniversalTrafficError("LANE5_REDIRECT_PROOF_REQUIRED")
    if envelope.get("zero_bypass_interposed") is not True:
        raise Lane5UniversalTrafficError("LANE5_ZERO_BYPASS_PROOF_REQUIRED")
    if envelope.get("mandatory_optimization_dispatch") is not True:
        raise Lane5UniversalTrafficError(
            "LANE5_MANDATORY_OPTIMIZATION_PROOF_REQUIRED"
        )
    if envelope.get("sandbox_queued") is not True:
        raise Lane5UniversalTrafficError("LANE5_SANDBOX_QUEUE_PROOF_REQUIRED")
    if envelope.get("sandbox_queue_optimized") is not True:
        raise Lane5UniversalTrafficError(
            "LANE5_SANDBOX_QUEUE_OPTIMIZATION_REQUIRED"
        )
    if envelope.get("sandbox_serial_bits") != CACHE_SERIAL_BITS:
        raise Lane5UniversalTrafficError("LANE5_SANDBOX_SERIAL_WIDTH_DRIFT")
    if envelope.get("sandbox_record_bytes") != CACHE_RECORD_BYTES:
        raise Lane5UniversalTrafficError("LANE5_SANDBOX_RECORD_WIDTH_DRIFT")
    if envelope.get("sandbox_byte_order") != CACHE_BYTE_ORDER:
        raise Lane5UniversalTrafficError("LANE5_SANDBOX_BYTE_ORDER_DRIFT")
    if any(
        envelope.get(key) is not False
        for key in (
            "canonical_mutation_authority",
            "hash72_authority",
            "hash216_authority",
            "canonical_persistence_authority",
            "pqc_key_authority",
            "receipt_clock_authority",
            "floating_point_canonical_authority",
        )
    ):
        raise Lane5UniversalTrafficError("LANE5_INTERCEPT_AUTHORITY_ESCALATION")

    if envelope.get("read_only") is True:
        return {
            "schema": "HHS_PASS219_UNIVERSAL_ABI_KERNEL_DISPATCH_DECISION_V1",
            "decision": ADMIT_DOWNSTREAM,
            "traffic_class": traffic_class,
            "read_only": True,
            "canonical_mutation_allowed": False,
            "pqc_required": False,
            "sandbox_queue_optimized": True,
            "sandbox_queue_reordered": bool(
                envelope.get("sandbox_queue_reordered")
            ),
            "sandbox_cache_hit": bool(envelope.get("sandbox_cache_hit")),
            "lane5_intercept_sha256": envelope.get("envelope_sha256"),
        }

    lane5 = dict(lane5_receipt or {})
    pqc = dict(pqc_receipt or {})
    lane5_ok = (
        lane5.get("lane5_mediation_verified") is True
        and lane5.get("mandatory_optimization_dispatch") is True
        and lane5.get("rna_cpp_cell_wall_routed") is True
        and lane5.get("candidate_only") is True
    )
    pqc_ok = (
        pqc.get("signed_environmental_admission") is True
        and pqc.get("pqc_authenticated") is True
        and pqc.get("decision") == "ADMIT"
        and pqc.get("singleton_vm81_authority") is True
    )
    if not lane5_ok:
        raise Lane5UniversalTrafficError(
            "LANE5_DOWNSTREAM_BLOCKED_MISSING_MEDIATION"
        )
    if not pqc_ok:
        raise Lane5UniversalTrafficError(
            "LANE5_DOWNSTREAM_BLOCKED_MISSING_SIGNED_PQC"
        )

    return {
        "schema": "HHS_PASS219_UNIVERSAL_ABI_KERNEL_DISPATCH_DECISION_V1",
        "decision": ADMIT_DOWNSTREAM,
        "traffic_class": traffic_class,
        "read_only": False,
        "canonical_mutation_allowed": True,
        "pqc_required": True,
        "sandbox_queue_optimized": True,
        "sandbox_queue_reordered": bool(
            envelope.get("sandbox_queue_reordered")
        ),
        "sandbox_cache_hit": bool(envelope.get("sandbox_cache_hit")),
        "lane5_intercept_sha256": envelope.get("envelope_sha256"),
        "lane5_receipt_sha256": _digest(lane5),
        "pqc_receipt_sha256": _digest(pqc),
    }


def direct_dispatch_rejection(
    *,
    traffic_class: str,
    operation: str,
) -> dict[str, Any]:
    """Explicit block record for a caller that tries to skip Lane 5."""
    if traffic_class not in TRAFFIC_CLASSES:
        raise Lane5UniversalTrafficError(
            f"LANE5_UNREGISTERED_TRAFFIC_CLASS:{traffic_class}"
        )
    sandbox = default_sandbox_cache()
    queued = sandbox.enqueue(
        traffic_class=traffic_class,
        operation=operation,
        payload={
            "schema": "HHS_PASS219_DIRECT_BYPASS_REDIRECT_V1",
            "bypass_attempt": True,
        },
        read_only=False,
    )
    optimized = sandbox.optimize_until(str(queued["ticket"]))
    return {
        "schema": "HHS_PASS219_UNIVERSAL_ABI_KERNEL_DIRECT_BLOCK_V1",
        "traffic_class": traffic_class,
        "operation": operation,
        "decision": REJECT_DOWNSTREAM,
        "pqc_boundary_action": BLOCK_DIRECT,
        "redirect_action": REDIRECT_REQUIRED,
        "direct_fallback_allowed": False,
        "canonical_mutation_allowed": False,
        "sandbox_queued": True,
        "sandbox_queue_ticket": queued["ticket"],
        "sandbox_queue_optimized": bool(
            optimized.get("lane5_queue_optimized")
        ),
        "sandbox_queue_reordered": bool(
            optimized.get("lane5_reordered")
        ),
    }


def audit_runtime_kernel_crossings(root: str | Path | None = None) -> dict[str, Any]:
    """Inventory direct runtime/kernel crossings requiring repair.

    This is deliberately a detector, not an automatic source rewriter.
    """
    repo = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]
    scan_roots = (
        repo / "hhs_backend",
        repo / "hhs_runtime",
        repo / "hhs_python",
    )
    patterns = {
        ".execute(candidate)": "DIRECT_VMRC_EXECUTE",
        "commit_retrieved_snapshot(": "DIRECT_RETRIEVAL_COMMIT",
        "ctypes.CDLL(": "DIRECT_CTYPES_DLOPEN",
        "subprocess.run(": "DIRECT_SUBPROCESS_RUN",
        "subprocess.Popen(": "DIRECT_SUBPROCESS_POPEN",
        "os.system(": "DIRECT_OS_SYSTEM",
        ".socket(": "DIRECT_SOCKET_OPEN",
    }
    exempt_paths = {
        Path("hhs_runtime/pass219/lane5_universal_abi_kernel_interceptor.py"),
    }
    findings: list[dict[str, Any]] = []
    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for path in sorted(scan_root.rglob("*.py")):
            rel = path.relative_to(repo)
            if rel in exempt_paths:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for needle, classification in patterns.items():
                start = 0
                while True:
                    index = text.find(needle, start)
                    if index < 0:
                        break
                    line = text.count("\n", 0, index) + 1
                    findings.append(
                        {
                            "path": str(rel),
                            "line": line,
                            "pattern": needle,
                            "classification": classification,
                            "lane5_intercept_marker_present": (
                                "lane5_universal_abi_kernel_interceptor"
                                in text
                                or "intercept_abi_traffic" in text
                            ),
                        }
                    )
                    start = index + len(needle)
    unmediated = [
        item for item in findings if not item["lane5_intercept_marker_present"]
    ]
    return {
        "schema": "HHS_PASS219_UNIVERSAL_ABI_KERNEL_AUDIT_V1",
        "finding_count": len(findings),
        "unmediated_count": len(unmediated),
        "findings": findings,
        "unmediated": unmediated,
        "production_acceptance": len(unmediated) == 0,
    }


__all__ = [
    "SCHEMA",
    "VERSION",
    "TRAFFIC_CLASSES",
    "TRAFFIC_RUNTIME_ABI",
    "TRAFFIC_LINUX_KERNEL_ABI",
    "TRAFFIC_CTYPES_NATIVE",
    "TRAFFIC_SUBPROCESS_NATIVE",
    "TRAFFIC_FILE_IO",
    "TRAFFIC_SOCKET_IO",
    "TRAFFIC_VMRC_COMPAT",
    "TRAFFIC_CACHE_REPLAY",
    "TRAFFIC_HTTP_API",
    "TRAFFIC_WEBSOCKET",
    "TRAFFIC_PLUGIN",
    "TRAFFIC_GPU_WORKER",
    "Lane5UniversalTrafficError",
    "intercept_abi_traffic",
    "authorize_downstream_dispatch",
    "direct_dispatch_rejection",
    "audit_runtime_kernel_crossings",
]
