"""Read-only Lane 5 equivalence of parallel I073 generators for one exact P.

Lean module HHS.RecursiveBigIntGenerator establishes the abstract nesting
value theorem. This adapter checks concrete inherited I073 reconstruction
without asserting that a Lean proof receipt has been kernel-bound to this
runtime result or granting canonical VM81/Hash216 authority.
"""
from __future__ import annotations
from hashlib import sha256
import json

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    VM81_CELLS, bigint_to_offsets, offsets_to_bigint,
)
from hhs_runtime.hhs_pass220_i073_palindromic_rna_fibonacci_symbolic_tensor_v1 import (
    build_generator, validate_generator, reconstruct_serialized_state,
)

SCHEMA = "HHS_PASS220_I073_LEAN_PARALLEL_GENERATOR_EQUIVALENCE_V1"
LEAN_MODULE = "HHS.RecursiveBigIntGenerator"
LEAN_THEOREM = "parallel_generator_equivalence"

class GeneratorEquivalenceError(ValueError):
    pass


def compare_p_generators(P: int, *, first_depth: int = 0, second_depth: int = 1) -> dict:
    if isinstance(P, bool) or not isinstance(P, int) or P < 0:
        raise GeneratorEquivalenceError("P_EXACT_NONNEGATIVE_BIGINT_REQUIRED")
    if any(isinstance(d, bool) or not isinstance(d, int) or d < 0 or d > 1_000_000
           for d in (first_depth, second_depth)):
        raise GeneratorEquivalenceError("NESTING_DEPTH_INVALID")
    try:
        offsets = bigint_to_offsets(P, length=VM81_CELLS)
    except (ValueError, TypeError, OverflowError) as exc:
        raise GeneratorEquivalenceError("P_EXCEEDS_LOCAL_VM81_OFFSET_CAPACITY") from exc
    if offsets_to_bigint(offsets) != P:
        raise GeneratorEquivalenceError("P_INHERITED_BIGINT_ROUNDTRIP_FAILED")
    generators = tuple(build_generator(
        offsets=offsets, nesting_depth=d, fibonacci_depth=1
    ) for d in (first_depth, second_depth))
    if not all(validate_generator(g) is True for g in generators):
        raise GeneratorEquivalenceError("I073_GENERATOR_INVALID")
    reconstructed = tuple(reconstruct_serialized_state(g) for g in generators)
    if reconstructed[0] != reconstructed[1]:
        raise GeneratorEquivalenceError("RECONSTRUCTED_STATE_MISMATCH")
    roots = tuple(g["generator_root_sha256"] for g in generators)
    record = {
        "schema": SCHEMA,
        "sole_free_parameter": "P",
        "P_decimal": str(P),
        "lean_module": LEAN_MODULE,
        "lean_theorem": LEAN_THEOREM,
        "lean_kernel_proof_bound_to_runtime": False,
        "nesting_depths": (first_depth, second_depth),
        "distinct_generator_roots": roots[0] != roots[1],
        "generator_roots": roots,
        "reconstructed_5184_sha256": sha256(reconstructed[0].encode("utf-8")).hexdigest(),
        "same_exact_reconstruction": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    record["witness_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return record
