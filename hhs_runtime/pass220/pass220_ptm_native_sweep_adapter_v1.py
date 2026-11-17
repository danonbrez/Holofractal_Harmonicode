"""Source-bound nine-state sweep adapter for the native P/t/m evaluator.

The caller must supply an executor that evaluates the unchanged original
GENERATOR_SOURCE for a chosen P,t,m and returns a 3x3 exact-rational matrix.
This module never substitutes host MatrixPower or fabricates matrix values.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from typing import Callable, Sequence

from hhs_runtime.pass220.pass220_ptm_exact_generator_witness_v1 import (
    GENERATOR_SOURCE, REFERENCE,
)

Grid = tuple[tuple[Fraction, ...], ...]
NativeExecutor = Callable[[str, str, int, int], Sequence[Sequence[Fraction]]]
SWEEP = tuple((t,m) for t in (24,25,26) for m in (247,248,249))
SOURCE_SHA256 = sha256(GENERATOR_SOURCE.encode("utf-8")).hexdigest()
REFERENCE_P = "Sqrt(3)"


class PtmExecutionError(RuntimeError):
    pass


def exact_matrix(value: Sequence[Sequence[Fraction]]) -> Grid:
    if len(value) != 3 or any(len(row) != 3 for row in value):
        raise PtmExecutionError("PTM_OUTPUT_NOT_3X3")
    out = []
    for row in value:
        converted = []
        for cell in row:
            if type(cell) is not Fraction:
                raise PtmExecutionError("PTM_OUTPUT_NOT_EXACT_RATIONAL")
            converted.append(cell)
        out.append(tuple(converted))
    return tuple(out)


def ratios(reference: Grid, current: Grid) -> tuple[tuple[str | None, ...], ...]:
    """Entrywise ratios; zero denominators stay explicit as None."""
    return tuple(tuple(
        str(current[i][j]/reference[i][j]) if reference[i][j] != 0 else None
        for j in range(3)) for i in range(3))


def sweep(executor: NativeExecutor | None, P: str = REFERENCE_P) -> dict:
    if executor is None:
        raise PtmExecutionError("NATIVE_PTM_EXECUTOR_NOT_BOUND")
    if type(P) is not str or not P:
        raise PtmExecutionError("PTM_P_OBJECT_SOURCE_REQUIRED")
    outputs = []
    for t,m in SWEEP:
        matrix = exact_matrix(executor(GENERATOR_SOURCE,P,t,m))
        outputs.append({"P":P,"t":t,"m":m,"matrix":matrix,
                        "ratios_to_supplied_reference":ratios(REFERENCE,matrix)})
    return {
        "source_sha256": SOURCE_SHA256,
        "P": P,
        "state_count": len(outputs),
        "native_evaluation": "EXECUTOR_SUPPLIED",
        "outputs": tuple(outputs),
    }


def serialize_exact(receipt: dict) -> dict:
    """JSON-compatible exact rational output: no float conversion."""
    return {
        "source_sha256": receipt["source_sha256"],
        "P":receipt["P"],
        "state_count":receipt["state_count"],
        "native_evaluation":receipt["native_evaluation"],
        "outputs":tuple({
            "P":r["P"],"t":r["t"],"m":r["m"],
            "matrix":tuple(tuple(str(v) for v in row) for row in r["matrix"]),
            "ratios_to_supplied_reference":r["ratios_to_supplied_reference"],
        } for r in receipt["outputs"]),
    }
