import pytest

from hhs_runtime.pass219.scalar_projection_proofs import (
    PARAMETERIZED,
    PROOFS,
    PROOF_BY_EXPRESSION,
    SYMBOL_COVERAGE,
    TYPED_NONSCALAR,
    UNSUPPORTED,
    build_scalar_projection_coverage,
    prove,
    validate_dependency_graph,
    verify_canonical_source,
)

CANONICAL = "(P^2/{(t^3-t=(P³-P/(P²-pq)=(t³-t)/∆=P²(MOD)(pq))=m^2-m)-(({{b^4,c^4,c^2-u^72},{c^2,5/u^((s==(b^(2c^2)c^b^4)^2)/(72P^2)),((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,(72*(pq+xy)))/Bt==AB/P^2==Sqrt[AB])==(AB/(pq+∆)-P^2)/(t^3-t)*u^72} where ∆/P=√(pq+u⁷²)^x²)/(NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4))=NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4)"


def scalar(expr):
    value = prove(expr)["result"]
    assert value["denominator"] == 1
    return value["numerator"]


def test_canonical_source_identity_and_tamper_fail_closed():
    identity = verify_canonical_source(CANONICAL)
    assert identity["verified"] is True
    assert identity["bytes"] == 632
    assert identity["sha256"] == "3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53"
    with pytest.raises(ValueError, match="CANONICAL_SOURCE_IDENTITY_MISMATCH"):
        build_scalar_projection_coverage(CANONICAL + " ")


def test_all_canonical_variable_tokens_receive_projection_classification():
    manifest = build_scalar_projection_coverage(CANONICAL)
    assert manifest["uncovered_symbols"] == []
    statuses = {entry["symbol"]: entry["status"] for entry in manifest["symbol_coverage"]}
    assert statuses["P"] == PARAMETERIZED
    assert statuses["t"] == UNSUPPORTED
    assert statuses["xy"] == TYPED_NONSCALAR
    assert statuses["u"] == TYPED_NONSCALAR


def test_primitive_and_loshu_polynomial_projection_dag():
    assert scalar("a^2") == 1
    assert scalar("b^2") == 2
    assert scalar("c^2") == 3
    assert scalar("b^4") == 4
    assert scalar("c^4") == 9
    assert scalar("b^6") == 8
    assert scalar("b^2+c^2") == 5
    assert scalar("b^4+c^2") == 7
    assert scalar("b^2*c^2") == 6
    loshu = [
        [scalar("b^4"), scalar("c^4"), scalar("b^2")],
        [scalar("c^2"), scalar("b^2+c^2"), scalar("b^4+c^2")],
        [scalar("b^6"), scalar("a^2"), scalar("b^2*c^2")],
    ]
    assert loshu == [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    assert all(sum(row) == 15 for row in loshu)
    assert all(sum(loshu[r][c] for r in range(3)) == 15 for c in range(3))


def test_nested_polynomial_projection_chain_is_exact():
    assert scalar("c^2-b^2") == 1
    assert scalar("b^2*(c^2+b^2)") == 10
    assert scalar("(b^2*(c^2+b^2))-(c^2-b^2)") == 9
    assert scalar("Sqrt(c^4)") == 3
    assert scalar("((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)") == 3
    assert scalar("c^2*b^6-c^2") == 21
    assert scalar("(c^2*b^6-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4))") == 7


def test_72_and_5184_have_source_bound_proofs():
    assert scalar("b^6*c^4") == 72
    assert scalar("(b^(2*c^2)*c^(b^4))^2") == 5184
    assert scalar("72^2") == 5184
    assert scalar("64*81") == 5184
    assert scalar("36*144") == 5184


def test_projection_equality_never_collapses_native_identity():
    five_a = prove("d^2")
    five_b = prove("b^2+c^2")
    five_c = prove("b^2*c^2-a^2")
    assert five_a["result"] == five_b["result"] == five_c["result"]
    assert len({five_a["proof_id"], five_b["proof_id"], five_c["proof_id"]}) == 3
    for proof in (five_a, five_b, five_c):
        assert proof["projection_equality_implies_native_identity"] is False


def test_projection_only_phase_and_rational_theorems_are_scoped():
    assert scalar("u_phase^72") == 1
    assert scalar("I^4") == 1
    assert scalar("Delta") == 1
    assert scalar("P^2-p*q") == 1
    assert scalar("(A/B)*(B/A)") == 1
    assert prove("Delta")["domain"] == "PASS129_NONZERO_EXACT_RATIONAL"
    assert prove("u_phase^72")["projection_id"] == "PI-U-PHASE-v1"


def test_base_symbols_are_not_given_unlicensed_fixed_scalar_values():
    for symbol in ("a", "b", "c", "x", "y", "z", "w", "xy", "u", "I"):
        assert SYMBOL_COVERAGE[symbol] == TYPED_NONSCALAR
    for expression in ("a", "b", "c", "P", "t", "xy"):
        assert expression not in PROOF_BY_EXPRESSION


def test_proof_receipts_deterministic_and_non_authoritative():
    first = prove("b^6*c^4")
    second = prove("b^6*c^4")
    assert first["proof_sha256"] == second["proof_sha256"]
    assert first["proof_receipt_hash72"] == second["proof_receipt_hash72"]
    assert len(first["proof_receipt_hash72"]) == 72
    for key in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_mint_authority",
        "canonical_hash216_persistence_authority",
    ):
        assert first[key] is False


def test_manifest_is_deterministic_and_has_no_projection_holes():
    first = build_scalar_projection_coverage(CANONICAL)
    second = build_scalar_projection_coverage(CANONICAL)
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert first["manifest_receipt_hash72"] == second["manifest_receipt_hash72"]
    assert first["proof_count"] == len(PROOFS) == 35
    assert first["uncovered_symbols"] == []
    assert "5/1" in first["same_scalar_value_distinct_native_proof_groups"]
    assert "5184/1" in first["same_scalar_value_distinct_native_proof_groups"]


def test_dependency_graph_and_unknown_fixed_projection_fail_closed():
    validate_dependency_graph()
    with pytest.raises(KeyError, match="NO_FIXED_SCALAR_PROOF"):
        prove("t^3-t")
