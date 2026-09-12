"""Focused exact tests for Pass 219 SPI Scalar Projection Registry v1."""
from __future__ import annotations

from fractions import Fraction
import json

from hhs_spi_scalar_projection_registry_v1 import (
    AUDITED_MAIN_SHA,
    CLOSED,
    IMPLEMENTED,
    MISSING_PROJECTION,
    NONE,
    NOT_EMITTED,
    OPEN,
    PROJECTION_ONLY,
    PROVEN,
    SYMBOLIC,
    VERIFIED,
    ProjectionProof,
    SPIProjectionError,
    SPIUnsupportedDomain,
    build_registry,
    coverage_manifest,
    divisibility_receipts,
    dyadic_fixed_point,
    equality_discrepancy,
    exact_real_surd_power,
    generator_mod_fixed_point,
    harmonicode_ast_binding,
    m2_factorization,
    scalar_reciprocal_units,
    spi_q_v1,
    spi_shell,
    source_coverage,
    surd_squared_projection,
    t3_factorization,
    t3b_modular_receipts,
    t6_projection,
    u0_projection,
    validate_registry,
)


def _raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__} from {fn.__name__}")


def test_main_anchor():
    assert AUDITED_MAIN_SHA == "2def7910b99046821f34e1446bcec33ca4fd4090"


def test_registry_valid():
    result = validate_registry()
    assert result["ok"], result
    assert result["proof_count"] >= 25
    assert result["coverage"][PROVEN] >= 20
    assert result["coverage"][SYMBOLIC] >= 1
    assert result["coverage"][MISSING_PROJECTION] >= 1


def test_projection_boundary():
    registry = build_registry()
    assert all(p.authority == PROJECTION_ONLY for p in registry.values())
    assert all(p.canonical_admission is False for p in registry.values())
    assert all(p.lost_information for p in registry.values())


def test_missing_loss_fails_closed():
    _raises(
        SPIProjectionError,
        ProjectionProof,
        proof_id="BAD",
        source_expression="x",
        profile="BAD",
        premises=(),
        domain="x",
        derivation=("x",),
        result=1,
        modulus=None,
        residual=0,
        lost_information=(),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
    )


def test_no_float_boundary():
    _raises(SPIProjectionError, spi_q_v1, 2.0)
    _raises(SPIProjectionError, t6_projection, 2.0)


def test_t1_exact():
    for P in (2, 3, 5, 7, 11, 13, 97, 101, Fraction(5, 2)):
        witness = spi_q_v1(P)
        assert witness["residual"] == 0
        assert witness["correction"] == 1
    _raises(SPIUnsupportedDomain, spi_q_v1, 0)


def test_t2_orientations_and_tower():
    plus = spi_shell(11, 1)
    minus = spi_shell(11, -1)
    assert plus["tower_residual"] == minus["tower_residual"] == 0
    assert plus["unit_discrepancy"] == minus["unit_discrepancy"] == 0
    assert (plus["p"], plus["q"]) == (Fraction(10), Fraction(12))
    assert (minus["p"], minus["q"]) == (Fraction(12), Fraction(10))
    assert (plus["p"], plus["q"]) != (minus["p"], minus["q"])
    for d in range(-5, 6):
        witness = spi_shell(19, d)
        assert witness["tower_residual"] == 0
        assert witness["unit_discrepancy"] == witness["factored_discrepancy"]


def test_t3_factorization_and_divisibility():
    for t in range(-12, 13):
        assert t3_factorization(t)["residual"] == 0
    for m in range(-12, 13):
        assert m2_factorization(m)["residual"] == 0
    for t in range(1, 13):
        for m in range(1, 13):
            assert divisibility_receipts(t, m)["ok"]


def test_t3b_receipts():
    for P in (2, 3, 5, 7, 11, 13, 97, 101):
        r = t3b_modular_receipts(P)
        assert r["cubic_residue"] == 0
        assert r["square_residue"] == 1
        assert r["square_minus_unit_residue"] == 0
    _raises(SPIUnsupportedDomain, t3b_modular_receipts, 1)


def test_t4_projection_only():
    witness = scalar_reciprocal_units(3, 5, 7, 11)
    assert witness["AB_reciprocal"] == 1
    assert witness["xy_reciprocal"] == 1
    _raises(SPIUnsupportedDomain, scalar_reciprocal_units, 0, 1, 1, 1)


def test_t5_affine_and_profiles():
    for A, B in ((2, 3), (5, 7), (Fraction(3, 2), Fraction(9, 4))):
        assert equality_discrepancy(A, B)["residual"] == 0
    dyadic = dyadic_fixed_point(5)
    assert dyadic["A"] == dyadic["B"] == Fraction(25, 2)
    assert dyadic["F"] == dyadic["target"] == 24
    assert dyadic["residual"] == 0
    generator = generator_mod_fixed_point(5)
    assert generator["residual"] == generator["modulus"] == 25
    assert generator["residue_class"] == 0


def test_t6_primitive_closure():
    witness = t6_projection(2)
    assert witness["alpha"] == 1
    assert witness["beta"] == 2
    assert witness["gamma"] == 3
    assert witness["pythagorean_residual"] == 0
    assert witness["u72"] == 1
    assert witness["first_branch"] == 2
    assert witness["first_branch_residual"] == 0
    _raises(SPIUnsupportedDomain, t6_projection, 0)
    _raises(SPIUnsupportedDomain, t6_projection, 1)


def test_surd_squared_coordinates():
    witness = surd_squared_projection(2)
    assert witness["N"] == 1
    assert witness["D"] == 1
    assert witness["ratio"] == witness["alpha"] == 1
    assert witness["residual"] == 0
    _raises(SPIUnsupportedDomain, surd_squared_projection, 1)


def test_exact_root_profile():
    assert exact_real_surd_power(2, 12, 72) == 64
    assert exact_real_surd_power(72, 72, 144) == 72**2
    _raises(SPIUnsupportedDomain, exact_real_surd_power, 2, 12, 71)
    _raises(SPIUnsupportedDomain, exact_real_surd_power, -2, 12, 72)


def test_u0_closed():
    witness = u0_projection()
    assert witness["root_index"] == 12
    assert witness["outer_power"] == 72
    assert witness["numerator"] == 64
    assert witness["denominator"] == 64
    assert witness["result"] == 1
    assert witness["residual"] == 0


def test_phase_symbols_not_collapsed():
    registry = build_registry()
    t6 = registry["SPI-T6"]
    assert "Pi" in t6.source_expression
    assert "O" not in t6.source_expression
    assert "Pi phase-label identity" in t6.lost_information


def test_open_obligations_isolated():
    registry = build_registry()
    o2 = registry["SPI-O2-MATRIX"]
    o3 = registry["SPI-O3-PROVENANCE"]
    assert o2.proof_status == OPEN and o2.coverage_state == SYMBOLIC
    assert o3.proof_status == OPEN and o3.coverage_state == MISSING_PROJECTION
    assert o2.receipt_status == o3.receipt_status == NOT_EMITTED
    assert o2.implementation_status != IMPLEMENTED
    assert o3.implementation_status != IMPLEMENTED


def test_exact_boundary_literal():
    registry = build_registry()
    literal = registry["SPI-O3-LITERAL"]
    assert literal.result == Fraction(179971179971, 1000000)
    assert literal.proof_status == CLOSED
    assert literal.receipt_status == VERIFIED


def test_receipts_deterministic():
    a = build_registry()
    b = build_registry()
    assert {k: v.receipt_sha256() for k, v in a.items()} == {k: v.receipt_sha256() for k, v in b.items()}


def test_harmonicode_ast_binding():
    binding = harmonicode_ast_binding("b²=(c²-a²)²/(2u⁷²)=(Pi-b²+b⁴-Pi)/(c²-b²)==c²-a²")
    assert binding["source_spans_preserved"] is True
    assert binding["nodes"]
    assert binding["nodes"][0]["ordered_symbol_identity_preserved"] is True


def test_source_coverage_fail_closed():
    known = source_coverage("b²=(c²-a²)²/(2u⁷²)=(Pi-b²+b⁴-Pi)/(c²-b²)==c²-a²")
    assert known["node_count"] == 1
    assert known["covered_node_count"] == 1
    assert "SPI-T6" in known["nodes"][0]["proof_ids"]

    unknown = source_coverage("UNREGISTERED_SCALAR_EDGE=17")
    assert unknown["node_count"] == 1
    assert unknown["covered_node_count"] == 0
    assert unknown["nodes"][0]["coverage_state"] == MISSING_PROJECTION


def test_manifest():
    manifest = coverage_manifest()
    assert manifest["validation"]["ok"] is True
    assert manifest["validation"]["proof_count"] == len(manifest["proofs"])
    assert manifest["native_authority_references"][0]["rule"].startswith("A=P=B")
    assert manifest["architectural_rule"].startswith("scalar calculus is downstream")


def main() -> None:
    tests = [
        test_main_anchor,
        test_registry_valid,
        test_projection_boundary,
        test_missing_loss_fails_closed,
        test_no_float_boundary,
        test_t1_exact,
        test_t2_orientations_and_tower,
        test_t3_factorization_and_divisibility,
        test_t3b_receipts,
        test_t4_projection_only,
        test_t5_affine_and_profiles,
        test_t6_primitive_closure,
        test_surd_squared_coordinates,
        test_exact_root_profile,
        test_u0_closed,
        test_phase_symbols_not_collapsed,
        test_open_obligations_isolated,
        test_exact_boundary_literal,
        test_receipts_deterministic,
        test_harmonicode_ast_binding,
        test_source_coverage_fail_closed,
        test_manifest,
    ]
    results = []
    for fn in tests:
        try:
            fn()
            results.append({"name": fn.__name__, "passed": True})
        except Exception as exc:
            results.append({"name": fn.__name__, "passed": False, "error": f"{type(exc).__name__}: {exc}"})
    report = {
        "schema": "HHS_SPI_SCALAR_PROJECTION_TEST_REPORT_V1",
        "count": len(results),
        "passed": sum(1 for row in results if row["passed"]),
        "failed": sum(1 for row in results if not row["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
