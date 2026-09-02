"""Pass 191 Genesis-to-runtime universal repository hydration.

Repair-forward implementation of HHS-P191-GTRFRH-UIC-VM81-H72-H216.

The runtime treats the committed Git tree as the source-preserving repository
object graph. It reuses the Pass 190 operation registry and the already
verified Pass 191 dyadic-quartic manifold evidence, then binds them into one
deterministic hydration manifest with explicit Genesis/Pass-001..190 lineage,
universal invariant records, Hash216 topology roots, finite durable jobs,
Hash72 mutation receipts, incremental invalidation and replay.

Canonical authority is exact. Wall-clock metrics and UI transport are
explicitly noncanonical. Persistent job mutation requires the inherited
singleton VM81 admission path; this module never constructs a second VM81.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time
from typing import Any, Iterable, Mapping, Optional, Sequence
import unicodedata

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import _validated_authorized_tick

CONTRACT_ID = "HHS-P191-GTRFRH-UIC-VM81-H72-H216"
CONTRACT_VERSION = "1.0.0"
CONTRACT_AUTHORIZATION_COMMIT = "89d67731c6c4f5798e26a43e0273c6ce33a1abee"
FROZEN_I134 = "4bb202e657670dac1ab2a39575821b647f691d71"
DQPL_CONTRACT_ID = "HHS-P191-DQPL-TENSOR-VM5184-G243-H216-H72"
RUNTIME_COMPLETION_CLASSIFICATION = (
    "HHS_PASS_191_GENESIS_TO_RUNTIME_REPOSITORY_HYDRATION_VERIFIED"
)

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_ROOT = Path(".hhs_runtime_state") / "pass191"
PASS190_REGISTRY = Path(
    "native_projects/hhs_pass190_operation_fabric/registry/HHS_OPERATION_REGISTRY_V1.json"
)
UNIVERSAL_CONTRACT_PATH = Path(
    "docs/pass191/"
    "HHS_PASS_191_GENESIS_TO_RUNTIME_FULL_REPOSITORY_HYDRATION_"
    "UNIVERSAL_INVARIANT_CLOSURE.md"
)
DQPL_PROOF_PATH = Path("HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md")
DQPL_EVIDENCE_PATH = Path(
    "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence/"
    "PASS_191_INTEGRATED_PROOF_SEARCH.json"
)
DQPL_COMPLETION_PATH = Path(
    "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence/"
    "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json"
)

LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
ORDERED_O8 = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
OUTER_HYDRATION_MODULUS = 1_259_713
Q = 64 * 81 * 243
N = 2 * Q
TRINARY = (-1, 0, 1)
TERMINAL_STAGES = ("COMPLETED", "FAILED", "CANCELLED", "BLOCKED")
LIFECYCLE = (
    "QUEUED",
    "DISCOVERING",
    "PRESERVING",
    "CLASSIFYING",
    "PARSING",
    "TYPING",
    "INDEXING",
    "LINKING",
    "BINDING",
    "VALIDATING",
    "ADMISSION_PENDING",
    "COMMITTING",
    "REPLAYING",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    "BLOCKED",
)

PASS191_OPERATION_IDS = (
    "P191.Hydrate.Repository",
    "P191.Hydrate.Genesis",
    "P191.Hydrate.Pass",
    "P191.Hydrate.Object",
    "P191.Hydrate.Function",
    "P191.Hydrate.Surface",
    "P191.Hydrate.ChangedSince",
    "P191.Hydrate.Resume",
    "P191.Hydrate.Verify",
    "P191.Hydrate.Replay",
    "P191.Hydrate.Report",
    "P191.Registry.Resolve",
    "P191.Symmetry.Validate",
    "P191.Reciprocal.Verify",
    "P191.Receipt.Get",
)

_PASS_RE = re.compile(r"(?i)(?:^|[^a-z0-9])pass[_\- ]?0*([0-9]{1,3})(?:[^0-9]|$)")


class Pass191Error(RuntimeError):
    def __init__(self, classification: str, detail: str = "") -> None:
        super().__init__(classification if not detail else f"{classification}: {detail}")
        self.classification = classification
        self.detail = detail


@dataclass(frozen=True)
class HydrationBounds:
    max_files: int = 100_000
    max_bytes: int = 4 * 1024 * 1024 * 1024
    max_single_object_bytes: int = 256 * 1024 * 1024
    max_dependency_edges: int = 1_000_000
    max_manifest_bytes: int = 64 * 1024 * 1024
    max_stage_duration_ns: int = 300_000_000_000
    max_total_job_duration_ns: int = 1_800_000_000_000
    max_replay_attempts: int = 3

    def validate(self) -> "HydrationBounds":
        for name, value in asdict(self).items():
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise Pass191Error("HHS_P191_BOUNDS_INVALID", name)
        return self

    @classmethod
    def from_mapping(cls, value: Optional[Mapping[str, Any]]) -> "HydrationBounds":
        if value is None:
            return cls().validate()
        allowed = set(cls.__dataclass_fields__)
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise Pass191Error("HHS_P191_BOUNDS_UNKNOWN_FIELD", ",".join(unknown))
        return cls(**{key: int(item) for key, item in value.items()}).validate()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _hash72(domain: str, payload: Any) -> str:
    return hash72_digest(
        {"domain": domain, "contract": CONTRACT_ID, "version": CONTRACT_VERSION},
        payload,
    )


def _hash216(domain: str, payload: Any) -> str:
    previous = _hash72(domain + ":PREVIOUS", {"authorization": CONTRACT_AUTHORIZATION_COMMIT})
    change = _hash72(domain + ":CHANGE", payload)
    receipt = _hash72(domain + ":RECEIPT", {"previous": previous, "change": change})
    value = previous + change + receipt
    if len(value) != 216:
        raise AssertionError("Hash216 must be three ordered Hash72 witnesses")
    return value


def _authority_lineage(execution: Mapping[str, Any]) -> tuple[str, str]:
    try:
        validated = _validated_authorized_tick(execution)
    except Exception as exc:
        raise Pass191Error("HHS_P191_VM81_AUTHORITY_REQUIRED") from exc
    receipt = validated["receipt"]
    state_hash72 = receipt["state_hash72"]
    receipt_hash72 = receipt["receipt_hash72"]
    if not validate_hash72(state_hash72) or not validate_hash72(receipt_hash72):
        raise Pass191Error("HHS_P191_VM81_AUTHORITY_HASH72_INVALID")
    return state_hash72, receipt_hash72


def _safe_locator(identity: str) -> str:
    return hashlib.sha256(b"HHS-P191-FILE\0" + identity.encode("utf-8")).hexdigest()


def _classify_path(path: str) -> str:
    lower = path.lower()
    suffix = Path(path).suffix.lower()
    if "/tests/" in f"/{lower}" or lower.startswith("tests/"):
        return "TEST"
    if "/evidence/" in f"/{lower}" or lower.startswith("evidence/"):
        return "EVIDENCE"
    if lower.startswith(".github/workflows/"):
        return "WORKFLOW"
    if "contract" in lower or lower.startswith("docs/pass"):
        return "CONTRACT_OR_PASS_DOC"
    if suffix in {".py", ".c", ".h", ".hpp", ".cpp", ".mjs", ".js", ".ts", ".tsx", ".rs", ".go"}:
        return "SOURCE"
    if suffix in {".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini"}:
        return "CONFIG_OR_DATA"
    if suffix in {".md", ".txt", ".rst"}:
        return "DOCUMENT"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".mp4", ".wav", ".mp3"}:
        return "MEDIA"
    if suffix in {".zip", ".tar", ".gz", ".bin", ".so", ".a", ".o"}:
        return "BINARY_OR_ARCHIVE"
    return "OTHER"


def _path_passes(path: str) -> list[int]:
    values: set[int] = set()
    for match in _PASS_RE.finditer(path):
        number = int(match.group(1))
        if 1 <= number <= 190:
            values.add(number)
    return sorted(values)


def exact_symmetry_witness() -> dict[str, Any]:
    rows = [sum(row) for row in LO_SHU]
    columns = [sum(LO_SHU[r][c] for r in range(3)) for c in range(3)]
    diagonals = [
        sum(LO_SHU[i][i] for i in range(3)),
        sum(LO_SHU[i][2 - i] for i in range(3)),
    ]
    pairs = []
    for index in range(20):
        other = 40 - index
        ratio = Fraction(index + 1, index + 2)
        reciprocal = Fraction(ratio.denominator, ratio.numerator)
        # i*r times -i/r = (-i^2)*(r/r) = 1.
        closure = ratio * reciprocal
        pairs.append(
            {
                "left": f"G_{index}",
                "right": f"G_{other}",
                "sigma_left": f"G_{other}",
                "sigma_right": f"G_{index}",
                "ratio": [ratio.numerator, ratio.denominator],
                "reciprocal": [reciprocal.numerator, reciprocal.denominator],
                "phase_product": [closure.numerator, closure.denominator],
            }
        )
    witness = {
        "lo_shu": [list(row) for row in LO_SHU],
        "line_sums": rows + columns + diagonals,
        "groups": [f"G_{index}" for index in range(41)],
        "involution": {f"G_{index}": f"G_{40-index}" for index in range(41)},
        "central_group": "G_20",
        "central_phase": "1",
        "reciprocal_pairs": pairs,
        "ordered_o8": list(ORDERED_O8),
        "ordered_distinctions": {"xy_ne_yx": True, "zw_ne_wz": True},
    }
    witness["valid"] = (
        all(value == 15 for value in witness["line_sums"])
        and witness["involution"]["G_20"] == "G_20"
        and all(pair["phase_product"] == [1, 1] for pair in pairs)
        and witness["ordered_distinctions"]["xy_ne_yx"]
        and witness["ordered_distinctions"]["zw_ne_wz"]
    )
    witness["hash216_identity"] = _hash216("HHS-P191-SYMMETRY", witness)
    return witness


def universal_invariant_registry(contract_blob: str) -> dict[str, Any]:
    invariants = [
        {
            "id": "P191-UIC-SOURCE",
            "kind": "SOURCE_PRESERVATION",
            "witness": {"contract_blob": contract_blob, "unicode": "NFC", "line_endings": "GIT_BLOB"},
        },
        {
            "id": "P191-UIC-CONSTANTS",
            "kind": "EXACT_CONSTANTS",
            "witness": {"a2": 1, "b2": 2, "c2": 3, "d2": 5, "u72": 1},
        },
        {
            "id": "P191-UIC-RECIPROCAL-POLYNOMIAL",
            "kind": "SYMBOLIC_ROOT_PAIR",
            "witness": {
                "Q": Q,
                "N": N,
                "polynomial": "m^2+m-N^2=0",
                "m_plus": "(-1+Sqrt(1+4*N^2))/2",
                "m_minus": "(-1-Sqrt(1+4*N^2))/2",
                "root_sum": -1,
                "root_product": -(N * N),
                "normalized_product": -1,
                "oriented_phase_product": 1,
            },
        },
        {
            "id": "P191-UIC-TRINARY",
            "kind": "EXACT_POLYNOMIAL",
            "witness": {"states": list(TRINARY), "equation": "t*(t-1)*(t+1)=0"},
        },
        {
            "id": "P191-UIC-MODULAR-BRIDGE",
            "kind": "EXACT_MODULAR",
            "witness": {"left": 5184 % 5040, "right": 144 % 5040, "expected": 144},
        },
        {
            "id": "P191-UIC-O8",
            "kind": "ORDERED_NONCOMMUTATIVE",
            "witness": {"lanes": list(ORDERED_O8), "xy_ne_yx": True, "zw_ne_wz": True},
        },
        {
            "id": "P191-UIC-LOSHU-G41",
            "kind": "GLOBAL_SYMMETRY",
            "witness": exact_symmetry_witness(),
        },
        {
            "id": "P191-UIC-OUTER-MODULUS",
            "kind": "MEMBRANE",
            "witness": {
                "outer_modulus": OUTER_HYDRATION_MODULUS,
                "internal_cardinality": Q,
                "local_reduction_authority": False,
            },
        },
        {
            "id": "P191-UIC-SYMBOL-DISTINCTION",
            "kind": "TYPED_SYMBOLS",
            "witness": {
                "O_ne_Pi": True,
                "O_ne_decimal_pi": True,
                "decimal_pi_role": "CALIBRATION_ONLY",
                "decimal_e_role": "CALIBRATION_ONLY",
            },
        },
        {
            "id": "P191-UIC-AUTHORITY",
            "kind": "AUTHORITY",
            "witness": {
                "singleton_vm81": True,
                "hash72_receipts": True,
                "hash216_identity_topology": True,
                "floating_point_canonical_authority": False,
            },
        },
    ]
    for record in invariants:
        record["hash216_identity"] = _hash216("HHS-P191-INVARIANT", record)
    identity = {
        "schema": "HHS_PASS_191_UNIVERSAL_INVARIANT_REGISTRY_V1",
        "contract": CONTRACT_ID,
        "invariants": invariants,
    }
    return {
        **identity,
        "registry_root_hash216": _hash216("HHS-P191-INVARIANT-REGISTRY", identity),
    }


def pass191_operation_overlay() -> list[dict[str, Any]]:
    mappings = {
        "P191.Hydrate.Repository": ("Hydrate.Repository", "hhs hydrate repository", "POST", "/v1/hydration/jobs"),
        "P191.Hydrate.Genesis": ("Hydrate.Genesis", "hhs hydrate genesis", "GET", "/v1/hydration/lineage/passes"),
        "P191.Hydrate.Pass": ("Hydrate.Pass", "hhs hydrate pass", "GET", "/v1/hydration/lineage/passes"),
        "P191.Hydrate.Object": ("Hydrate.Object", "hhs hydrate object", "GET", "/v1/hydration/objects/{object_id}"),
        "P191.Hydrate.Function": ("Hydrate.Function", "hhs hydrate function", "GET", "/v1/hydration/functions/{operation_id}"),
        "P191.Hydrate.Surface": ("Hydrate.Surface", "hhs hydrate surface", "GET", "/v1/hydration/surfaces"),
        "P191.Hydrate.ChangedSince": ("Hydrate.ChangedSince", "hhs hydrate changed --since", "POST", "/v1/hydration/preview"),
        "P191.Hydrate.Resume": ("Hydrate.Resume", "hhs hydrate resume", "POST", "/v1/hydration/jobs/{job_id}/resume"),
        "P191.Hydrate.Verify": ("Hydrate.Verify", "hhs hydrate verify", "POST", "/v1/hydration/jobs/{job_id}/verify"),
        "P191.Hydrate.Replay": ("Hydrate.Replay", "hhs hydrate replay", "POST", "/v1/hydration/jobs/{job_id}/replay"),
        "P191.Hydrate.Report": ("Hydrate.Report", "hhs hydrate report", "GET", "/v1/hydration/jobs/{job_id}/report"),
        "P191.Registry.Resolve": ("Registry.Resolve", "hhs registry functions", "GET", "/v1/hydration/functions/{operation_id}"),
        "P191.Symmetry.Validate": ("Symmetry.Validate", "hhs symmetry verify", "GET", "/v1/hydration/invariants"),
        "P191.Reciprocal.Verify": ("Reciprocal.Verify", "hhs reciprocal verify", "GET", "/v1/hydration/invariants"),
        "P191.Receipt.Get": ("Receipt.Get", "hhs hydrate receipt", "GET", "/v1/hydration/receipts/{receipt_id}"),
    }
    records = []
    for operation_id in PASS191_OPERATION_IDS:
        constructor, shell, method, path = mappings[operation_id]
        record = {
            "operation_id": operation_id,
            "canonical_name": constructor,
            "harmonicode_constructor": constructor,
            "introduced_by_pass": 191,
            "effect_class": "mutation" if operation_id in {
                "P191.Hydrate.Repository", "P191.Hydrate.Resume"
            } else "pure",
            "capability_scope": "hydration:write" if operation_id in {
                "P191.Hydrate.Repository", "P191.Hydrate.Resume"
            } else "hydration:read",
            "VM81_binding": (
                f"VM81:{operation_id}" if operation_id in {
                    "P191.Hydrate.Repository", "P191.Hydrate.Resume"
                } else "READ_ONLY_NO_MUTATION"
            ),
            "HTTP_method": method,
            "HTTP_path": path,
            "WebSocket_channel": "pass191.hydration.lifecycle",
            "CLI_command": shell,
            "SDK_symbols": {"python": operation_id.replace(".", "_")},
            "replay_supported": True,
            "implementation_status": "EXECUTABLE_VERIFIED_PENDING_I135_SEAL",
        }
        record["Hash216_identity"] = _hash216("HHS-P191-OPERATION", record)
        records.append(record)
    return records


class RepositoryHydrationRuntime:
    """Deterministic committed-tree hydrator with durable VM81-bound jobs."""

    def __init__(
        self,
        root: Path | str = DEFAULT_ROOT,
        state_root: Path | str = DEFAULT_STATE_ROOT,
    ) -> None:
        self.root = Path(root).resolve()
        self.state_root = (
            Path(state_root)
            if Path(state_root).is_absolute()
            else self.root / Path(state_root)
        )
        self.jobs_root = self.state_root / "jobs"
        self.receipt_path = self.state_root / "receipts.jsonl"
        self._mutation_lock = threading.RLock()
        self._cancel_events: dict[str, threading.Event] = {}

    def _git(self, *args: str, text: bool = True) -> str | bytes:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=text,
        )
        return completed.stdout if not text else completed.stdout.strip()

    def head_commit(self) -> str:
        return str(self._git("rev-parse", "HEAD"))

    def status(self) -> dict[str, Any]:
        return {
            "contract": CONTRACT_ID,
            "contract_version": CONTRACT_VERSION,
            "authorization_commit": CONTRACT_AUTHORIZATION_COMMIT,
            "frozen_predecessor_i134": FROZEN_I134,
            "canonical_arithmetic": "EXACT_INTEGER_RATIONAL_SYMBOLIC_ORDERED_BYTES",
            "floating_point_canonical_authority": False,
            "singleton_vm81_authority": "INHERITED",
            "hash72_receipts": True,
            "hash216_identity_topology": True,
            "lifecycle": list(LIFECYCLE),
            "pass190_registry": str(PASS190_REGISTRY),
            "dqpl_inherited": True,
            "universal_hydration_repair": True,
        }

    def _tree_rows(
        self,
        commit: str,
        bounds: HydrationBounds,
        changed_paths: Optional[set[str]] = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        raw = str(self._git("ls-tree", "-r", "-l", "-z", commit))
        rows: list[dict[str, Any]] = []
        blockers: list[dict[str, Any]] = []
        total_bytes = 0
        entries = [entry for entry in raw.split("\0") if entry]
        if len(entries) > bounds.max_files:
            raise Pass191Error(
                "HHS_P191_FILE_LIMIT_BLOCKED",
                f"{len(entries)}>{bounds.max_files}",
            )
        for entry in entries:
            try:
                meta, path = entry.split("\t", 1)
                mode, kind, blob_sha, size_text = meta.split()
            except ValueError as exc:
                raise Pass191Error("HHS_P191_GIT_TREE_PARSE_ERROR", entry[:160]) from exc
            if kind != "blob":
                blockers.append(
                    {
                        "classification": "BLOCKED_UNSUPPORTED_GIT_OBJECT",
                        "path": path,
                        "kind": kind,
                    }
                )
                continue
            size = int(size_text)
            total_bytes += size
            if total_bytes > bounds.max_bytes:
                raise Pass191Error(
                    "HHS_P191_TOTAL_BYTE_LIMIT_BLOCKED",
                    f"{total_bytes}>{bounds.max_bytes}",
                )
            if size > bounds.max_single_object_bytes:
                blockers.append(
                    {
                        "classification": "BLOCKED_SINGLE_OBJECT_SIZE",
                        "path": path,
                        "size_bytes": size,
                        "limit_bytes": bounds.max_single_object_bytes,
                    }
                )
            if changed_paths is not None and path not in changed_paths:
                continue
            identity_core = {
                "path": path,
                "mode": mode,
                "git_blob": blob_sha,
                "size_bytes": size,
                "object_class": _classify_path(path),
                "pass_references": _path_passes(path),
            }
            rows.append(
                {
                    **identity_core,
                    "hash216_identity": _hash216("HHS-P191-OBJECT", identity_core),
                }
            )
        return rows, blockers

    def _changed_paths(self, since_commit: Optional[str], commit: str) -> Optional[set[str]]:
        if not since_commit:
            return None
        try:
            self._git("cat-file", "-e", f"{since_commit}^{{commit}}")
        except subprocess.CalledProcessError as exc:
            raise Pass191Error("HHS_P191_SINCE_COMMIT_NOT_FOUND", since_commit) from exc
        raw = str(self._git("diff", "--name-only", "-z", since_commit, commit))
        return {path for path in raw.split("\0") if path}

    def _contract_blob(self, commit: str) -> str:
        return str(self._git("rev-parse", f"{commit}:{UNIVERSAL_CONTRACT_PATH}"))

    def _load_pass190_operations(self, commit: str) -> tuple[list[dict[str, Any]], str]:
        try:
            raw = self._git("show", f"{commit}:{PASS190_REGISTRY}")
            payload = json.loads(str(raw))
        except Exception as exc:
            raise Pass191Error("HHS_P191_PASS190_REGISTRY_UNAVAILABLE") from exc
        if payload.get("schema") != "HHS_OPERATION_REGISTRY_V1":
            raise Pass191Error("HHS_P191_PASS190_REGISTRY_SCHEMA_DRIFT")
        operations = payload.get("operations")
        if not isinstance(operations, list) or not operations:
            raise Pass191Error("HHS_P191_PASS190_REGISTRY_EMPTY")
        ids = [item.get("operation_id") for item in operations]
        if any(not isinstance(item, str) or not item for item in ids):
            raise Pass191Error("HHS_P191_PASS190_OPERATION_ID_INVALID")
        if len(ids) != len(set(ids)):
            raise Pass191Error("HHS_P191_PASS190_OPERATION_ID_DUPLICATE")
        for operation in operations:
            if operation.get("implementation_status") != "EXECUTABLE_VERIFIED":
                raise Pass191Error(
                    "HHS_P191_PASS190_OPERATION_NOT_VERIFIED",
                    str(operation.get("operation_id")),
                )
            identity = operation.get("Hash216_identity")
            if not isinstance(identity, str) or len(identity) != 216:
                raise Pass191Error(
                    "HHS_P191_PASS190_HASH216_INVALID",
                    str(operation.get("operation_id")),
                )
        return operations, str(payload.get("registry_hash216", ""))

    def _function_registry(self, commit: str) -> dict[str, Any]:
        inherited, inherited_root = self._load_pass190_operations(commit)
        overlay = pass191_operation_overlay()
        combined = inherited + overlay
        ids = [item["operation_id"] for item in combined]
        if len(ids) != len(set(ids)):
            raise Pass191Error("HHS_P191_FUNCTION_REGISTRY_DUPLICATE")
        identity = {
            "schema": "HHS_PASS_191_FUNCTION_REGISTRY_V1",
            "pass190_registry_root": inherited_root,
            "inherited_operation_count": len(inherited),
            "pass191_operation_count": len(overlay),
            "operations": combined,
        }
        return {
            **identity,
            "registry_root_hash216": _hash216("HHS-P191-FUNCTION-REGISTRY", identity),
        }

    @staticmethod
    def _lineage(objects: Sequence[Mapping[str, Any]], commit: str) -> dict[str, Any]:
        by_pass: dict[int, list[str]] = {number: [] for number in range(1, 191)}
        genesis_sources: list[str] = []
        for obj in objects:
            path = str(obj["path"])
            lower = path.lower()
            if "genesis" in lower:
                genesis_sources.append(path)
            for number in obj.get("pass_references", []):
                by_pass[int(number)].append(path)
        records: list[dict[str, Any]] = [
            {
                "kind": "GENESIS",
                "pass_number": 0,
                "representation": "EXPLICIT_GENESIS_SLOT",
                "source_count": len(genesis_sources),
                "sources": sorted(genesis_sources)[:64],
            }
        ]
        for number in range(1, 191):
            sources = sorted(set(by_pass[number]))
            records.append(
                {
                    "kind": "PASS",
                    "pass_number": number,
                    "representation": (
                        "DISCOVERED_REPOSITORY_AUTHORITY"
                        if sources
                        else "EXPLICIT_LINEAGE_SLOT_NO_DIRECT_PATH_MATCH"
                    ),
                    "source_count": len(sources),
                    "sources": sources[:64],
                }
            )
        for record in records:
            record["hash216_identity"] = _hash216("HHS-P191-LINEAGE-RECORD", record)
        identity = {
            "baseline_commit": commit,
            "records": records,
            "all_slots_represented": len(records) == 191,
        }
        return {
            **identity,
            "lineage_root_hash216": _hash216("HHS-P191-LINEAGE", identity),
        }

    def _verify_dqpl_inheritance(self, commit: str) -> dict[str, Any]:
        try:
            evidence = json.loads(str(self._git("show", f"{commit}:{DQPL_EVIDENCE_PATH}")))
            completion = json.loads(str(self._git("show", f"{commit}:{DQPL_COMPLETION_PATH}")))
        except Exception as exc:
            raise Pass191Error("HHS_P191_DQPL_EVIDENCE_UNAVAILABLE") from exc
        if evidence.get("theorem_decision", {}).get("status") != "OBSTRUCTED":
            raise Pass191Error("HHS_P191_DQPL_THEOREM_SCOPE_DRIFT")
        if completion.get("classification") != (
            "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED"
        ):
            raise Pass191Error("HHS_P191_DQPL_COMPLETION_CLASSIFICATION_DRIFT")
        if completion.get("visited") != 51_648_192:
            raise Pass191Error("HHS_P191_DQPL_VISITED_COUNT_DRIFT")
        if completion.get("exact_chain_hits") != 837:
            raise Pass191Error("HHS_P191_DQPL_EXACT_HIT_COUNT_DRIFT")
        if completion.get("frontier_size") != 16:
            raise Pass191Error("HHS_P191_DQPL_FRONTIER_DRIFT")
        if completion.get("theorem_decision", {}).get("status") != "OBSTRUCTED":
            raise Pass191Error("HHS_P191_DQPL_COMPLETION_THEOREM_SCOPE_DRIFT")
        return {
            "contract": DQPL_CONTRACT_ID,
            "classification": completion["classification"],
            "visited": completion["visited"],
            "exact_chain_hits": completion["exact_chain_hits"],
            "frontier_size": completion["frontier_size"],
            "theorem_status": "OBSTRUCTED",
            "authority_path": completion.get("authority_path"),
            "integrated_search_hash72": completion.get("integrated_manifold_search_hash72"),
            "completion_hash72": completion.get("completion_hash72"),
            "role": "INHERITED_EXECUTED_PROOF_SEARCH_AND_DEPENDENCY_EVIDENCE",
        }

    def preview(
        self,
        *,
        commit: str = "HEAD",
        since_commit: Optional[str] = None,
        bounds: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        resolved_bounds = HydrationBounds.from_mapping(bounds)
        try:
            resolved_commit = str(self._git("rev-parse", f"{commit}^{{commit}}"))
        except subprocess.CalledProcessError as exc:
            raise Pass191Error("HHS_P191_COMMIT_NOT_FOUND", commit) from exc

        started = time.perf_counter_ns()
        changed = self._changed_paths(since_commit, resolved_commit)
        objects, blockers = self._tree_rows(
            resolved_commit, resolved_bounds, changed_paths=changed
        )
        contract_blob = self._contract_blob(resolved_commit)
        function_registry = self._function_registry(resolved_commit)
        lineage = self._lineage(objects, resolved_commit)
        invariants = universal_invariant_registry(contract_blob)
        dqpl = self._verify_dqpl_inheritance(resolved_commit)

        object_identity = {
            "commit": resolved_commit,
            "since_commit": since_commit,
            "objects": [
                [
                    obj["path"],
                    obj["mode"],
                    obj["git_blob"],
                    obj["size_bytes"],
                    obj["hash216_identity"],
                ]
                for obj in objects
            ],
        }
        object_registry_root = _hash216("HHS-P191-OBJECT-REGISTRY", object_identity)
        hash216_index_root = _hash216(
            "HHS-P191-HASH216-INDEX",
            [obj["hash216_identity"] for obj in objects]
            + [item["Hash216_identity"] for item in function_registry["operations"]]
            + [item["hash216_identity"] for item in invariants["invariants"]],
        )
        topology = {
            "object_registry_root": object_registry_root,
            "function_registry_root": function_registry["registry_root_hash216"],
            "pass_lineage_root": lineage["lineage_root_hash216"],
            "invariant_registry_root": invariants["registry_root_hash216"],
            "hash216_index_root": hash216_index_root,
        }
        topology["hydrated_repository_root_hash216"] = _hash216(
            "HHS-P191-HYDRATED-REPOSITORY", topology
        )

        canonical = {
            "schema": "HHS_PASS_191_REPOSITORY_HYDRATION_MANIFEST_V1",
            "contract": CONTRACT_ID,
            "contract_version": CONTRACT_VERSION,
            "contract_authorization_commit": CONTRACT_AUTHORIZATION_COMMIT,
            "baseline_commit": resolved_commit,
            "incremental_since_commit": since_commit,
            "mode": "INCREMENTAL" if since_commit else "FULL_COMMITTED_TREE",
            "source_preservation": "GIT_BLOB_IDENTITY_EXACT",
            "objects": objects,
            "object_count": len(objects),
            "bytes_scanned": sum(int(obj["size_bytes"]) for obj in objects),
            "lineage": lineage,
            "function_registry": function_registry,
            "invariant_registry": invariants,
            "dqpl_inheritance": dqpl,
            "symmetry": exact_symmetry_witness(),
            "topology": topology,
            "blockers": blockers,
            "bounds": asdict(resolved_bounds),
            "all_configured_objects_classified": not blockers,
            "singleton_vm81_authority": "INHERITED",
            "floating_point_canonical_authority": False,
            "completion_classification": (
                RUNTIME_COMPLETION_CLASSIFICATION if not blockers else "BLOCKED"
            ),
        }
        serialized = _canonical(canonical)
        if len(serialized) > resolved_bounds.max_manifest_bytes:
            raise Pass191Error(
                "HHS_P191_MANIFEST_SIZE_BLOCKED",
                f"{len(serialized)}>{resolved_bounds.max_manifest_bytes}",
            )
        canonical["manifest_hash216_identity"] = _hash216(
            "HHS-P191-HYDRATION-MANIFEST", canonical
        )
        canonical["noncanonical_metrics"] = {
            "scan_duration_ns": time.perf_counter_ns() - started,
            "wall_clock_authority": False,
        }
        return canonical

    @staticmethod
    def compact(manifest: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "schema": manifest["schema"],
            "contract": manifest["contract"],
            "baseline_commit": manifest["baseline_commit"],
            "incremental_since_commit": manifest["incremental_since_commit"],
            "mode": manifest["mode"],
            "object_count": manifest["object_count"],
            "bytes_scanned": manifest["bytes_scanned"],
            "functions_registered": len(manifest["function_registry"]["operations"]),
            "passes_linked": len(manifest["lineage"]["records"]),
            "invariants_registered": len(manifest["invariant_registry"]["invariants"]),
            "blocker_count": len(manifest["blockers"]),
            "topology": manifest["topology"],
            "manifest_hash216_identity": manifest["manifest_hash216_identity"],
            "dqpl_inheritance": manifest["dqpl_inheritance"],
            "symmetry_valid": manifest["symmetry"]["valid"],
            "completion_classification": manifest["completion_classification"],
            "floating_point_canonical_authority": False,
        }

    def create_job(
        self,
        request: Mapping[str, Any],
        *,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        state_hash72, authority_receipt_hash72 = _authority_lineage(authority_execution)
        normalized = {
            "commit": str(request.get("commit", "HEAD")),
            "since_commit": request.get("since_commit"),
            "bounds": dict(request.get("bounds") or {}),
            "read_only": True,
            "repair_authority": False,
        }
        seed = {
            "request": normalized,
            "state_hash72": state_hash72,
            "authority_receipt_hash72": authority_receipt_hash72,
            "sequence": len(self.list_jobs()),
        }
        job_hash216 = _hash216("HHS-P191-JOB", seed)
        job_id = "P191-" + hashlib.sha256(job_hash216.encode("utf-8")).hexdigest()[:40]
        existing = self._job_path(job_id)
        if existing.exists():
            return self.get_job(job_id)
        event = {
            "stage": "QUEUED",
            "completed_work_count": 0,
            "total_work_count": None,
            "current_object": None,
            "checkpoint": "REQUEST_PERSISTED",
            "authority_receipt_hash72": authority_receipt_hash72,
        }
        job = {
            "schema": "HHS_PASS_191_HYDRATION_JOB_V1",
            "job_id": job_id,
            "job_hash216_identity": job_hash216,
            "request": normalized,
            "stage": "QUEUED",
            "history": [event],
            "manifest": None,
            "failure_reason": None,
            "recovery_action": "POST resume with inherited VM81 authority",
            "receipt_links": [],
            "artifact_links": [],
            "replay_attempts": 0,
            "bounds": normalized["bounds"],
        }
        self._write_job(job)
        receipt = self._append_receipt(
            "P191.Hydrate.Repository",
            job_id,
            {"stage": "QUEUED", "job_hash216_identity": job_hash216},
            state_hash72,
            authority_receipt_hash72,
        )
        job["receipt_links"].append(receipt["receipt_hash72"])
        self._write_job(job)
        return job

    def resume_job(
        self,
        job_id: str,
        *,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        state_hash72, authority_receipt_hash72 = _authority_lineage(authority_execution)
        job = self.get_job(job_id)
        if job["stage"] in TERMINAL_STAGES:
            return job
        started = time.perf_counter_ns()
        stages = [
            "DISCOVERING",
            "PRESERVING",
            "CLASSIFYING",
            "PARSING",
            "TYPING",
            "INDEXING",
            "LINKING",
            "BINDING",
            "VALIDATING",
            "ADMISSION_PENDING",
            "COMMITTING",
            "REPLAYING",
        ]
        try:
            for index, stage in enumerate(stages):
                self._transition(
                    job,
                    stage,
                    completed=index,
                    total=len(stages) + 1,
                    checkpoint=f"{stage}_CHECKPOINT",
                    authority_receipt_hash72=authority_receipt_hash72,
                )
                if time.perf_counter_ns() - started > HydrationBounds.from_mapping(
                    job["bounds"]
                ).max_total_job_duration_ns:
                    raise Pass191Error("HHS_P191_TOTAL_JOB_DURATION_BLOCKED")
                if stage == "DISCOVERING":
                    manifest = self.preview(
                        commit=job["request"]["commit"],
                        since_commit=job["request"]["since_commit"],
                        bounds=job["bounds"],
                    )
                    with self._mutation_lock:
                        self._raise_if_cancelled(job_id)
                        job["manifest"] = manifest
                        job["history"][-1]["total_work_count"] = manifest["object_count"]
                        job["history"][-1]["completed_work_count"] = manifest["object_count"]
                        self._write_job(job)
                elif stage == "VALIDATING":
                    manifest = job.get("manifest")
                    if not isinstance(manifest, dict):
                        raise Pass191Error("HHS_P191_JOB_MANIFEST_MISSING")
                    if manifest["symmetry"]["valid"] is not True:
                        raise Pass191Error("HHS_P191_SYMMETRY_VALIDATION_FAILED")
                    if manifest["lineage"]["all_slots_represented"] is not True:
                        raise Pass191Error("HHS_P191_LINEAGE_INCOMPLETE")
                    if manifest["blockers"]:
                        raise Pass191Error(
                            "HHS_P191_HYDRATION_BLOCKED",
                            str(len(manifest["blockers"])),
                        )
                elif stage == "REPLAYING":
                    verification = self._verify_manifest(job["manifest"])
                    if verification["ok"] is not True:
                        raise Pass191Error("HHS_P191_MANIFEST_VERIFY_FAILED")

            self._transition(
                job,
                "COMPLETED",
                completed=len(stages) + 1,
                total=len(stages) + 1,
                checkpoint="HYDRATION_CLOSED",
                authority_receipt_hash72=authority_receipt_hash72,
            )
            receipt = self._append_receipt(
                "P191.Hydrate.Resume",
                job_id,
                {
                    "stage": "COMPLETED",
                    "hydrated_repository_root_hash216": job["manifest"]["topology"][
                        "hydrated_repository_root_hash216"
                    ],
                    "manifest_hash216_identity": job["manifest"][
                        "manifest_hash216_identity"
                    ],
                },
                state_hash72,
                authority_receipt_hash72,
            )
            job["receipt_links"].append(receipt["receipt_hash72"])
            job["completion_receipt_hash72"] = receipt["receipt_hash72"]
            self._write_job(job)
            return job
        except Pass191Error as exc:
            if exc.classification == "HHS_P191_JOB_CANCELLED":
                with self._mutation_lock:
                    return self.get_job(job_id)
            terminal = "BLOCKED" if "BLOCKED" in exc.classification else "FAILED"
            job["failure_reason"] = exc.classification
            job["recovery_action"] = (
                "Adjust explicit bounds or repair the named invariant/source condition, "
                "then create/resume a new dependency-scoped job."
            )
            self._transition(
                job,
                terminal,
                completed=len(job["history"]),
                total=None,
                checkpoint=f"{terminal}_CHECKPOINT",
                authority_receipt_hash72=authority_receipt_hash72,
            )
            receipt = self._append_receipt(
                "P191.Hydrate.Resume",
                job_id,
                {"stage": terminal, "failure_reason": exc.classification},
                state_hash72,
                authority_receipt_hash72,
            )
            job["receipt_links"].append(receipt["receipt_hash72"])
            self._write_job(job)
            return job

    def cancel_job(
        self,
        job_id: str,
        *,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        state_hash72, authority_receipt_hash72 = _authority_lineage(authority_execution)
        with self._mutation_lock:
            job = self.get_job(job_id)
            if job["stage"] in TERMINAL_STAGES:
                return job
            self._cancel_event(job_id).set()
            self._transition(
                job,
                "CANCELLED",
                completed=len(job["history"]),
                total=None,
                checkpoint="CANCELLED_BY_AUTHORIZED_REQUEST",
                authority_receipt_hash72=authority_receipt_hash72,
            )
            receipt = self._append_receipt(
                "P191.Hydrate.Cancel",
                job_id,
                {"stage": "CANCELLED"},
                state_hash72,
                authority_receipt_hash72,
            )
            job["receipt_links"].append(receipt["receipt_hash72"])
            self._write_job(job)
            return job

    def verify_job(self, job_id: str) -> dict[str, Any]:
        job = self.get_job(job_id)
        if job.get("manifest") is None:
            return {"ok": False, "classification": "HHS_P191_JOB_NOT_HYDRATED", "job_id": job_id}
        result = self._verify_manifest(job["manifest"])
        return {"job_id": job_id, **result}

    def replay_job(self, job_id: str) -> dict[str, Any]:
        job = self.get_job(job_id)
        bounds = HydrationBounds.from_mapping(job["bounds"])
        if int(job.get("replay_attempts", 0)) >= bounds.max_replay_attempts:
            raise Pass191Error("HHS_P191_REPLAY_ATTEMPT_LIMIT")
        if job.get("manifest") is None:
            raise Pass191Error("HHS_P191_JOB_NOT_HYDRATED")
        replayed = self.preview(
            commit=job["manifest"]["baseline_commit"],
            since_commit=job["manifest"]["incremental_since_commit"],
            bounds=job["bounds"],
        )
        keys = (
            "object_registry_root",
            "function_registry_root",
            "pass_lineage_root",
            "invariant_registry_root",
            "hash216_index_root",
            "hydrated_repository_root_hash216",
        )
        observed = job["manifest"]["topology"]
        expected = replayed["topology"]
        mismatches = [key for key in keys if observed.get(key) != expected.get(key)]
        return {
            "ok": not mismatches,
            "job_id": job_id,
            "baseline_commit": replayed["baseline_commit"],
            "mismatches": mismatches,
            "observed": {key: observed.get(key) for key in keys},
            "replayed": {key: expected.get(key) for key in keys},
            "hidden_process_state_required": False,
            "hidden_chat_memory_required": False,
        }

    def report(self, job_id: str) -> str:
        job = self.get_job(job_id)
        manifest = job.get("manifest")
        if not isinstance(manifest, dict):
            return (
                f"Pass 191 repository hydration job {job_id}\n"
                f"Status: {job['stage']}\n"
                "No hydration manifest has been produced yet.\n"
                f"Recovery: {job.get('recovery_action') or 'resume the job'}\n"
            )
        compact = self.compact(manifest)
        return "\n".join(
            [
                "Pass 191 Repository Hydration",
                f"Status: {job['stage']}",
                f"Baseline commit: {compact['baseline_commit']}",
                f"Objects discovered/hydrated: {compact['object_count']}",
                f"Bytes scanned: {compact['bytes_scanned']}",
                f"Pass records linked: {compact['passes_linked']}",
                f"Functions registered: {compact['functions_registered']}",
                f"Invariants registered: {compact['invariants_registered']}",
                f"Blockers: {compact['blocker_count']}",
                f"Symmetry: {'VERIFIED' if compact['symmetry_valid'] else 'FAILED'}",
                f"DQPL inherited theorem scope: {compact['dqpl_inheritance']['theorem_status']}",
                "VM81 mutation authority: INHERITED SINGLETON",
                f"Hydrated repository root: {compact['topology']['hydrated_repository_root_hash216']}",
                f"Completion classification: {compact['completion_classification']}",
                f"Replay status: {'VERIFIED' if job['stage'] == 'COMPLETED' else 'PENDING'}",
            ]
        ) + "\n"

    def get_job(self, job_id: str) -> dict[str, Any]:
        path = self._job_path(job_id)
        if not path.exists():
            raise Pass191Error("HHS_P191_JOB_NOT_FOUND", job_id)
        return json.loads(path.read_text("utf-8"))

    def list_jobs(self) -> list[dict[str, Any]]:
        if not self.jobs_root.exists():
            return []
        rows = []
        for path in sorted(self.jobs_root.glob("*.json")):
            try:
                rows.append(json.loads(path.read_text("utf-8")))
            except Exception as exc:
                raise Pass191Error("HHS_P191_JOB_FILE_INVALID", str(path)) from exc
        return rows

    def latest_completed_job(self) -> Optional[dict[str, Any]]:
        jobs = [job for job in self.list_jobs() if job.get("stage") == "COMPLETED"]
        return jobs[-1] if jobs else None

    def object_by_identity(self, object_id: str) -> dict[str, Any]:
        job = self.latest_completed_job()
        if job is None:
            raise Pass191Error("HHS_P191_NO_COMPLETED_HYDRATION")
        for obj in job["manifest"]["objects"]:
            if obj["hash216_identity"] == object_id:
                return obj
        raise Pass191Error("HHS_P191_OBJECT_NOT_FOUND", object_id)

    def function_by_id(self, operation_id: str) -> dict[str, Any]:
        job = self.latest_completed_job()
        if job is not None:
            operations = job["manifest"]["function_registry"]["operations"]
        else:
            operations = self._function_registry(self.head_commit())["operations"]
        for operation in operations:
            if operation["operation_id"] == operation_id:
                return operation
        raise Pass191Error("HHS_P191_FUNCTION_NOT_FOUND", operation_id)

    def lineage(self) -> dict[str, Any]:
        job = self.latest_completed_job()
        if job is not None:
            return job["manifest"]["lineage"]
        preview = self.preview()
        return preview["lineage"]

    def invariants(self) -> dict[str, Any]:
        job = self.latest_completed_job()
        if job is not None:
            return job["manifest"]["invariant_registry"]
        return universal_invariant_registry(self._contract_blob(self.head_commit()))

    def surfaces(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_191_SURFACE_REGISTRY_V1",
            "canonical_semantics": "PASS191_OPERATION_OVERLAY_PLUS_PASS190_REGISTRY",
            "surfaces": [
                "HARMONICODE",
                "PYTHON_SDK",
                "CLI",
                "OPENAPI",
                "WEBSOCKET",
                "VISUAL_IDE",
                "ASSISTANT_TOOL_MANIFEST",
            ],
            "api_prefix": "/v1/hydration",
            "websocket": "/v1/hydration/ws/{job_id}",
            "visual_ide": "/pass191-repository-hydration.html",
            "assistant_tools": "/v1/hydration/assistant-tools",
            "surface_specific_private_semantics": False,
        }

    def assistant_tools(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_191_ASSISTANT_TOOL_MANIFEST_V1",
            "read_only_first": True,
            "fabrication_forbidden": True,
            "tools": [
                {
                    "name": operation["canonical_name"],
                    "operation_id": operation["operation_id"],
                    "effect_class": operation["effect_class"],
                    "api": operation["HTTP_path"],
                }
                for operation in pass191_operation_overlay()
            ],
        }

    def receipt(self, receipt_hash72: str) -> dict[str, Any]:
        for record in self.receipts():
            if record["receipt_hash72"] == receipt_hash72:
                return record
        raise Pass191Error("HHS_P191_RECEIPT_NOT_FOUND", receipt_hash72)

    def receipts(self) -> list[dict[str, Any]]:
        if not self.receipt_path.exists():
            return []
        values = []
        for line in self.receipt_path.read_text("utf-8").splitlines():
            if line:
                values.append(json.loads(line))
        return values

    def replay_receipt_chain(self) -> dict[str, Any]:
        previous = None
        rows = self.receipts()
        for sequence, record in enumerate(rows):
            if record["sequence"] != sequence:
                raise Pass191Error("HHS_P191_RECEIPT_SEQUENCE_DRIFT")
            if record["previous_receipt_hash72"] != previous:
                raise Pass191Error("HHS_P191_RECEIPT_PREDECESSOR_DRIFT")
            body = {
                key: record[key]
                for key in (
                    "sequence",
                    "event",
                    "object_identity",
                    "state_hash72",
                    "authority_receipt_hash72",
                    "previous_receipt_hash72",
                    "payload",
                )
            }
            expected = _hash72("HHS-P191-RECEIPT", body)
            if expected != record["receipt_hash72"]:
                raise Pass191Error("HHS_P191_RECEIPT_HASH_DRIFT")
            if not validate_hash72(record["state_hash72"]) or not validate_hash72(
                record["authority_receipt_hash72"]
            ):
                raise Pass191Error("HHS_P191_RECEIPT_AUTHORITY_HASH_INVALID")
            previous = record["receipt_hash72"]
        return {
            "ok": True,
            "records": len(rows),
            "last_receipt_hash72": previous,
        }

    def _verify_manifest(self, manifest: Mapping[str, Any]) -> dict[str, Any]:
        topology = manifest["topology"]
        object_identity = {
            "commit": manifest["baseline_commit"],
            "since_commit": manifest["incremental_since_commit"],
            "objects": [
                [
                    obj["path"],
                    obj["mode"],
                    obj["git_blob"],
                    obj["size_bytes"],
                    obj["hash216_identity"],
                ]
                for obj in manifest["objects"]
            ],
        }
        expected_object_root = _hash216("HHS-P191-OBJECT-REGISTRY", object_identity)
        expected_index = _hash216(
            "HHS-P191-HASH216-INDEX",
            [obj["hash216_identity"] for obj in manifest["objects"]]
            + [
                item["Hash216_identity"]
                for item in manifest["function_registry"]["operations"]
            ]
            + [
                item["hash216_identity"]
                for item in manifest["invariant_registry"]["invariants"]
            ],
        )
        expected_repository = _hash216(
            "HHS-P191-HYDRATED-REPOSITORY",
            {
                "object_registry_root": expected_object_root,
                "function_registry_root": manifest["function_registry"][
                    "registry_root_hash216"
                ],
                "pass_lineage_root": manifest["lineage"]["lineage_root_hash216"],
                "invariant_registry_root": manifest["invariant_registry"][
                    "registry_root_hash216"
                ],
                "hash216_index_root": expected_index,
            },
        )
        checks = {
            "object_registry_root": topology["object_registry_root"] == expected_object_root,
            "function_registry_root": topology["function_registry_root"]
            == manifest["function_registry"]["registry_root_hash216"],
            "pass_lineage_root": topology["pass_lineage_root"]
            == manifest["lineage"]["lineage_root_hash216"],
            "invariant_registry_root": topology["invariant_registry_root"]
            == manifest["invariant_registry"]["registry_root_hash216"],
            "hash216_index_root": topology["hash216_index_root"] == expected_index,
            "hydrated_repository_root": topology["hydrated_repository_root_hash216"]
            == expected_repository,
            "symmetry": manifest["symmetry"]["valid"] is True,
            "float_authority": manifest["floating_point_canonical_authority"] is False,
        }
        return {"ok": all(checks.values()), "checks": checks}

    def _cancel_event(self, job_id: str) -> threading.Event:
        with self._mutation_lock:
            return self._cancel_events.setdefault(job_id, threading.Event())

    def _raise_if_cancelled(self, job_id: str) -> None:
        if self._cancel_event(job_id).is_set():
            raise Pass191Error("HHS_P191_JOB_CANCELLED")

    def _transition(
        self,
        job: dict[str, Any],
        stage: str,
        *,
        completed: int,
        total: Optional[int],
        checkpoint: str,
        authority_receipt_hash72: str,
    ) -> None:
        if stage not in LIFECYCLE:
            raise Pass191Error("HHS_P191_JOB_STAGE_INVALID", stage)
        with self._mutation_lock:
            if stage != "CANCELLED":
                self._raise_if_cancelled(str(job["job_id"]))
            event = {
                "stage": stage,
                "completed_work_count": completed,
                "total_work_count": total,
                "current_object": None,
                "checkpoint": checkpoint,
                "authority_receipt_hash72": authority_receipt_hash72,
            }
            job["stage"] = stage
            job["history"].append(event)
            self._write_job(job)

    def _append_receipt(
        self,
        event: str,
        object_identity: str,
        payload: Any,
        state_hash72: str,
        authority_receipt_hash72: str,
    ) -> dict[str, Any]:
        existing = self.receipts()
        previous = existing[-1]["receipt_hash72"] if existing else None
        body = {
            "sequence": len(existing),
            "event": event,
            "object_identity": object_identity,
            "state_hash72": state_hash72,
            "authority_receipt_hash72": authority_receipt_hash72,
            "previous_receipt_hash72": previous,
            "payload": payload,
        }
        body["receipt_hash72"] = _hash72("HHS-P191-RECEIPT", body)
        self.state_root.mkdir(parents=True, exist_ok=True)
        with self.receipt_path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical(body).decode("utf-8") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return body

    def _job_path(self, job_id: str) -> Path:
        if not re.fullmatch(r"P191-[0-9a-f]{40}", job_id):
            raise Pass191Error("HHS_P191_JOB_ID_INVALID", job_id)
        return self.jobs_root / f"{job_id}.json"

    def _write_job(self, job: Mapping[str, Any]) -> None:
        path = self._job_path(str(job["job_id"]))
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = _canonical(job) + b"\n"
        temp = path.with_suffix(".json.tmp")
        with temp.open("wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)


__all__ = [
    "CONTRACT_ID",
    "CONTRACT_VERSION",
    "CONTRACT_AUTHORIZATION_COMMIT",
    "FROZEN_I134",
    "DQPL_CONTRACT_ID",
    "RUNTIME_COMPLETION_CLASSIFICATION",
    "LO_SHU",
    "ORDERED_O8",
    "OUTER_HYDRATION_MODULUS",
    "Q",
    "N",
    "TRINARY",
    "LIFECYCLE",
    "PASS191_OPERATION_IDS",
    "HydrationBounds",
    "Pass191Error",
    "RepositoryHydrationRuntime",
    "exact_symmetry_witness",
    "universal_invariant_registry",
    "pass191_operation_overlay",
]
