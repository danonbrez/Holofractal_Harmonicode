"""Tests for HARMONICODE matrix/tensor-defined scalar projection rule v1."""
from __future__ import annotations

import json

from hhs_spi_defined_scalar_projection_rule_v1 import (
    PROFILE,
    SPIDefinedScalarProjectionError,
    defined_scalar_projection,
)


def _raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def _a2_receipt():
    branch = "(NcalcMatrixPower((M/J),4))^b⁴"
    edge = f"a²={branch}"
    return defined_scalar_projection(
        scalar_symbol="a²",
        scalar_proof_id="SPI-PROJ-0001",
        scalar_value=1,
        defining_expression=branch,
        equality_edge_source=edge,
        definition_kind="EXACT_SYMBOLIC_MATRIX_POWER",
        edge_id="HHCQ:E_a2:matrix-branch",
    )


def test_a2_matrix_definition_projects_to_one():
    receipt = _a2_receipt()
    assert receipt["profile"] == PROFILE
    assert receipt["result"] == {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    assert receipt["residual"] == {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1}
    assert receipt["matrix_or_tensor_host_evaluated"] is False
    assert receipt["native_substitution_authorized"] is False


def test_projection_keeps_native_authority_false():
    receipt = _a2_receipt()
    for key in (
        "canonical_admission_authority",
        "vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "canonical_persistence_authority",
        "floating_point_authority",
    ):
        assert receipt[key] is False


def test_arbitrary_matrix_without_definition_edge_fails():
    _raises(
        SPIDefinedScalarProjectionError,
        defined_scalar_projection,
        scalar_symbol="a²",
        scalar_proof_id="SPI-PROJ-0001",
        scalar_value=1,
        defining_expression="Matrix(M)",
        equality_edge_source="b²=Matrix(N)",
        definition_kind="ORDERED_MATRIX",
        edge_id="BAD",
    )


def test_float_scalar_fails_closed():
    _raises(
        SPIDefinedScalarProjectionError,
        defined_scalar_projection,
        scalar_symbol="a²",
        scalar_proof_id="SPI-PROJ-0001",
        scalar_value=1.0,
        defining_expression="Tensor(T)",
        equality_edge_source="a²=Tensor(T)",
        definition_kind="ORDERED_TENSOR",
        edge_id="BAD-FLOAT",
    )


def test_unknown_definition_kind_fails_closed():
    _raises(
        SPIDefinedScalarProjectionError,
        defined_scalar_projection,
        scalar_symbol="a²",
        scalar_proof_id="SPI-PROJ-0001",
        scalar_value=1,
        defining_expression="Something(X)",
        equality_edge_source="a²=Something(X)",
        definition_kind="ARBITRARY_SCALAR_COLLAPSE",
        edge_id="BAD-KIND",
    )


def test_receipt_deterministic():
    assert _a2_receipt() == _a2_receipt()


def main() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    results = []
    for test in tests:
        try:
            test()
            results.append({"name": test.__name__, "passed": True})
        except Exception as exc:
            results.append({"name": test.__name__, "passed": False, "error": f"{type(exc).__name__}: {exc}"})
    report = {
        "schema": "HHS_SPI_DEFINED_SCALAR_PROJECTION_RULE_TEST_REPORT_V1",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
