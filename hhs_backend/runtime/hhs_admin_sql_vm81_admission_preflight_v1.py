"""Read-only environmental admission capability probe for staged Lane 5 sources.

Does NOT assemble synthetic UQCEL values, mint credentials, or call the signed
VM81 mutator. Uses actual exported Pass219 runtime symbols to report prerequisites.
"""
from __future__ import annotations

import ctypes
from typing import Callable

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_python.runtime.hhs_pass219_lane5_unbounded_workload_scaling_bridge import _load_runtime

ML_DSA_65 = 1
SLH_DSA_SHA2_192S = 2


def inspect_staged_admission_prerequisites(
    staging: AdminStreamStaging,
    upload_id: str,
    owner: str,
    *,
    loader: Callable[[], ctypes.CDLL] = _load_runtime,
) -> dict[str, object]:
    record = staging.status(upload_id, owner)
    if record["state"] != "STAGED":
        raise ValueError("SIGNED_VM81_PREFLIGHT_REQUIRES_STAGED_SOURCE")

    lib = loader()
    symbols = (
        "hhs_exact_pass219_vm81_environment_version",
        "hhs_exact_pass219_vm81_environment_state",
        "hhs_exact_pass219_vm81_pqc_signature_provider_available",
        "hhs_exact_pass219_vm81_pqc_firewall_halted",
        "hhs_exact_pass219_vm81_environment_admit_signed",
    )
    if any(not hasattr(lib, symbol) for symbol in symbols):
        raise RuntimeError("SIGNED_VM81_NATIVE_SYMBOL_SET_INCOMPLETE")
    version = lib.hhs_exact_pass219_vm81_environment_version
    version.argtypes = []
    version.restype = ctypes.c_uint32
    state = lib.hhs_exact_pass219_vm81_environment_state
    state.argtypes = []
    state.restype = ctypes.c_uint32
    provider = lib.hhs_exact_pass219_vm81_pqc_signature_provider_available
    provider.argtypes = [ctypes.c_uint32]
    provider.restype = ctypes.c_uint32
    halted = lib.hhs_exact_pass219_vm81_pqc_firewall_halted
    halted.argtypes = []
    halted.restype = ctypes.c_uint32

    return {
        "schema": "HHS_ADMIN_STAGED_SIGNED_VM81_PREFLIGHT_V1",
        "upload_id": upload_id,
        "source_sha256": record["source_sha256"],
        "received_bytes": record["received_bytes"],
        "environment_native_version": int(version()),
        "environment_state": int(state()),
        "firewall_halted": bool(halted()),
        "ml_dsa_65_provider_available": provider(ML_DSA_65) == 1,
        "slh_dsa_sha2_192s_provider_available": provider(SLH_DSA_SHA2_192S) == 1,
        "signed_environmental_entrypoint_exported": True,
        "typed_source_constructor_bound": False,
        "authorized_parent_hash216_bound": False,
        "signed_vm81_admission_performed": False,
        "canonical_hash216_admitted": False,
        "next_gate": "TYPED_AUTHORIZED_SOURCE_TO_VM81_CONSTRUCTOR_AND_PARENT_REFERENCE",
    }
