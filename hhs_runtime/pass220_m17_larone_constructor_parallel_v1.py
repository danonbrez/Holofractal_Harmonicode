"""Read-only Pass220 M17 phase crosswalk using inherited RML4 rotation semantics."""
from __future__ import annotations

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    expected_product_phase, CHANNELS,
)
from hhs_runtime.pass219.phase_geometry_learning import (
    PHASE_MODULUS, QUARTER_CYCLE, HALF_CYCLE,
)

ADDRESSES = ("111", "100", "101", "001", "110", "010", "011", "000")
REGISTERS = (8, 17, 26, 35, 44, 53, 62, 71)
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19)
RESIDUES = tuple(p % 8 for p in PRIMES)
SCHEMA = "HHS_PASS220_M17_LARONE_CONSTRUCTOR_PARALLEL_CANDIDATE_V1"

class CrosswalkFailure(ValueError):
    pass

def witness(addresses=ADDRESSES, registers=REGISTERS):
    # Freeze inputs before admission. No caller-owned mutable witness members.
    addresses = tuple(addresses)
    registers = tuple(registers)
    if addresses != ADDRESSES or registers != REGISTERS:
        raise CrosswalkFailure("ORDERED_PHASE_SOURCE_DRIFT")
    if PHASE_MODULUS != 72 or QUARTER_CYCLE != 18 or HALF_CYCLE != 36:
        raise CrosswalkFailure("INHERITED_RML4_PHASE_CONTRACT_DRIFT")
    if CHANNELS != ("x", "y", "z", "w", "xy", "yx", "zw", "wz"):
        raise CrosswalkFailure("INHERITED_CHANNEL_ORDER_DRIFT")
    if any(type(r) is not int or r % 9 != 8 for r in registers):
        raise CrosswalkFailure("X_SQUARED_PHASE_RESIDUE_DRIFT")
    if any(registers[(i+2)%8] != expected_product_phase(registers[i], 1)
           for i in range(8)):
        raise CrosswalkFailure("INHERITED_RML4_QUARTER_TURN_DRIFT")
    if any(registers[(i+4)%8] != (registers[i]+HALF_CYCLE)%PHASE_MODULUS
           for i in range(8)):
        raise CrosswalkFailure("INHERITED_RML4_HALF_TURN_DRIFT")
    return {
        "schema": SCHEMA, "addresses": addresses, "phase72": registers,
        "prime_index": PRIMES, "prime_residue8": RESIDUES,
        "phase_operator": "SIGNED_IMAGINARY_PHASE_ROTATION",
        "loop_closed": True, "phase_residue_mod9": 8,
        "parallel_with_existing_constructor": True,
        "candidate_only": True, "hash72_minted": False, "hash216_minted": False,
    }
