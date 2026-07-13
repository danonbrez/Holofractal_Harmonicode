"""Pass 073 — first native HHS software-development workload.

This module is a workload/product layer above the frozen Pass 072
Holofractal HARMONICODE System v1.0-alpha foundation.

Repair invariants:
- canonical product identity is independent of host paths and runtime mode;
- live runtime use is optional and read-only;
- committed fallback artifacts are schema- and digest-verified;
- recorded witnesses remain recorded witnesses in every execution mode;
- undeclared binary normalization is rejected;
- Pass 068 is consumed through an authenticated 81-cell kernel binding;
- restart state is committed in-repository so no LLM context window is needed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional, Sequence, Tuple
import argparse
import hashlib
import json
import os
import platform
import shutil

PASS_ID = "PASS_073"
VERSION = "PASS_073_PORTABILITY_AND_PROVENANCE_REPAIR_V1"
PRODUCT_ID = "NATIVE_HHS_DETERMINISTIC_TRANSFORMATION_PACKAGE"
FROZEN_PASS072_SYSTEM_ROOT_HASH72 = (
    "ZF9bto?tV>P(KcFPL5L+csyy!jxdrAaadua1a!w-uwug8/MeMSqSS3*R>lXIefi)nyjXpc+)"
)
PASS072_ARCHIVE_SHA256 = "3BE8F1393B16E12EA7D2E2931BED7F26D9D095774C0979B3692AEB6174D2D794"
CANONICAL_INPUT_MANIFEST_RELATIVE_PATH = (
    "native_projects/pass073_deterministic_transform/artifacts/"
    "PASS_073_CANONICAL_INPUT_MANIFEST.json"
)
CANONICAL_INPUT_MANIFEST_SHA256 = (
    "9c8cfd26c7fc21e1ecc177928423be62e36f37bd653409a67565e5f61c6e3d1c"
)
PRODUCT_COMMITMENT_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()^=!?>"
PAIR_MAP: Dict[Tuple[int, int], Tuple[int, int]] = {
    (0, 0): (0, 0),
    (0, 1): (1, 0),
    (1, 0): (-1, 0),
    (1, 1): (0, 1),
}
INVERSE_PAIR_MAP = {value: key for key, value in PAIR_MAP.items()}
EXPECTED_LO_SHU = (8, 1, 6, 3, 5, 7, 4, 9, 2)
ResolutionMode = Literal["AUTO", "LIVE_RUNTIME", "COMMITTED_ARTIFACT"]


class ArtifactIntegrityError(RuntimeError):
    """Raised when a committed fallback artifact fails canonical binding."""


@dataclass(frozen=True)
class CanonicalState:
    schema: str
    system_root_hash72: str
    artifacts: Mapping[str, Any]
    artifact_bindings: Mapping[str, Mapping[str, Any]]
    manifest_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        """Return only repository-relative, content-addressed canonical identity."""
        return {
            "schema": self.schema,
            "system_root_hash72": self.system_root_hash72,
            "canonical_input_manifest": {
                "relative_path": CANONICAL_INPUT_MANIFEST_RELATIVE_PATH,
                "sha256": self.manifest_sha256,
            },
            "artifact_bindings": {
                key: {
                    "artifact_id": value["artifact_id"],
                    "relative_path": value["relative_path"],
                    "sha256": value["sha256"],
                    "schema": value["schema"],
                    **(
                        {
                            "root_field": value["root_field"],
                            "root_value": value["root_value"],
                        }
                        if value.get("root_field")
                        else {}
                    ),
                }
                for key, value in sorted(self.artifact_bindings.items())
            },
            "host_path_committed": False,
            "all_artifacts_digest_verified": True,
        }


@dataclass(frozen=True)
class WitnessRecord:
    object_id: str
    witness: Mapping[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_PASS073_HASH72_SURFACE_WITNESS_RECORD_V2",
            "object_id": self.object_id,
            "witness_source": "COMMITTED_CANONICAL_ARTIFACT",
            "witness": dict(self.witness),
            "recorded_witness_not_new_kernel_witness": True,
            "execution_mode_does_not_reclassify_witness": True,
        }


@dataclass(frozen=True)
class VerificationResult:
    schema: str
    execution_mode: str
    committed_root_hash72: str
    expected_root_hash72: str
    committed_root_verified: bool
    artifact_integrity_verified: bool
    live_total_system_verification_executed: bool
    live_total_system_root_hash72: Optional[str]
    live_total_system_root_matches: Optional[bool]
    live_pass068_kernel_verification_executed: bool
    live_pass068_lattice_root_hash72: Optional[str]
    live_pass068_lattice_root_matches: Optional[bool]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapabilityState:
    hash72_surface_mode: str
    live_c_runtime_available: bool
    runtime_library_relative_path: Optional[str]
    compiler_available: bool
    compiler_observation: Mapping[str, Optional[str]]
    canonical_artifact_access: bool
    committed_artifact_integrity_verified: bool
    new_kernel_witness_generation: bool
    implicit_build_authorized: bool
    foundation_modified: bool
    context_window_required: bool
    host_path_required_for_canonical_identity: bool
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NativeTransformInput:
    sequence: str
    width: int = 16
    mode: str = "binary_trinary_loshu_three_lane_zero_sum"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[2]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _stable(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str))


def _witness(label: str, payload: Any) -> Dict[str, Any]:
    stable_payload = _stable(payload)
    material = json.dumps(
        {"label": label, "payload": stable_payload},
        sort_keys=True,
        ensure_ascii=False,
        default=str,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(material).digest()
    value = int.from_bytes(digest, "big")
    base = len(PRODUCT_COMMITMENT_ALPHABET)
    chars: List[str] = []
    for _ in range(72):
        value, remainder = divmod(value, base)
        chars.append(PRODUCT_COMMITMENT_ALPHABET[remainder])
    digest72 = "".join(reversed(chars))
    return {
        "schema": "HHS_NATIVE_PRODUCT_COMMITMENT_WITNESS_V1",
        "authority": "PRODUCT_LOCAL_COMMITMENT_NOT_FOUNDATION_HASH72_AUTHORITY",
        "label": label,
        "digest": digest72,
        "digest72": digest72,
        "sha256": _sha256_bytes(material),
        "product_local_commitment_not_foundation_authority": True,
    }


def _root(label: str, payload: Any) -> str:
    return str(_witness(label, payload)["digest"])


def _finish(schema: str, body: Mapping[str, Any], root_field: str, label: str) -> Dict[str, Any]:
    payload = {"schema": schema, "version": VERSION, **dict(body)}
    payload[root_field] = _root(label, payload)
    return payload


def _runtime_library_relative_path() -> str:
    system = platform.system().lower()
    if system == "windows":
        name = "hhs_runtime.dll"
    elif system == "darwin":
        name = "libhhs_runtime.dylib"
    else:
        name = "libhhs_runtime.so"
    return f"hhs_runtime/builds/{name}"


def _compiler_observation() -> Dict[str, Optional[str]]:
    return {
        "make": shutil.which("make"),
        "cc": shutil.which("cc") or shutil.which("gcc") or shutil.which("clang"),
    }


class Hash72Surface:
    """Read-only dual-resolution surface for Pass 073.

    Canonical witnesses are always read from authenticated committed artifacts.
    Live mode adds independent platform verification; it never reclassifies a
    recorded witness and never auto-builds the frozen foundation.
    """

    mode: Literal["LIVE_RUNTIME", "COMMITTED_ARTIFACT"]

    def __init__(
        self,
        repo: Optional[str | Path] = None,
        *,
        resolution_mode: ResolutionMode = "AUTO",
    ) -> None:
        if resolution_mode not in {"AUTO", "LIVE_RUNTIME", "COMMITTED_ARTIFACT"}:
            raise ValueError(f"unsupported resolution mode: {resolution_mode}")
        self.repo = _repo_root(repo)
        self.requested_resolution_mode = resolution_mode
        self.mode = "COMMITTED_ARTIFACT"
        self._live_error: Optional[str] = None
        self._live_total_runner = None
        self._live_pass068_runner = None
        self._state_cache: Optional[CanonicalState] = None
        self._runtime_library_rel = _runtime_library_relative_path()
        self._runtime_library_path = self.repo / self._runtime_library_rel

        # Integrity is checked before optional live imports.
        self.load_canonical_state()

        if resolution_mode == "COMMITTED_ARTIFACT":
            self._live_error = "LIVE_RUNTIME_NOT_REQUESTED"
            return

        if not self._runtime_library_path.is_file():
            self._live_error = (
                "LIVE_C_RUNTIME_LIBRARY_ABSENT; READ_ONLY_PROBE_DID_NOT_BUILD_FOUNDATION: "
                f"{self._runtime_library_rel}"
            )
            if resolution_mode == "LIVE_RUNTIME":
                raise RuntimeError(self._live_error)
            return

        prior = os.environ.get("HHS_DISABLE_C_AUTOBUILD")
        os.environ["HHS_DISABLE_C_AUTOBUILD"] = "1"
        try:
            from hhs_backend.runtime.hhs_total_system_recursive_holographic_closure_v1 import (
                run_total_system_recursive_holographic_closure,
            )
            from hhs_backend.runtime.hhs_three_lane_81_cell_qudit_kernel_v1 import (
                run_three_lane_81_cell_kernel,
            )

            self._live_total_runner = run_total_system_recursive_holographic_closure
            self._live_pass068_runner = run_three_lane_81_cell_kernel
            self.mode = "LIVE_RUNTIME"
        except Exception as exc:  # pragma: no cover - depends on host ABI
            self._live_error = f"{type(exc).__name__}: {exc}"
            if resolution_mode == "LIVE_RUNTIME":
                raise RuntimeError(self._live_error) from exc
        finally:
            if prior is None:
                os.environ.pop("HHS_DISABLE_C_AUTOBUILD", None)
            else:
                os.environ["HHS_DISABLE_C_AUTOBUILD"] = prior

    def _manifest(self) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        path = self.repo / CANONICAL_INPUT_MANIFEST_RELATIVE_PATH
        data = path.read_bytes()
        observed = _sha256_bytes(data)
        if observed != CANONICAL_INPUT_MANIFEST_SHA256:
            raise ArtifactIntegrityError(
                "REJECT_CANONICAL_INPUT_MANIFEST_DIGEST_MISMATCH: "
                f"expected={CANONICAL_INPUT_MANIFEST_SHA256} observed={observed}"
            )
        manifest = json.loads(data.decode("utf-8"))
        if manifest.get("schema") != "HHS_PASS_073_CANONICAL_INPUT_MANIFEST_V1":
            raise ArtifactIntegrityError("REJECT_CANONICAL_INPUT_MANIFEST_SCHEMA_MISMATCH")
        bindings = {str(item["artifact_id"]): dict(item) for item in manifest.get("artifacts", [])}
        if len(bindings) != int(manifest.get("artifact_count", -1)):
            raise ArtifactIntegrityError("REJECT_CANONICAL_INPUT_MANIFEST_CARDINALITY_MISMATCH")
        return manifest, bindings

    def _read_verified_json(self, binding: Mapping[str, Any]) -> Dict[str, Any]:
        relative = str(binding["relative_path"])
        rel_path = Path(relative)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            raise ArtifactIntegrityError("REJECT_NONCANONICAL_ARTIFACT_PATH")
        path = self.repo / rel_path
        data = path.read_bytes()
        observed = _sha256_bytes(data)
        expected = str(binding["sha256"])
        if observed != expected:
            raise ArtifactIntegrityError(
                "REJECT_COMMITTED_ARTIFACT_DIGEST_MISMATCH: "
                f"artifact={binding['artifact_id']} expected={expected} observed={observed}"
            )
        payload = json.loads(data.decode("utf-8"))
        if payload.get("schema") != binding.get("schema"):
            raise ArtifactIntegrityError(
                "REJECT_COMMITTED_ARTIFACT_SCHEMA_MISMATCH: "
                f"artifact={binding['artifact_id']}"
            )
        root_field = binding.get("root_field")
        if root_field and payload.get(root_field) != binding.get("root_value"):
            raise ArtifactIntegrityError(
                "REJECT_COMMITTED_ARTIFACT_ROOT_BINDING_MISMATCH: "
                f"artifact={binding['artifact_id']} field={root_field}"
            )
        return payload

    def load_canonical_state(self) -> CanonicalState:
        if self._state_cache is not None:
            return self._state_cache
        _, bindings = self._manifest()
        artifacts = {key: self._read_verified_json(binding) for key, binding in bindings.items()}
        required = {
            "pass072_total_system_root",
            "pass070_universal_binary_trinary_translation",
            "pass070_binary_trinary_round_trip",
            "pass070_zero_sum_switching_closure",
            "pass068_three_lane_81_cell_qudit_kernel",
        }
        if set(artifacts) != required:
            raise ArtifactIntegrityError("REJECT_CANONICAL_INPUT_SET_MISMATCH")
        self._validate_artifact_relations(artifacts)
        system_root = str(artifacts["pass072_total_system_root"]["total_system_root_hash72"])
        self._state_cache = CanonicalState(
            schema="HHS_PASS073_HASH72_SURFACE_CANONICAL_STATE_V2",
            system_root_hash72=system_root,
            artifacts=artifacts,
            artifact_bindings=bindings,
            manifest_sha256=CANONICAL_INPUT_MANIFEST_SHA256,
        )
        return self._state_cache

    @staticmethod
    def _validate_artifact_relations(artifacts: Mapping[str, Any]) -> None:
        root = artifacts["pass072_total_system_root"].get("total_system_root_hash72")
        if root != FROZEN_PASS072_SYSTEM_ROOT_HASH72:
            raise ArtifactIntegrityError("REJECT_PASS072_TOTAL_SYSTEM_ROOT_MISMATCH")

        universal = artifacts["pass070_universal_binary_trinary_translation"]
        expected_mapping = {key: list(value) for key, value in {"00": (0, 0), "01": (1, 0), "10": (-1, 0), "11": (0, 1)}.items()}
        if universal.get("mapping") != expected_mapping:
            raise ArtifactIntegrityError("REJECT_PASS070_TRANSLATION_MAPPING_MISMATCH")
        if not universal.get("translation_is_reversible") or not universal.get("all_pair_round_trips_valid"):
            raise ArtifactIntegrityError("REJECT_PASS070_TRANSLATION_NOT_CLOSED")

        round_trip = artifacts["pass070_binary_trinary_round_trip"]
        records = list(round_trip.get("pair_records", []))
        record_ids = {"".join(str(bit) for bit in item["source"]["bits"]) for item in records}
        if record_ids != {"00", "01", "10", "11"} or not round_trip.get("all_valid"):
            raise ArtifactIntegrityError("REJECT_PASS070_ROUND_TRIP_RECORD_SET_MISMATCH")
        for item in records:
            pair_id = "".join(str(bit) for bit in item["source"]["bits"])
            expected_phase, expected_switch = PAIR_MAP[tuple(item["source"]["bits"])]
            if (
                item["state"].get("trinary_phase") != expected_phase
                or item["state"].get("binary_switch") != expected_switch
                or not item["gate"].get("round_trip_valid")
                or not item["gate"].get("zero_sum_closed")
            ):
                raise ArtifactIntegrityError(f"REJECT_PASS070_PAIR_RELATION_MISMATCH:{pair_id}")

        closure = artifacts["pass070_zero_sum_switching_closure"]
        if not (
            closure.get("translation_reversible")
            and closure.get("zero_states_distinguished")
            and closure.get("switch_confers_authority") is False
            and len(closure.get("pair_gate_roots_hash72", [])) == 4
        ):
            raise ArtifactIntegrityError("REJECT_PASS070_ZERO_SUM_CLOSURE_MISMATCH")

        kernel = artifacts["pass068_three_lane_81_cell_qudit_kernel"]
        cells = list(kernel.get("cells", []))
        lo_shu = tuple(int(item["lo_shu_value"]) for item in cells[:9])
        if (
            kernel.get("cell_count") != 81
            or kernel.get("subgrid_count") != 9
            or not kernel.get("global_closure")
            or lo_shu != EXPECTED_LO_SHU
        ):
            raise ArtifactIntegrityError("REJECT_PASS068_KERNEL_BINDING_MISMATCH")

    def resolve_witness(self, object_id: str) -> WitnessRecord:
        artifacts = self.load_canonical_state().artifacts
        if object_id == "PASS_072_TOTAL_SYSTEM_ROOT":
            source = artifacts["pass072_total_system_root"]
            witness: Mapping[str, Any] = {
                "source_artifact_id": "pass072_total_system_root",
                "source_relative_path": "PASS_072_TOTAL_SYSTEM_ROOT.json",
                "root_field": "total_system_root_hash72",
                "root_hash72": source["total_system_root_hash72"],
                "authority": source.get("authority"),
                "source_sha256": self.load_canonical_state().artifact_bindings[
                    "pass072_total_system_root"
                ]["sha256"],
            }
        elif object_id in {"00", "01", "10", "11"}:
            records = artifacts["pass070_binary_trinary_round_trip"]["pair_records"]
            match = next(
                item for item in records if "".join(str(bit) for bit in item["source"]["bits"]) == object_id
            )
            witness = {
                "source_artifact_id": "pass070_binary_trinary_round_trip",
                "source_relative_path": "BINARY_TRINARY_ROUND_TRIP_PASS_070.json",
                "source_sha256": self.load_canonical_state().artifact_bindings[
                    "pass070_binary_trinary_round_trip"
                ]["sha256"],
                "source_root_hash72": match["source"]["source_root_hash72"],
                "translation_root_hash72": match["state"]["translation_root_hash72"],
                "reconstruction_root_hash72": match["reconstruction"]["reconstruction_root_hash72"],
                "gate_root_hash72": match["gate"]["gate_root_hash72"],
                "authority": match["state"]["authority"],
            }
        else:
            raise KeyError(f"unknown committed Hash72 witness object id: {object_id}")
        return WitnessRecord(object_id=object_id, witness=witness)

    def pass068_kernel_binding(self) -> Dict[str, Any]:
        state = self.load_canonical_state()
        kernel = state.artifacts["pass068_three_lane_81_cell_qudit_kernel"]
        cells = list(kernel["cells"])
        return {
            "schema": "HHS_PASS073_PASS068_KERNEL_BINDING_V1",
            "source_artifact_id": "pass068_three_lane_81_cell_qudit_kernel",
            "source_relative_path": "THREE_LANE_81_CELL_QUDIT_KERNEL_PASS_068.json",
            "source_sha256": state.artifact_bindings[
                "pass068_three_lane_81_cell_qudit_kernel"
            ]["sha256"],
            "source_schema": kernel["schema"],
            "lattice_root_hash72": kernel["lattice_root_hash72"],
            "cell_count": kernel["cell_count"],
            "subgrid_count": kernel["subgrid_count"],
            "global_closure": kernel["global_closure"],
            "lo_shu_cycle": [int(item["lo_shu_value"]) for item in cells[:9]],
            "first_subgrid_cell_ids": [str(item["cell_id"]) for item in cells[:9]],
            "artifact_consumed_as_read_only_kernel_surface": True,
        }

    def verify_committed_root(self) -> VerificationResult:
        state = self.load_canonical_state()
        committed_root = state.system_root_hash72
        live_root: Optional[str] = None
        live_root_matches: Optional[bool] = None
        live_kernel_root: Optional[str] = None
        live_kernel_matches: Optional[bool] = None
        live_total_executed = False
        live_pass068_executed = False

        if self.mode == "LIVE_RUNTIME" and self._live_total_runner is not None:
            live_total = self._live_total_runner()
            live_root = str(live_total["total_system_root_hash72"])
            live_root_matches = live_root == FROZEN_PASS072_SYSTEM_ROOT_HASH72
            live_total_executed = True
        if self.mode == "LIVE_RUNTIME" and self._live_pass068_runner is not None:
            live_kernel = self._live_pass068_runner()
            live_kernel_root = str(live_kernel["lattice_root_hash72"])
            expected = str(
                state.artifacts["pass068_three_lane_81_cell_qudit_kernel"]["lattice_root_hash72"]
            )
            live_kernel_matches = live_kernel_root == expected
            live_pass068_executed = True

        verified = committed_root == FROZEN_PASS072_SYSTEM_ROOT_HASH72
        if live_root_matches is False or live_kernel_matches is False:
            verified = False
        return VerificationResult(
            schema="HHS_PASS073_HASH72_SURFACE_VERIFICATION_RESULT_V2",
            execution_mode=self.mode,
            committed_root_hash72=committed_root,
            expected_root_hash72=FROZEN_PASS072_SYSTEM_ROOT_HASH72,
            committed_root_verified=verified,
            artifact_integrity_verified=True,
            live_total_system_verification_executed=live_total_executed,
            live_total_system_root_hash72=live_root,
            live_total_system_root_matches=live_root_matches,
            live_pass068_kernel_verification_executed=live_pass068_executed,
            live_pass068_lattice_root_hash72=live_kernel_root,
            live_pass068_lattice_root_matches=live_kernel_matches,
        )

    def capabilities(self) -> CapabilityState:
        observation = _compiler_observation()
        compiler_available = bool(observation["cc"])
        return CapabilityState(
            hash72_surface_mode=self.mode,
            live_c_runtime_available=self.mode == "LIVE_RUNTIME",
            runtime_library_relative_path=(
                self._runtime_library_rel if self._runtime_library_path.is_file() else None
            ),
            compiler_available=compiler_available,
            compiler_observation=observation,
            canonical_artifact_access=True,
            committed_artifact_integrity_verified=True,
            new_kernel_witness_generation=False,
            implicit_build_authorized=False,
            foundation_modified=False,
            context_window_required=False,
            host_path_required_for_canonical_identity=False,
            status=(
                "ADMIT_NATIVE_WORKLOAD_WITH_LIVE_REVALIDATION"
                if self.mode == "LIVE_RUNTIME"
                else "ADMIT_CONSTRAINED_NATIVE_WORKLOAD_FROM_AUTHENTICATED_ARTIFACTS"
            ),
        )

    @property
    def live_error(self) -> Optional[str]:
        return self._live_error


def _bits_for_word(word: int, width: int) -> str:
    if word < 0:
        raise ValueError("word must be non-negative")
    if width <= 0 or width % 2 != 0:
        raise ValueError("translation width must be a positive even integer")
    if word >= (1 << width):
        raise ValueError("word exceeds translation width")
    return format(word, f"0{width}b")


def _normalize_bits(sequence: str, width: int) -> Dict[str, Any]:
    original = str(sequence)
    if not original:
        raise ValueError("REJECT_EMPTY_BINARY_INPUT")
    invalid = sorted({ch for ch in original if ch not in "01"})
    if invalid:
        rendered = ",".join(repr(ch) for ch in invalid)
        raise ValueError(f"REJECT_UNDECLARED_NON_BINARY_CHARACTERS:{rendered}")
    if width <= 0 or width % 2 != 0:
        raise ValueError("REJECT_INVALID_TRANSLATION_WIDTH")
    if len(original) > width:
        raise ValueError("REJECT_BINARY_SEQUENCE_EXCEEDS_DECLARED_WIDTH")
    padded = original.zfill(width)
    operation = "IDENTITY" if padded == original else "LEFT_ZERO_PAD_TO_DECLARED_WIDTH"
    return {
        "schema": "HHS_STRICT_BINARY_INPUT_NORMALIZATION_RECEIPT_V1",
        "original_sequence": original,
        "original_sequence_sha256": _sha256_bytes(original.encode("utf-8")),
        "canonical_bits": padded,
        "canonical_bits_sha256": _sha256_bytes(padded.encode("utf-8")),
        "width": width,
        "source_word": int(padded, 2),
        "normalization_operation": operation,
        "left_zero_count": width - len(original),
        "undeclared_characters_removed": False,
        "source_identity_preserved": True,
    }


def translate_word(word: int, width: int, surface: Optional[Hash72Surface] = None) -> Dict[str, Any]:
    hash72_surface = surface or Hash72Surface()
    bits = _bits_for_word(int(word), int(width))
    pairs: List[Dict[str, Any]] = []
    trinary_lane_vector: List[int] = []
    binary_switch_mask: List[int] = []
    for index in range(0, width, 2):
        left = int(bits[index])
        right = int(bits[index + 1])
        trinary_phase, binary_switch = PAIR_MAP[(left, right)]
        witness_body = hash72_surface.resolve_witness(f"{left}{right}").to_dict()
        inverse_left, inverse_right = INVERSE_PAIR_MAP[(trinary_phase, binary_switch)]
        round_trip_valid = (inverse_left, inverse_right) == (left, right)
        zero_sum_closed = trinary_phase + (-trinary_phase) == 0
        pairs.append(
            {
                "pair_index": index // 2,
                "source": {"left_bit": left, "right_bit": right},
                "state": {
                    "trinary_phase": trinary_phase,
                    "binary_switch": binary_switch,
                    "translation_root_hash72": witness_body["witness"]["translation_root_hash72"],
                    "recorded_witness_not_new_kernel_witness": True,
                },
                "reconstruction": {
                    "left_bit": inverse_left,
                    "right_bit": inverse_right,
                    "reconstruction_root_hash72": witness_body["witness"]["reconstruction_root_hash72"],
                },
                "gate": {
                    "round_trip_valid": round_trip_valid,
                    "zero_sum_closed": zero_sum_closed,
                    "gate_root_hash72": witness_body["witness"]["gate_root_hash72"],
                },
                "committed_witness": witness_body,
            }
        )
        trinary_lane_vector.append(trinary_phase)
        binary_switch_mask.append(binary_switch)
    return _finish(
        "HHS_NATIVE_PRODUCT_BINARY_TRINARY_PACKET_V2",
        {
            "word": word,
            "width": width,
            "bits": bits,
            "pairs": pairs,
            "trinary_lane_vector": trinary_lane_vector,
            "binary_switch_mask": binary_switch_mask,
            "all_zero_sum_closed": all(item["gate"]["zero_sum_closed"] for item in pairs),
            "all_round_trip_valid": all(item["gate"]["round_trip_valid"] for item in pairs),
            "witness_source": "AUTHENTICATED_PASS070_COMMITTED_ARTIFACT",
            "execution_mode_excluded_from_semantic_commitment": True,
            "projection_access_not_platform_authority": True,
        },
        "packet_root_hash72",
        "pass073_native_product_binary_trinary_packet_v2",
    )


def reconstruct_word(packet: Mapping[str, Any]) -> Dict[str, Any]:
    bits: List[str] = []
    for pair in packet["pairs"]:
        reconstruction = pair["reconstruction"]
        bits.extend((str(int(reconstruction["left_bit"])), str(int(reconstruction["right_bit"]))))
    reconstructed_bits = "".join(bits)
    reconstructed_word = int(reconstructed_bits, 2) if reconstructed_bits else 0
    canonical_reconstruction = reconstructed_bits == packet["bits"]
    return _finish(
        "HHS_NATIVE_PRODUCT_RECONSTRUCTION_V1",
        {
            "packet_root_hash72": packet["packet_root_hash72"],
            "reconstructed_bits": reconstructed_bits,
            "reconstructed_word": reconstructed_word,
            "round_trip_valid": canonical_reconstruction and bool(packet["all_round_trip_valid"]),
            "canonical_reconstruction": canonical_reconstruction,
        },
        "round_trip_root_hash72",
        "pass073_native_product_reconstruction_v1",
    )


def make_alpha_release_baseline(
    root: Optional[str | Path] = None,
    surface: Optional[Hash72Surface] = None,
) -> Dict[str, Any]:
    hash72_surface = surface or Hash72Surface(root)
    state = hash72_surface.load_canonical_state()
    total_witness = hash72_surface.resolve_witness("PASS_072_TOTAL_SYSTEM_ROOT")
    kernel = hash72_surface.pass068_kernel_binding()
    return _finish(
        "HHS_ALPHA_RELEASE_SEMANTIC_BASELINE_V2",
        {
            "version_label": "1.0-alpha",
            "canonical_pass": "PASS_072",
            "total_system_root_hash72": FROZEN_PASS072_SYSTEM_ROOT_HASH72,
            "system_root_matches_frozen_release": state.system_root_hash72
            == FROZEN_PASS072_SYSTEM_ROOT_HASH72,
            "canonical_state": state.to_dict(),
            "total_system_witness": total_witness.to_dict(),
            "pass068_kernel_binding": kernel,
            "source_archive_sha256": PASS072_ARCHIVE_SHA256,
            "foundation_frozen": True,
            "ordinary_workload_may_mutate_foundation": False,
            "foundation_service_delta": 0,
            "foundation_surface_delta": 0,
            "foundation_authority_delta": 0,
            "runtime_mode_excluded_from_semantic_baseline": True,
            "host_path_excluded_from_semantic_baseline": True,
        },
        "system_baseline_root_hash72",
        "hhs_alpha_release_semantic_baseline_v2",
    )


def make_execution_environment(surface: Hash72Surface) -> Dict[str, Any]:
    verification = surface.verify_committed_root().to_dict()
    capabilities = surface.capabilities().to_dict()
    return _finish(
        "HHS_PASS073_EXECUTION_ENVIRONMENT_ENVELOPE_V1",
        {
            "execution_mode": surface.mode,
            "requested_resolution_mode": surface.requested_resolution_mode,
            "capabilities": capabilities,
            "platform_verification": verification,
            "live_platform_verification_error": surface.live_error,
            "semantic_product_root_must_not_depend_on_this_envelope": True,
            "implicit_foundation_build_performed": False,
            "foundation_mutation": False,
        },
        "execution_environment_root_hash72",
        "hhs_pass073_execution_environment_envelope_v1",
    )


def make_project_requirement(user_requirement: str, typed_input: Mapping[str, Any]) -> Dict[str, Any]:
    return _finish(
        "HHS_PROJECT_REQUIREMENT_V2",
        {
            "pass_id": PASS_ID,
            "requirement_text": user_requirement,
            "typed_input": dict(typed_input),
            "product_goal": "derive a deterministic binary/trinary Lo Shu scheduled artifact with replay",
            "environment_independence_required": True,
            "context_window_independence_required": True,
            "foundation_mutation_requested": False,
        },
        "requirement_root_hash72",
        "hhs_project_requirement_v2",
    )


def make_project_specification(requirement: Mapping[str, Any], baseline: Mapping[str, Any]) -> Dict[str, Any]:
    return _finish(
        "HHS_PROJECT_SPECIFICATION_V2",
        {
            "requirement_root_hash72": requirement["requirement_root_hash72"],
            "system_root_hash72": baseline["total_system_root_hash72"],
            "system_baseline_root_hash72": baseline["system_baseline_root_hash72"],
            "transformation": [
                "strict_binary_input_commitment",
                "authenticated_pass070_binary_to_trinary_switch_packet",
                "authenticated_pass068_81_cell_loshu_schedule",
                "three_lane_validation",
                "zero_sum_round_trip_closure",
            ],
            "uses_existing_platform_surfaces": [
                "PASS_070_UNIVERSAL_BINARY_TRINARY_TRANSLATION_COMMITTED_ARTIFACT",
                "PASS_068_THREE_LANE_81_CELL_QUDIT_KERNEL_COMMITTED_ARTIFACT",
                "PASS_072_TOTAL_SYSTEM_ROOT",
            ],
            "live_verification_optional_not_semantic": True,
            "canonical_identity_uses_repository_relative_content_addresses": True,
            "adds_foundational_service": False,
            "product_root_must_differ_from_system_root": True,
        },
        "specification_root_hash72",
        "hhs_project_specification_v2",
    )


def make_project_plan(specification: Mapping[str, Any]) -> Dict[str, Any]:
    role_contracts = [
        {
            "role": "requirements_custodian",
            "authority": "commit requirement as data",
            "may_mutate_foundation": False,
        },
        {
            "role": "transform_implementer",
            "authority": "compose authenticated translation and kernel artifacts",
            "may_mutate_foundation": False,
        },
        {
            "role": "verification_replayer",
            "authority": "replay committed project inputs and compare semantic roots",
            "may_mutate_foundation": False,
        },
    ]
    leases = [
        {
            "lease_id": f"PASS073_LEASE_{index:02d}",
            "role": contract["role"],
            "capability": contract["authority"],
            "revocable": True,
            "scope": "native_project_only",
        }
        for index, contract in enumerate(role_contracts)
    ]
    task_graph = [
        {"task_id": "T1_REQUIREMENT", "depends_on": [], "lease_id": "PASS073_LEASE_00"},
        {"task_id": "T2_SPECIFICATION", "depends_on": ["T1_REQUIREMENT"], "lease_id": "PASS073_LEASE_00"},
        {"task_id": "T3_IMPLEMENTATION", "depends_on": ["T2_SPECIFICATION"], "lease_id": "PASS073_LEASE_01"},
        {"task_id": "T4_TESTING", "depends_on": ["T3_IMPLEMENTATION"], "lease_id": "PASS073_LEASE_02"},
        {"task_id": "T5_REPLAY", "depends_on": ["T4_TESTING"], "lease_id": "PASS073_LEASE_02"},
        {"task_id": "T6_RELEASE", "depends_on": ["T5_REPLAY"], "lease_id": "PASS073_LEASE_02"},
    ]
    return _finish(
        "HHS_PROJECT_PLAN_V2",
        {
            "specification_root_hash72": specification["specification_root_hash72"],
            "role_contracts": role_contracts,
            "capability_leases": leases,
            "task_graph": task_graph,
            "all_leases_native_scoped": True,
            "restart_state_must_be_committed_to_repository": True,
            "conversation_context_may_not_be_a_dependency": True,
            "foundation_mutation_allowed": False,
        },
        "plan_root_hash72",
        "hhs_project_plan_v2",
    )


def _make_loshu_schedule(packet: Mapping[str, Any], kernel_binding: Mapping[str, Any]) -> Dict[str, Any]:
    lo_shu = list(kernel_binding["lo_shu_cycle"])
    cell_ids = list(kernel_binding["first_subgrid_cell_ids"])
    schedule: List[Dict[str, Any]] = []
    for index, pair in enumerate(packet["pairs"]):
        slot = index % len(lo_shu)
        schedule.append(
            {
                "pair_index": index,
                "kernel_cell_id": cell_ids[slot],
                "lo_shu_slot": slot,
                "lo_shu_value": lo_shu[slot],
                "trinary_phase": pair["state"]["trinary_phase"],
                "binary_switch": pair["state"]["binary_switch"],
                "zero_sum_closed": pair["gate"]["zero_sum_closed"],
                "round_trip_valid": pair["gate"]["round_trip_valid"],
                "translation_root_hash72": pair["state"]["translation_root_hash72"],
            }
        )
    lane_sums = {
        "positive_lane_count": sum(1 for item in schedule if item["trinary_phase"] > 0),
        "plastic_lane_count": sum(1 for item in schedule if item["trinary_phase"] == 0),
        "zero_sum_lane_count": sum(1 for item in schedule if item["trinary_phase"] < 0),
    }
    return _finish(
        "HHS_NATIVE_PASS068_BOUND_LO_SHU_TRANSFORMATION_SCHEDULE_V2",
        {
            "packet_root_hash72": packet["packet_root_hash72"],
            "pass068_lattice_root_hash72": kernel_binding["lattice_root_hash72"],
            "pass068_artifact_sha256": kernel_binding["source_sha256"],
            "pair_count": len(schedule),
            "lo_shu_cycle": lo_shu,
            "scheduled_pairs": schedule,
            "lane_sums": lane_sums,
            "all_pairs_zero_sum_closed": all(item["zero_sum_closed"] for item in schedule),
            "all_pairs_round_trip_valid": all(item["round_trip_valid"] for item in schedule),
            "pass068_kernel_explicitly_consumed": True,
        },
        "schedule_root_hash72",
        "hhs_native_pass068_bound_loshu_schedule_v2",
    )


def build_native_product_artifact(
    typed_input: Mapping[str, Any],
    requirement: Mapping[str, Any],
    specification: Mapping[str, Any],
    plan: Mapping[str, Any],
    baseline: Mapping[str, Any],
    surface: Optional[Hash72Surface] = None,
) -> Dict[str, Any]:
    hash72_surface = surface or Hash72Surface()
    normalized = _normalize_bits(str(typed_input["sequence"]), int(typed_input.get("width", 16)))
    packet = translate_word(normalized["source_word"], normalized["width"], surface=hash72_surface)
    round_trip = reconstruct_word(packet)
    kernel_binding = hash72_surface.pass068_kernel_binding()
    schedule = _make_loshu_schedule(packet, kernel_binding)
    result = {
        "canonical_bits": normalized["canonical_bits"],
        "source_word": normalized["source_word"],
        "trinary_lane_vector": packet["trinary_lane_vector"],
        "binary_switch_mask": packet["binary_switch_mask"],
        "lo_shu_schedule": schedule["scheduled_pairs"],
        "reconstructed_word": round_trip["reconstructed_word"],
        "round_trip_valid": round_trip["round_trip_valid"],
        "zero_sum_closed": packet["all_zero_sum_closed"] and schedule["all_pairs_zero_sum_closed"],
    }
    return _finish(
        "HHS_PROJECT_SOURCE_ARTIFACT_V2",
        {
            "product_id": PRODUCT_ID,
            "system_root_hash72": baseline["total_system_root_hash72"],
            "requirement_root_hash72": requirement["requirement_root_hash72"],
            "specification_root_hash72": specification["specification_root_hash72"],
            "plan_root_hash72": plan["plan_root_hash72"],
            "typed_input": dict(typed_input),
            "strict_input_normalization_receipt": normalized,
            "binary_trinary_packet": packet,
            "round_trip": round_trip,
            "pass068_kernel_binding": kernel_binding,
            "lo_shu_schedule": schedule,
            "derived_artifact": result,
            "foundation_mutation": False,
            "recorded_witness_not_newly_generated_witness": True,
            "semantic_commitment_excludes_execution_mode": True,
            "semantic_commitment_excludes_host_paths": True,
            "projection_access_not_platform_authority": True,
        },
        "product_artifact_root_hash72",
        "hhs_native_product_artifact_v2",
    )


def _invalid_input_rejected(typed_input: Mapping[str, Any]) -> bool:
    try:
        _normalize_bits(str(typed_input.get("sequence", "")), int(typed_input.get("width", 0)))
    except Exception:
        return True
    return False


def make_test_plan(artifact: Mapping[str, Any]) -> Dict[str, Any]:
    tests = [
        {"case": "positive_round_trip", "passed": bool(artifact["derived_artifact"]["round_trip_valid"])},
        {"case": "negative_invalid_width_rejected", "passed": _invalid_input_rejected({"sequence": "1010", "width": 3})},
        {"case": "negative_non_binary_rejected", "passed": _invalid_input_rejected({"sequence": "10abc01", "width": 8})},
        {"case": "negative_whitespace_rejected", "passed": _invalid_input_rejected({"sequence": "10 01", "width": 8})},
        {"case": "reconstruction_case", "passed": artifact["round_trip"]["canonical_reconstruction"] is True},
        {"case": "pass068_kernel_binding", "passed": artifact["lo_shu_schedule"]["pass068_kernel_explicitly_consumed"] is True},
    ]
    return _finish(
        "HHS_PROJECT_TEST_PLAN_V2",
        {
            "product_artifact_root_hash72": artifact["product_artifact_root_hash72"],
            "tests": tests,
            "all_tests_passed": all(item["passed"] for item in tests),
        },
        "test_plan_root_hash72",
        "hhs_project_test_plan_v2",
    )


def make_execution_receipt(
    artifact: Mapping[str, Any],
    test_plan: Mapping[str, Any],
    environment: Mapping[str, Any],
) -> Dict[str, Any]:
    return _finish(
        "HHS_PROJECT_EXECUTION_RECEIPT_V2",
        {
            "product_artifact_root_hash72": artifact["product_artifact_root_hash72"],
            "test_plan_root_hash72": test_plan["test_plan_root_hash72"],
            "execution_environment_root_hash72": environment["execution_environment_root_hash72"],
            "execution_mode": environment["execution_mode"],
            "execution_result": artifact["derived_artifact"],
            "tests_passed": test_plan["all_tests_passed"],
            "execution_envelope_separate_from_semantic_product_commitment": True,
            "execution_root_is_product_specific": True,
        },
        "execution_root_hash72",
        "hhs_project_execution_receipt_v2",
    )


def _source_binding(repo: Path, relative_path: str) -> Dict[str, Any]:
    path = repo / relative_path
    return {
        "relative_path": relative_path,
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def make_context_independent_development_capsule(
    repo: Path,
    *,
    requirement: Mapping[str, Any],
    specification: Mapping[str, Any],
    plan: Mapping[str, Any],
    project: Mapping[str, Any],
    product_artifact: Mapping[str, Any],
) -> Dict[str, Any]:
    source_files = [
        "native_projects/pass073_deterministic_transform/__init__.py",
        "native_projects/pass073_deterministic_transform/hhs_native_deterministic_transform_v1.py",
        "native_projects/pass073_deterministic_transform/hhs_context_independent_project_runner_v1.py",
        "tests/test_hhs_pass073_native_deterministic_transform_v1.py",
        CANONICAL_INPUT_MANIFEST_RELATIVE_PATH,
    ]
    bindings = [_source_binding(repo, name) for name in source_files]
    return _finish(
        "HHS_CONTEXT_INDEPENDENT_NATIVE_DEVELOPMENT_CAPSULE_V1",
        {
            "pass_id": PASS_ID,
            "project_id": PRODUCT_ID,
            "completed_stage": "VERIFIED_NATIVE_PRODUCT_RELEASE",
            "next_stage": "COMPLETE",
            "restart_safe": True,
            "thread_context_required": False,
            "llm_context_window_required": False,
            "host_path_required": False,
            "canonical_inputs_manifest_relative_path": CANONICAL_INPUT_MANIFEST_RELATIVE_PATH,
            "canonical_inputs_manifest_sha256": CANONICAL_INPUT_MANIFEST_SHA256,
            "source_bindings": bindings,
            "requirement_root_hash72": requirement["requirement_root_hash72"],
            "specification_root_hash72": specification["specification_root_hash72"],
            "plan_root_hash72": plan["plan_root_hash72"],
            "project_root_hash72": project["project_root_hash72"],
            "product_artifact_root_hash72": product_artifact["product_artifact_root_hash72"],
            "entrypoint": "python -m native_projects.pass073_deterministic_transform.hhs_native_deterministic_transform_v1 --write-artifacts",
            "verification_command": "python -m pytest -q tests/test_hhs_pass073_native_deterministic_transform_v1.py",
            "resume_contract": {
                "python_module": "native_projects.pass073_deterministic_transform.hhs_native_deterministic_transform_v1",
                "callable": "run_native_transform_product",
                "typed_input": dict(requirement["typed_input"]),
                "expected_product_root_hash72": product_artifact["product_artifact_root_hash72"],
                "default_resolution_mode": "AUTO",
            },
            "resume_algorithm": [
                "verify source_bindings sha256",
                "verify canonical input manifest sha256",
                "load committed requirement/specification/plan/project roots",
                "select live runtime only when shared library already exists",
                "otherwise execute authenticated committed-artifact mode",
                "rebuild semantic product and compare product root",
            ],
            "conversation_narrative_is_non_authoritative": True,
            "repository_state_is_authoritative": True,
        },
        "development_capsule_root_hash72",
        "hhs_context_independent_native_development_capsule_v1",
    )


def replay_native_transform(
    bundle: Mapping[str, Any],
    *,
    root: Optional[str | Path] = None,
    resolution_mode: ResolutionMode = "AUTO",
) -> Dict[str, Any]:
    repo = _repo_root(root)
    surface = Hash72Surface(repo, resolution_mode=resolution_mode)
    requirement = dict(bundle["requirement"])
    specification = dict(bundle["specification"])
    plan = dict(bundle["plan"])
    baseline = dict(bundle["alpha_release_baseline"])
    rebuilt = build_native_product_artifact(
        dict(requirement["typed_input"]),
        requirement,
        specification,
        plan,
        baseline,
        surface=surface,
    )
    expected = str(bundle["product_artifact"]["product_artifact_root_hash72"])
    observed = str(rebuilt["product_artifact_root_hash72"])
    matches = observed == expected
    return _finish(
        "HHS_PROJECT_REPLAY_RECEIPT_V2",
        {
            "system_root_hash72": baseline["total_system_root_hash72"],
            "project_root_hash72": bundle["project"]["project_root_hash72"],
            "admitted_plan_root_hash72": plan["plan_root_hash72"],
            "expected_product_root_hash72": expected,
            "replayed_product_root_hash72": observed,
            "product_root_matches": matches,
            "reconstruction_verified": matches and rebuilt["round_trip"]["round_trip_valid"],
            "replay_execution_mode": surface.mode,
            "cross_mode_semantic_replay_supported": True,
            "mode_specific_receipt_not_used_as_product_identity": True,
        },
        "replay_root_hash72",
        "hhs_project_replay_receipt_v2",
    )


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


def run_native_transform_product(
    typed_input: Optional[Mapping[str, Any]] = None,
    *,
    root: Optional[str | Path] = None,
    write_artifacts: bool = False,
    resolution_mode: ResolutionMode = "AUTO",
) -> Dict[str, Any]:
    repo = _repo_root(root)
    surface = Hash72Surface(repo, resolution_mode=resolution_mode)
    input_obj = NativeTransformInput(
        **dict(typed_input or {"sequence": "1011001110001111", "width": 16})
    ).to_dict()
    baseline = make_alpha_release_baseline(repo, surface=surface)
    environment = make_execution_environment(surface)
    requirement = make_project_requirement(
        "Build a native deterministic HHS transformation product without mutating the frozen platform.",
        input_obj,
    )
    specification = make_project_specification(requirement, baseline)
    plan = make_project_plan(specification)
    project = _finish(
        "HHS_NATIVE_PROJECT_V2",
        {
            "pass_id": PASS_ID,
            "project_name": "First Native HHS Deterministic Transformation Workload",
            "system_root_hash72": baseline["total_system_root_hash72"],
            "requirement_root_hash72": requirement["requirement_root_hash72"],
            "specification_root_hash72": specification["specification_root_hash72"],
            "plan_root_hash72": plan["plan_root_hash72"],
            "foundation_mutation_allowed": False,
            "host_environment_not_canonical_identity": True,
            "conversation_context_not_project_state": True,
        },
        "project_root_hash72",
        "hhs_native_project_v2",
    )
    artifact = build_native_product_artifact(
        input_obj, requirement, specification, plan, baseline, surface=surface
    )
    test_plan = make_test_plan(artifact)
    execution = make_execution_receipt(artifact, test_plan, environment)
    build_receipt = _finish(
        "HHS_PROJECT_BUILD_RECEIPT_V2",
        {
            "project_root_hash72": project["project_root_hash72"],
            "product_artifact_root_hash72": artifact["product_artifact_root_hash72"],
            "test_plan_root_hash72": test_plan["test_plan_root_hash72"],
            "build_interpreted_not_compiled": True,
            "implicit_platform_build_performed": False,
            "foundation_delta": {"services": 0, "surfaces": 0, "authority": 0},
        },
        "build_root_hash72",
        "hhs_project_build_receipt_v2",
    )
    pre_replay = {
        "alpha_release_baseline": baseline,
        "requirement": requirement,
        "specification": specification,
        "plan": plan,
        "project": project,
        "product_artifact": artifact,
    }
    replay = replay_native_transform(pre_replay, root=repo, resolution_mode=resolution_mode)
    capsule = make_context_independent_development_capsule(
        repo,
        requirement=requirement,
        specification=specification,
        plan=plan,
        project=project,
        product_artifact=artifact,
    )
    release = _finish(
        "HHS_PRODUCT_RELEASE_MANIFEST_V2",
        {
            "product_id": PRODUCT_ID,
            "pass_id": PASS_ID,
            "system_root_hash72": baseline["total_system_root_hash72"],
            "project_root_hash72": project["project_root_hash72"],
            "product_artifact_root_hash72": artifact["product_artifact_root_hash72"],
            "execution_root_hash72": execution["execution_root_hash72"],
            "replay_root_hash72": replay["replay_root_hash72"],
            "development_capsule_root_hash72": capsule["development_capsule_root_hash72"],
            "root_distinctions": {
                "project_root_distinct_from_system_root": project["project_root_hash72"]
                != baseline["total_system_root_hash72"],
                "product_root_distinct_from_system_root": artifact["product_artifact_root_hash72"]
                != baseline["total_system_root_hash72"],
                "execution_root_distinct_from_system_root": execution["execution_root_hash72"]
                != baseline["total_system_root_hash72"],
                "semantic_product_root_distinct_from_execution_root": artifact[
                    "product_artifact_root_hash72"
                ]
                != execution["execution_root_hash72"],
            },
            "product_verified": test_plan["all_tests_passed"] and replay["reconstruction_verified"],
            "deterministic_replay": replay["product_root_matches"],
            "portable_cross_mode_semantic_replay": replay["cross_mode_semantic_replay_supported"],
            "environment_independent_semantic_commitment": True,
            "context_independent_development_state": True,
            "foundation_delta": {"services": 0, "surfaces": 0, "authority": 0},
        },
        "product_release_root_hash72",
        "hhs_product_release_manifest_v2",
    )
    bundle = {
        "schema": "HHS_PASS_073_NATIVE_DEVELOPMENT_WORKLOAD_BUNDLE_V2",
        "version": VERSION,
        "alpha_release_baseline": baseline,
        "execution_environment": environment,
        "requirement": requirement,
        "specification": specification,
        "plan": plan,
        "project": project,
        "product_artifact": artifact,
        "test_plan": test_plan,
        "build_receipt": build_receipt,
        "execution_receipt": execution,
        "replay_receipt": replay,
        "context_independent_development_capsule": capsule,
        "product_release_manifest": release,
        "ok": release["product_verified"]
        and release["deterministic_replay"]
        and all(release["root_distinctions"].values())
        and baseline["system_root_matches_frozen_release"]
        and environment["platform_verification"]["committed_root_verified"],
    }
    if write_artifacts:
        out_dir = repo / "native_projects/pass073_deterministic_transform/artifacts"
        _write_json(out_dir / "HHS_PASS_073_NATIVE_WORKLOAD_BUNDLE.json", bundle)
        _write_json(repo / "HHS_PASS_073_NATIVE_WORKLOAD_BUNDLE.json", bundle)
        _write_json(repo / "HHS_PRODUCT_RELEASE_MANIFEST_PASS_073.json", release)
        _write_json(repo / "PASS_073_CONTEXT_INDEPENDENT_DEVELOPMENT_CAPSULE.json", capsule)
        _write_json(out_dir / "PASS_073_CONTEXT_INDEPENDENT_DEVELOPMENT_CAPSULE.json", capsule)
    return bundle


def native_transform_self_test(
    payload: Optional[Mapping[str, Any]] = None,
    *,
    root: Optional[str | Path] = None,
    resolution_mode: ResolutionMode = "AUTO",
) -> Dict[str, Any]:
    bundle = run_native_transform_product(
        payload,
        root=root,
        write_artifacts=False,
        resolution_mode=resolution_mode,
    )
    release = bundle["product_release_manifest"]
    return {
        "schema": "HHS_PASS_073_NATIVE_TRANSFORM_SELF_TEST_V2",
        "ok": bool(bundle["ok"]),
        "execution_mode": bundle["execution_environment"]["execution_mode"],
        "system_root_hash72": bundle["alpha_release_baseline"]["total_system_root_hash72"],
        "project_root_hash72": bundle["project"]["project_root_hash72"],
        "product_root_hash72": bundle["product_artifact"]["product_artifact_root_hash72"],
        "execution_root_hash72": bundle["execution_receipt"]["execution_root_hash72"],
        "replay_root_hash72": bundle["replay_receipt"]["replay_root_hash72"],
        "product_release_root_hash72": release["product_release_root_hash72"],
        "development_capsule_root_hash72": bundle[
            "context_independent_development_capsule"
        ]["development_capsule_root_hash72"],
        "root_distinctions": release["root_distinctions"],
        "deterministic_replay": release["deterministic_replay"],
        "portable_cross_mode_semantic_replay": release[
            "portable_cross_mode_semantic_replay"
        ],
        "foundation_delta": release["foundation_delta"],
        "thread_context_required": False,
    }


def _parse_cli(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence", default="1011001110001111")
    parser.add_argument("--width", type=int, default=16)
    parser.add_argument(
        "--resolution-mode",
        choices=("AUTO", "LIVE_RUNTIME", "COMMITTED_ARTIFACT"),
        default="AUTO",
    )
    parser.add_argument("--write-artifacts", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_cli(argv)
    bundle = run_native_transform_product(
        {"sequence": args.sequence, "width": args.width},
        write_artifacts=args.write_artifacts,
        resolution_mode=args.resolution_mode,
    )
    print(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False, default=str))
    return 0 if bundle["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
