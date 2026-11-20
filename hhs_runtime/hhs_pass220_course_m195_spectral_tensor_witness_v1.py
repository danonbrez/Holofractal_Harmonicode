"""Module 195 exact ordered spectral-tensor witness (non-admitting).

This is an exact arithmetic audit, not a native HARMONICODE typed gate,
HNAN runtime execution, VM81 admission, Hash72 mint, or Hash216 receipt.
Preserves Module 194 V160 as a separate source-address/physics workstream.
"""
from __future__ import annotations
from hashlib import sha256
import json

SCHEMA = "HHS_PASS220_COURSE_M195_SPECTRAL_TENSOR_WITNESS_V1"
SOURCE = ("MatrixTimes(MatrixTimes({{2,-1,0},{0,1,-2},{-1,0,1}},"
          "-List(List(2,(-1),0),List(0,1,(-2)),List((-1),0,1))),m)"
          "/(25*x+6*x^2+x^3)==1/m")
M = ((2, -1, 0), (0, 1, -2), (-1, 0, 1))
ZERO = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
I = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
EXPECTED_K = ((-4, 3, -2), (-2, -1, 4), (3, -1, -1))
# Polynomial coefficient order: constant, x, x^2, x^3.
D = (0, 25, 6, 1)


def mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3))
                       for j in range(3)) for i in range(3))


def add(a, b):
    return tuple(tuple(a[i][j] + b[i][j] for j in range(3))
                 for i in range(3))


def scale(a, n):
    return tuple(tuple(n * v for v in row) for row in a)


def pmat_mul(a, b):
    out = [ZERO for _ in range(len(a) + len(b) - 1)]
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] = add(out[i + j], mm(ai, bj))
    return tuple(out)


def evaluate() -> dict:
    """Return a bounded exact witness; never claim native typed admission."""
    k = mm(M, scale(M, -1))  # Preserve ordered MatrixTimes(M,-M).
    assert k == EXPECTED_K
    k2, k3 = mm(k, k), mm(mm(k, k), k)
    ch = add(add(k3, scale(k2, 6)), scale(k, 25))
    # adj(xI-K) = K^2 + (x+6)K + (x^2+6x+25)I
    adj = (add(add(k2, scale(k, 6)), scale(I, 25)),
           add(k, scale(I, 6)), I)
    resolvent = pmat_mul((scale(k, -1), I), adj)
    target = tuple(scale(I, coeff) for coeff in D)
    residual = tuple(add(a, scale(b, -1)) for a, b in zip(resolvent, target))
    assert ch == ZERO and residual == (ZERO,) * 4
    result = {
        "schema": SCHEMA, "module": 195, "source": SOURCE,
        "source_sha256": sha256(SOURCE.encode("utf-8")).hexdigest(),
        "matrix_M": [list(row) for row in M],
        "ordered_operator_K": [list(row) for row in k],
        "denominator_coefficients_ascending": list(D),
        "spectral_roots": ["0", "-3+4I", "-3-4I"],
        "nonzero_spectral_magnitudes": [5, 5],
        "rank_K": 2, "null_vector": [1, 2, 1],
        "cayley_hamilton_residual": [list(row) for row in ch],
        "adjugate_residual_coefficients": [
            [list(row) for row in coefficient] for coefficient in residual
        ],
        "denominator_zero_guard": "HNAN_NATIVE_RUNTIME_GATE_REQUIRED",
        "hnan_gain_one_no_phase_write": "COURSE_CONTRACT_NOT_EXECUTED",
        "ordered_typed_equality": "OUTSTANDING_NATIVE_PROOF_OBLIGATION",
        "scalar_coercion_refutes_native_gate": False,
        "module194_v160_source_address_contract": "DISTINCT_UNCHANGED",
        "lane5_producer_provenance_verified": False,
        "canonical_vm81_admission": False, "hash72_minted": False,
        "hash216_minted": False, "native_hnan_executed": False,
    }
    # Candidate fingerprint, NOT Hash72 / Hash216 or runtime receipt.
    result["candidate_sha256"] = sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return result


if __name__ == "__main__":
    print(json.dumps(evaluate(), sort_keys=True, indent=2))
