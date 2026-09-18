"""Exact native bridge for Pass 219 Lane 5 Pythagorean phase geometry 1.49."""
from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path
from typing import Any

SCHEMA = "HHS_PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_1_49_BRIDGE_V1"
LIBRARY_ENV = "HHS_PASS219_LANE5_P149_NATIVE_LIB"
OK = 0
VERSION = 0x00010031
PAIR_KIND = {"AB": 0, "XY": 1, "ZW": 2, "PQ": 3}

class Lane5PythagoreanPhaseGeometryError(RuntimeError):
    pass

class _Authority(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32), ("version", ctypes.c_uint32),
        ("namespace_id", ctypes.c_uint32), ("a2", ctypes.c_uint32),
        ("b2", ctypes.c_uint32), ("c2", ctypes.c_uint32), ("c4", ctypes.c_uint32),
        ("phase_cycle", ctypes.c_uint32), ("phase_quarter", ctypes.c_uint32),
        ("phase_half", ctypes.c_uint32), ("lo_shu_line_sum", ctypes.c_uint32),
        ("lo_shu_center", ctypes.c_uint32), ("pair_kind_count", ctypes.c_uint32),
        ("pass192_fibonacci_max_depth", ctypes.c_uint32),
        ("pythagorean_constant_projection_exact", ctypes.c_uint8),
        ("lo_shu_denominator_geometry_exact", ctypes.c_uint8),
        ("lo_shu_complement_involution_exact", ctypes.c_uint8),
        ("finite_corner_phase_correspondence_exact", ctypes.c_uint8),
        ("reciprocal_phase_involution_exact", ctypes.c_uint8),
        ("directional_pair_involution_exact", ctypes.c_uint8),
        ("shared_fourth_power_is_typed_projection", ctypes.c_uint8),
        ("pass192_fibonacci_schedule_reused", ctypes.c_uint8),
        ("candidate_only", ctypes.c_uint8),
        ("canonical_vm81_mutation_authority", ctypes.c_uint8),
        ("canonical_hash72_authority", ctypes.c_uint8),
        ("canonical_hash216_authority", ctypes.c_uint8),
        ("canonical_persistence_authority", ctypes.c_uint8),
        ("floating_point_canonical_authority", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 2),
    ]

class _Input(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32), ("version", ctypes.c_uint32),
        ("pair_kind", ctypes.c_uint32), ("orientation", ctypes.c_uint32),
        ("phase_slot", ctypes.c_uint32), ("lo_shu_cell_index", ctypes.c_uint32),
        ("fibonacci_depth", ctypes.c_uint32), ("projected_p4", ctypes.c_uint64),
    ]

class _Receipt(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32), ("version", ctypes.c_uint32),
        ("namespace_id", ctypes.c_uint32), ("pair_kind", ctypes.c_uint32),
        ("orientation", ctypes.c_uint32), ("inverse_orientation", ctypes.c_uint32),
        ("phase_slot", ctypes.c_uint32), ("inverse_phase_slot", ctypes.c_uint32),
        ("lo_shu_cell_index", ctypes.c_uint32), ("lo_shu_denominator", ctypes.c_uint32),
        ("inverse_lo_shu_cell_index", ctypes.c_uint32), ("inverse_lo_shu_denominator", ctypes.c_uint32),
        ("fibonacci_depth", ctypes.c_uint32), ("pass192_fibonacci_version", ctypes.c_uint32),
        ("a2", ctypes.c_uint32), ("b2", ctypes.c_uint32), ("c2", ctypes.c_uint32), ("c4", ctypes.c_uint32),
        ("projected_p4", ctypes.c_uint64), ("geometry_signature64", ctypes.c_uint64),
        ("pythagorean_identity_verified", ctypes.c_uint8),
        ("phase_involution_verified", ctypes.c_uint8), ("pair_involution_verified", ctypes.c_uint8),
        ("lo_shu_cell_verified", ctypes.c_uint8), ("lo_shu_complement_verified", ctypes.c_uint8),
        ("lo_shu_phase_half_turn_verified", ctypes.c_uint8), ("finite_phase_anchor_cell", ctypes.c_uint8),
        ("finite_phase_anchor_consistent", ctypes.c_uint8), ("continuation_cell", ctypes.c_uint8),
        ("fibonacci_depth_within_pass192", ctypes.c_uint8), ("shared_fourth_power_match", ctypes.c_uint8),
        ("collapse_candidate_admissible", ctypes.c_uint8), ("candidate_only", ctypes.c_uint8),
        ("canonical_mutation_authority", ctypes.c_uint8), ("canonical_hash72_authority", ctypes.c_uint8),
        ("canonical_hash216_authority", ctypes.c_uint8), ("canonical_persistence_authority", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 3),
    ]

def _default_library() -> Path:
    explicit=os.getenv(LIBRARY_ENV)
    if explicit:
        return Path(explicit).expanduser().resolve()
    name="hhs_runtime.dll" if sys.platform.startswith("win") else ("libhhs_runtime.dylib" if sys.platform=="darwin" else "libhhs_runtime.so")
    return Path(__file__).resolve().parents[1] / "builds" / name

def _load(path: str | Path | None=None) -> tuple[ctypes.CDLL,Path,_Authority]:
    selected=Path(path).expanduser().resolve() if path else _default_library()
    if not selected.is_file():
        raise Lane5PythagoreanPhaseGeometryError(f"P149_NATIVE_LIBRARY_REQUIRED:{selected}")
    lib=ctypes.CDLL(str(selected))
    for symbol in (
        "hhs_exact_pass219_lane5_pythagorean_phase_geometry_version",
        "hhs_exact_pass219_lane5_pythagorean_phase_geometry_authority",
        "hhs_exact_pass219_lane5_pythagorean_phase_project",
    ):
        if not hasattr(lib,symbol):
            raise Lane5PythagoreanPhaseGeometryError(f"P149_NATIVE_SYMBOL_MISSING:{symbol}")
    lib.hhs_exact_pass219_lane5_pythagorean_phase_geometry_version.restype=ctypes.c_uint32
    lib.hhs_exact_pass219_lane5_pythagorean_phase_geometry_authority.argtypes=[ctypes.POINTER(_Authority)]
    lib.hhs_exact_pass219_lane5_pythagorean_phase_geometry_authority.restype=ctypes.c_int
    lib.hhs_exact_pass219_lane5_pythagorean_phase_project.argtypes=[ctypes.POINTER(_Input),ctypes.POINTER(_Receipt)]
    lib.hhs_exact_pass219_lane5_pythagorean_phase_project.restype=ctypes.c_int
    if int(lib.hhs_exact_pass219_lane5_pythagorean_phase_geometry_version()) != VERSION:
        raise Lane5PythagoreanPhaseGeometryError("P149_NATIVE_VERSION_DRIFT")
    authority=_Authority()
    if int(lib.hhs_exact_pass219_lane5_pythagorean_phase_geometry_authority(ctypes.byref(authority))) != OK:
        raise Lane5PythagoreanPhaseGeometryError("P149_NATIVE_AUTHORITY_REJECTED")
    if not (
        authority.a2==1 and authority.b2==2 and authority.c2==3 and authority.c4==9
        and authority.phase_cycle==72 and authority.phase_half==36
        and authority.candidate_only==1
        and authority.canonical_vm81_mutation_authority==0
        and authority.canonical_hash72_authority==0
        and authority.canonical_hash216_authority==0
        and authority.canonical_persistence_authority==0
        and authority.floating_point_canonical_authority==0
    ):
        raise Lane5PythagoreanPhaseGeometryError("P149_NATIVE_AUTHORITY_DRIFT")
    return lib,selected,authority

def project_pythagorean_phase_geometry(
    *, pair_kind: str, orientation: int, phase_slot: int,
    lo_shu_cell_index: int, fibonacci_depth: int=10, projected_p4: int=9,
    library_path: str | Path | None=None,
) -> dict[str,Any]:
    if pair_kind not in PAIR_KIND:
        raise Lane5PythagoreanPhaseGeometryError("P149_PAIR_KIND_UNSUPPORTED")
    for value,label in ((orientation,"ORIENTATION"),(phase_slot,"PHASE"),(lo_shu_cell_index,"CELL"),(fibonacci_depth,"FIBONACCI_DEPTH"),(projected_p4,"PROJECTED_P4")):
        if isinstance(value,bool) or not isinstance(value,int):
            raise Lane5PythagoreanPhaseGeometryError(f"P149_{label}_EXACT_INTEGER_REQUIRED")
    lib,selected,_=_load(library_path)
    inp=_Input(ctypes.sizeof(_Input),VERSION,PAIR_KIND[pair_kind],orientation,phase_slot,lo_shu_cell_index,fibonacci_depth,projected_p4)
    receipt=_Receipt()
    status=int(lib.hhs_exact_pass219_lane5_pythagorean_phase_project(ctypes.byref(inp),ctypes.byref(receipt)))
    if status != OK:
        raise Lane5PythagoreanPhaseGeometryError(f"P149_NATIVE_PROJECTION_REJECTED:status={status}")
    authority={
        "candidate_only": bool(receipt.candidate_only),
        "canonical_vm81_mutation_authority": bool(receipt.canonical_mutation_authority),
        "canonical_hash72_authority": bool(receipt.canonical_hash72_authority),
        "canonical_hash216_authority": bool(receipt.canonical_hash216_authority),
        "canonical_persistence_authority": bool(receipt.canonical_persistence_authority),
        "floating_point_authority": False,
    }
    if authority != {
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }:
        raise Lane5PythagoreanPhaseGeometryError("P149_AUTHORITY_ESCALATION")
    return {
        "schema":SCHEMA,"result":"PASS","native_library":str(selected),
        "pair_kind":pair_kind,"orientation":int(receipt.orientation),
        "inverse_orientation":int(receipt.inverse_orientation),
        "phase_slot":int(receipt.phase_slot),"inverse_phase_slot":int(receipt.inverse_phase_slot),
        "lo_shu_cell_index":int(receipt.lo_shu_cell_index),"lo_shu_denominator":int(receipt.lo_shu_denominator),
        "inverse_lo_shu_cell_index":int(receipt.inverse_lo_shu_cell_index),
        "inverse_lo_shu_denominator":int(receipt.inverse_lo_shu_denominator),
        "fibonacci_depth":int(receipt.fibonacci_depth),"a2":int(receipt.a2),"b2":int(receipt.b2),
        "c2":int(receipt.c2),"c4":int(receipt.c4),"projected_p4":int(receipt.projected_p4),
        "geometry_signature64":int(receipt.geometry_signature64),
        "finite_phase_anchor_cell":bool(receipt.finite_phase_anchor_cell),
        "finite_phase_anchor_consistent":bool(receipt.finite_phase_anchor_consistent),
        "continuation_cell":bool(receipt.continuation_cell),
        "shared_fourth_power_match":bool(receipt.shared_fourth_power_match),
        "collapse_candidate_admissible":bool(receipt.collapse_candidate_admissible),
        "pythagorean_identity_verified":bool(receipt.pythagorean_identity_verified),
        "phase_involution_verified":bool(receipt.phase_involution_verified),
        "pair_involution_verified":bool(receipt.pair_involution_verified),
        "lo_shu_complement_verified":bool(receipt.lo_shu_complement_verified),
        "lo_shu_phase_half_turn_verified":bool(receipt.lo_shu_phase_half_turn_verified),
        "authority":authority,
    }
