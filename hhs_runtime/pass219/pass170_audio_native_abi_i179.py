"""Pass219 I179 native admissibility binding for the Pass170 audio operation.

The C membrane is not a second token verifier, operation engine, receipt minter,
or persistence path. Pass190 verifies the signed capability first. This module
then binds that verified admission to inherited harmonic-time/audio ECC,
raw5184 audio hydration availability, the internal post-quantum-oriented
security signal, and receipt replay before any public audio side effect runs.
"""
from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_reality_to_manifold_translation_v1 import (
    make_harmonic_time_audio_witness,
    make_non_silent_security_policy,
)

SCHEMA = "HHS_PASS170_AUDIO_NATIVE_SECURITY_BINDING_I179_V1"
REPLAY_SCHEMA = "HHS_PASS170_AUDIO_NATIVE_REPLAY_BINDING_I179_V1"
OPERATION_ID = "public.audio_language.feedback.run"
AUDIO_CAPABILITY_SCOPE = "pass170.audio_language.feedback"
NATIVE_SYMBOL = "hhs_exact_pass219_audio_security_transport_admit"
NATIVE_VERSION_SYMBOL = "hhs_exact_pass219_audio_security_transport_version"
RAW5184_SYMBOL = "hhs_exact_pass219_audio5184_hydrate"
LIBRARY_ENV = "HHS_PASS170_AUDIO_NATIVE_LIB"
HHS_EXACT_STATUS_OK = 0
HASH72_LEN = 72
HASH72_STRLEN = 73


class Pass170AudioNativeABIError(RuntimeError):
    pass


class _Witness(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("signed_capability_verified", ctypes.c_uint32),
        ("capability_scope_bound", ctypes.c_uint32),
        ("raw5184_audio_hydration_bound", ctypes.c_uint32),
        ("harmonic_time_audio_ecc_required", ctypes.c_uint32),
        ("harmonic_time_audio_ecc_valid", ctypes.c_uint32),
        ("internal_pq_oriented_signal_required", ctypes.c_uint32),
        ("internal_pq_oriented_signal_valid", ctypes.c_uint32),
        ("receipt_replay_binding_required", ctypes.c_uint32),
        ("auxiliary_persistence_only", ctypes.c_uint32),
        ("public_crypto_primitive", ctypes.c_uint32),
        ("standardized_pq_crypto_claim", ctypes.c_uint32),
        ("independent_key_or_kem_authority", ctypes.c_uint32),
        ("canonical_vm81_mutation_authority", ctypes.c_uint32),
        ("new_hash72_mint_authority", ctypes.c_uint32),
        ("hash216_persistence_authority", ctypes.c_uint32),
        ("floating_point_canonical_authority", ctypes.c_uint32),
        ("binding_hash72", ctypes.c_char * HASH72_STRLEN),
    ]


class _Admission(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("admitted", ctypes.c_uint32),
        ("signed_capability_bound", ctypes.c_uint32),
        ("raw5184_audio_hydration_bound", ctypes.c_uint32),
        ("harmonic_time_audio_ecc_bound", ctypes.c_uint32),
        ("internal_pq_oriented_signal_bound", ctypes.c_uint32),
        ("receipt_replay_binding_bound", ctypes.c_uint32),
        ("auxiliary_persistence_only", ctypes.c_uint32),
        ("public_crypto_primitive", ctypes.c_uint32),
        ("standardized_pq_crypto_claim", ctypes.c_uint32),
        ("independent_key_or_kem_authority", ctypes.c_uint32),
        ("canonical_vm81_mutation_authority", ctypes.c_uint32),
        ("new_hash72_mint_authority", ctypes.c_uint32),
        ("hash216_persistence_authority", ctypes.c_uint32),
        ("floating_point_canonical_authority", ctypes.c_uint32),
        ("binding_hash72", ctypes.c_char * HASH72_STRLEN),
    ]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_library_path() -> Path:
    explicit = os.environ.get(LIBRARY_ENV)
    if explicit:
        return Path(explicit).expanduser().resolve()
    root = _repo_root() / "hhs_runtime" / "builds"
    names = (
        ("hhs_runtime.dll",) if sys.platform.startswith("win")
        else (("libhhs_runtime.dylib",) if sys.platform == "darwin" else ("libhhs_runtime.so",))
    )
    return root / names[0]


def _load_library(path: str | Path | None = None) -> tuple[ctypes.CDLL, Path, int]:
    selected = Path(path).expanduser().resolve() if path is not None else _default_library_path()
    if not selected.is_file():
        raise Pass170AudioNativeABIError(f"HHS_PASS170_AUDIO_NATIVE_ABI_REQUIRED:{selected}")
    try:
        library = ctypes.CDLL(str(selected))
    except OSError as exc:
        raise Pass170AudioNativeABIError(
            f"HHS_PASS170_AUDIO_NATIVE_ABI_LOAD_FAILED:{selected}:{exc}"
        ) from exc
    for symbol in (NATIVE_SYMBOL, NATIVE_VERSION_SYMBOL, RAW5184_SYMBOL):
        if not hasattr(library, symbol):
            raise Pass170AudioNativeABIError(f"HHS_PASS170_AUDIO_NATIVE_SYMBOL_MISSING:{symbol}")
    version_fn = getattr(library, NATIVE_VERSION_SYMBOL)
    version_fn.argtypes = []
    version_fn.restype = ctypes.c_uint32
    version = int(version_fn())
    admit_fn = getattr(library, NATIVE_SYMBOL)
    admit_fn.argtypes = [ctypes.POINTER(_Witness), ctypes.POINTER(_Admission)]
    admit_fn.restype = ctypes.c_int
    return library, selected, version


def _temporal_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    manifest = payload.get("audio_manifest")
    manifest_map = dict(manifest) if isinstance(manifest, Mapping) else {}
    temporal = manifest_map.get("temporal")
    temporal_map = dict(temporal) if isinstance(temporal, Mapping) else {}
    for key in ("sample_index", "sample_rate", "frame_window_samples", "latency_ticks", "phase_modulus"):
        if key in manifest_map and key not in temporal_map:
            temporal_map[key] = manifest_map[key]
    return temporal_map


def _ecc_witness(payload: Mapping[str, Any]) -> dict[str, Any]:
    temporal = _temporal_manifest(payload)
    witness = make_harmonic_time_audio_witness(
        sample_index=int(temporal.get("sample_index", 179971)),
        sample_rate=temporal.get("sample_rate", "48000/1"),
        frame_window_samples=int(temporal.get("frame_window_samples", 144)),
        latency_ticks=int(temporal.get("latency_ticks", 72)),
        phase_modulus=int(temporal.get("phase_modulus", 72)),
    )
    if witness.get("schema") != "HHS_HARMONIC_TIME_AUDIO_PHASE_ECC_WITNESS_V1":
        raise Pass170AudioNativeABIError("HHS_PASS170_AUDIO_ECC_SCHEMA_MISMATCH")
    if witness.get("harmonic_time_valid") is not True:
        raise Pass170AudioNativeABIError("HHS_PASS170_AUDIO_ECC_INVALID")
    return witness


def _policy_valid() -> bool:
    policy = make_non_silent_security_policy()
    evidence = policy.get("required_evidence")
    return (
        policy.get("terminal_output_sufficient") is False
        and isinstance(evidence, list)
        and "harmonic_time_audio_coherence_when_temporal" in evidence
    )


def _binding_hash72(
    *,
    capability_admission: Mapping[str, Any],
    payload: Mapping[str, Any],
    ecc: Mapping[str, Any],
) -> str:
    manifest = payload.get("audio_manifest")
    manifest_map = dict(manifest) if isinstance(manifest, Mapping) else {}
    ecc_kernel = ecc.get("kernel_witness")
    ecc_kernel_map = dict(ecc_kernel) if isinstance(ecc_kernel, Mapping) else {}
    digest = make_hash72_kernel_witness(
        "HHS_PASS170_AUDIO_NATIVE_SECURITY_BINDING_I179_V1",
        {
            "operation_id": OPERATION_ID,
            "principal": capability_admission.get("principal"),
            "required_scope": capability_admission.get("required_scope"),
            "token_hash72": capability_admission.get("token_hash72"),
            "manifest_hash72": manifest_map.get("manifest_hash72"),
            "harmonic_time_audio_ecc_digest72": ecc_kernel_map.get("digest72") or ecc_kernel_map.get("digest"),
            "raw5184_audio_hydration_bound": True,
            "internal_pq_oriented_signal": True,
            "receipt_replay_binding_required": True,
            "public_crypto_primitive": False,
            "standardized_pq_crypto_claim": False,
            "independent_key_or_kem_authority": False,
        },
        width=HASH72_LEN,
    ).digest
    if len(digest) != HASH72_LEN:
        raise Pass170AudioNativeABIError("HHS_PASS170_AUDIO_BINDING_HASH72_LENGTH_INVALID")
    return digest


def _invoke_exact_gate(
    *,
    binding_hash72: str,
    library_path: str | Path | None = None,
) -> dict[str, Any]:
    library, selected, version = _load_library(library_path)
    witness = _Witness()
    witness.struct_size = ctypes.sizeof(_Witness)
    witness.version = version
    witness.signed_capability_verified = 1
    witness.capability_scope_bound = 1
    witness.raw5184_audio_hydration_bound = 1
    witness.harmonic_time_audio_ecc_required = 1
    witness.harmonic_time_audio_ecc_valid = 1
    witness.internal_pq_oriented_signal_required = 1
    witness.internal_pq_oriented_signal_valid = 1
    witness.receipt_replay_binding_required = 1
    witness.auxiliary_persistence_only = 1
    witness.public_crypto_primitive = 0
    witness.standardized_pq_crypto_claim = 0
    witness.independent_key_or_kem_authority = 0
    witness.canonical_vm81_mutation_authority = 0
    witness.new_hash72_mint_authority = 0
    witness.hash216_persistence_authority = 0
    witness.floating_point_canonical_authority = 0
    witness.binding_hash72 = binding_hash72.encode("utf-8")

    result = _Admission()
    fn = getattr(library, NATIVE_SYMBOL)
    status = int(fn(ctypes.byref(witness), ctypes.byref(result)))
    if status != HHS_EXACT_STATUS_OK or result.admitted != 1:
        raise Pass170AudioNativeABIError(
            f"HHS_PASS170_AUDIO_NATIVE_ADMISSION_REJECTED:status={status}:admitted={int(result.admitted)}"
        )
    result_hash = bytes(result.binding_hash72).split(b"\0", 1)[0].decode("utf-8")
    if result_hash != binding_hash72:
        raise Pass170AudioNativeABIError("HHS_PASS170_AUDIO_NATIVE_BINDING_HASH_MISMATCH")
    return {
        "native_library": str(selected),
        "native_symbol": NATIVE_SYMBOL,
        "native_version": version,
        "binding_hash72": result_hash,
        "admitted": True,
        "signed_capability_bound": bool(result.signed_capability_bound),
        "raw5184_audio_hydration_bound": bool(result.raw5184_audio_hydration_bound),
        "harmonic_time_audio_ecc_bound": bool(result.harmonic_time_audio_ecc_bound),
        "internal_pq_oriented_signal_bound": bool(result.internal_pq_oriented_signal_bound),
        "receipt_replay_binding_bound": bool(result.receipt_replay_binding_bound),
        "auxiliary_persistence_only": bool(result.auxiliary_persistence_only),
        "public_crypto_primitive": bool(result.public_crypto_primitive),
        "standardized_pq_crypto_claim": bool(result.standardized_pq_crypto_claim),
        "independent_key_or_kem_authority": bool(result.independent_key_or_kem_authority),
        "canonical_vm81_mutation_authority": bool(result.canonical_vm81_mutation_authority),
        "new_hash72_mint_authority": bool(result.new_hash72_mint_authority),
        "hash216_persistence_authority": bool(result.hash216_persistence_authority),
        "floating_point_canonical_authority": bool(result.floating_point_canonical_authority),
    }


def admit_audio_native_transport(
    capability_admission: Mapping[str, Any],
    payload: Mapping[str, Any],
    *,
    library_path: str | Path | None = None,
) -> dict[str, Any]:
    if capability_admission.get("required_scope") != AUDIO_CAPABILITY_SCOPE:
        raise Pass170AudioNativeABIError("HHS_PASS170_AUDIO_NATIVE_SCOPE_NOT_BOUND")
    if capability_admission.get("pass190_verifier_reused") is not True:
        raise Pass170AudioNativeABIError("HHS_PASS170_AUDIO_NATIVE_SIGNED_ADMISSION_NOT_PROVEN")
    if not _policy_valid():
        raise Pass170AudioNativeABIError("HHS_PASS170_AUDIO_INTERNAL_SECURITY_POLICY_INVALID")
    ecc = _ecc_witness(payload)
    binding_hash72 = _binding_hash72(
        capability_admission=capability_admission,
        payload=payload,
        ecc=ecc,
    )
    native = _invoke_exact_gate(binding_hash72=binding_hash72, library_path=library_path)
    ecc_kernel = ecc.get("kernel_witness")
    ecc_kernel_map = dict(ecc_kernel) if isinstance(ecc_kernel, Mapping) else {}
    return {
        "schema": SCHEMA,
        "operation_id": OPERATION_ID,
        "required_scope": AUDIO_CAPABILITY_SCOPE,
        "principal": capability_admission.get("principal"),
        "binding_hash72": binding_hash72,
        "harmonic_time_audio_ecc_schema": ecc.get("schema"),
        "harmonic_time_audio_ecc_valid": True,
        "harmonic_time_audio_ecc_digest72": ecc_kernel_map.get("digest72") or ecc_kernel_map.get("digest"),
        "internal_pq_oriented_signal": True,
        "internal_pq_oriented_signal_public_crypto": False,
        "raw5184_audio_hydration_bound": True,
        "receipt_replay_binding_required": True,
        "native": native,
        "new_capability_authority": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
    }


def admit_audio_native_replay(
    capability_admission: Mapping[str, Any],
    *,
    receipt_hash72: str,
    original_security_binding: Mapping[str, Any],
    library_path: str | Path | None = None,
) -> dict[str, Any]:
    if capability_admission.get("required_scope") != AUDIO_CAPABILITY_SCOPE:
        raise Pass170AudioNativeABIError("HHS_PASS170_AUDIO_REPLAY_SCOPE_NOT_BOUND")
    original = str(original_security_binding.get("binding_hash72") or "")
    if len(original) != HASH72_LEN:
        raise Pass170AudioNativeABIError("HHS_PASS170_AUDIO_REPLAY_ORIGINAL_BINDING_INVALID")
    replay_hash = make_hash72_kernel_witness(
        "HHS_PASS170_AUDIO_NATIVE_REPLAY_BINDING_I179_V1",
        {
            "operation_id": OPERATION_ID,
            "receipt_hash72": receipt_hash72,
            "original_binding_hash72": original,
            "replay_principal": capability_admission.get("principal"),
            "replay_token_hash72": capability_admission.get("token_hash72"),
            "required_scope": AUDIO_CAPABILITY_SCOPE,
            "reexecuted": False,
        },
        width=HASH72_LEN,
    ).digest
    native = _invoke_exact_gate(binding_hash72=replay_hash, library_path=library_path)
    return {
        "schema": REPLAY_SCHEMA,
        "operation_id": OPERATION_ID,
        "receipt_hash72": receipt_hash72,
        "original_binding_hash72": original,
        "replay_binding_hash72": replay_hash,
        "principal": capability_admission.get("principal"),
        "reexecuted": False,
        "native": native,
        "new_capability_authority": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "AUDIO_CAPABILITY_SCOPE",
    "LIBRARY_ENV",
    "NATIVE_SYMBOL",
    "OPERATION_ID",
    "Pass170AudioNativeABIError",
    "SCHEMA",
    "admit_audio_native_replay",
    "admit_audio_native_transport",
]
