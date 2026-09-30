import pytest

from hhs_runtime.pass219.scalar_projection_theorems import (
    FIXED,
    MULTIBRANCH,
    PARAMETERIZED,
    SYMBOLIC,
    TYPED_NONSCALAR,
    UNSUPPORTED,
    THEOREMS,
    build_theorem_manifest,
    explain_projection,
    source_bound_occurrences,
    validate_theorem_registry,
)

CANONICAL = "(P^2/{(t^3-t=(P³-P/(P²-pq)=(t³-t)/∆=P²(MOD)(pq))=m^2-m)-(({{b^4,c^4,c^2-u^72},{c^2,5/u^((s==(b^(2c^2)c^b^4)^2)/(72P^2)),((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,(72*(pq+xy)))/Bt==AB/P^2==Sqrt[AB])==(AB/(pq+∆)-P^2)/(t^3-t)*u^72} where ∆/P=√(pq+u⁷²)^x²)/(NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4))=NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4)"


def one(expr, projection_id=None):
    options = explain_projection(expr)
    if projection_id is None:
        assert len(options) == 1
        return options[0]
    matches = [item for item in options if item["projection_id"] == projection_id]
    assert len(matches) == 1
    return matches[0]


def test_registry_integrity_and_determinism():
    validate_theorem_registry()
    assert len(THEOREMS) == 87
    first = build_theorem_manifest(CANONICAL)
    second = build_theorem_manifest(CANONICAL)
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert first["manifest_receipt_hash72"] == second["manifest_receipt_hash72"]
    assert len(first["manifest_receipt_hash72"]) == 72


def test_source_bound_theorems_have_exact_spans():
    occurrences = source_bound_occurrences(CANONICAL)
    assert occurrences
    for record in occurrences:
        assert CANONICAL[record["start"]:record["end"]] == record["needle"]
        assert len(record["span_sha256"]) == 64


def test_primitive_projection_theorems_delegate_to_fixed_proofs():
    for expr, result in (("a^2", "1"), ("b^2", "2"), ("c^2", "3"), ("b^4", "4"), ("c^4", "9"), ("b^6", "8")):
        theorem = one(expr)
        assert theorem["projection_class"] == FIXED
        assert theorem["result_expression"] == result
        assert theorem["fixed_proof_id"].startswith("SPP")


def test_base_root_symbols_are_not_silently_scalarized():
    a = one("a")
    b = one("b")
    c = one("c")
    assert a["projection_class"] == MULTIBRANCH
    assert a["result_expression"] == "{+1,-1}"
    assert b["projection_class"] == SYMBOLIC
    assert c["projection_class"] == SYMBOLIC


def test_pass129_macro_projection_theorems():
    assert one("Delta", "PI-P129-DELTA-RATIONAL-v1")["result_expression"] == "1"
    assert one("p", "PI-P129-DELTA-RATIONAL-v1")["result_expression"] == "P-Delta"
    assert one("q", "PI-P129-DELTA-RATIONAL-v1")["result_expression"] == "P+Delta"
    assert one("p+q")["result_expression"] == "2P"
    assert one("q-p")["result_expression"] == "2Delta"
    assert one("p*q")["result_expression"] == "P^2-Delta^2"
    assert one("P^2-p*q")["result_expression"] == "1"


def test_t_m_are_not_solved_but_their_residues_have_projection_theorems():
    assert one("t^3-t")["result_expression"] == "Delta"
    assert one("m^2-m")["result_expression"] == "Delta"
    assert one("t")["projection_class"] == UNSUPPORTED
    assert one("m")["projection_class"] == UNSUPPORTED


def test_ordered_phase_coordinates_receive_parameterized_scalar_views_without_identity_collapse():
    for expr in ("x", "y", "z", "w", "xy", "yx", "zw", "wz"):
        options = explain_projection(expr)
        assert any(item["projection_class"] in {FIXED, PARAMETERIZED} for item in options)
        for item in options:
            assert item["projection_equality_implies_native_identity"] is False
    assert one("xy", "PI-HHCQ-8BASIS-INTEGER-v1")["result_expression"] == "ordered_product(x,y)"
    assert one("yx")["result_expression"] == "ordered_product(y,x)"


def test_macro_micro_equilibrium_projection():
    phi = one("Phi8=x+y+z+w+xy+yx+zw+wz")
    assert phi["result_expression"] == "b^2*P-(p+q)"
    p_hhcq = one("P", "PI-HHCQ-8BASIS-EQUILIBRIUM-v1")
    assert p_hhcq["result_expression"] == "(Phi8+p+q)/2"
    assert one("Phi8")["result_expression"] == "0"


def test_uce_and_prime_rational_projection_families_are_distinct():
    uce_a = one("A", "PI-UCE-INTEGER-SYMMETRIC-v1")
    phase10_a = one("A", "PI-HHCQ-PRIME-RATIONAL-v1")
    assert uce_a["result_expression"] == "P^2"
    assert phase10_a["result_expression"] == "P^2*(p/q)"
    assert one("A/B")["result_expression"] == "p^2/q^2"
    assert one("B/A")["result_expression"] == "q^2/p^2"
    assert one("(A/B)*(B/A)")["result_expression"] == "1"


def test_u_phase_is_distinct_from_native_u_and_proves_polynomial_consequences():
    assert one("u")["projection_class"] == TYPED_NONSCALAR
    assert one("u_phase^72")["result_expression"] == "1"
    assert one("c^2-u_phase^72")["result_expression"] == "2"
    assert one("72*(pq+xy)")["result_expression"] == "72*P^2"
    assert one("b^6-xy")["result_expression"] == "7"


def test_b2_u72_and_u0_exact_projection_chain():
    assert one("c^2-a^2")["result_expression"] == "2"
    assert one("(c^2-a^2)^2")["result_expression"] == "4"
    assert one("(c^2-a^2)^2/(2*u_phase^72)")["result_expression"] == "2"
    assert one("Pi-b^2+b^4-Pi")["result_expression"] == "2"
    assert one("(Pi-b^2+b^4-Pi)/(c^2-b^2)")["result_expression"] == "2"
    assert one("u_phase^0")["result_expression"] == "1"
    assert one("b^4*c^2")["result_expression"] == "12"
    assert one("Power(RealSurd(b^2,b^4*c^2),a^2)^(b^6*c^4)")["result_expression"] == "64"
    assert one("(b^6)^2")["result_expression"] == "64"
    assert one("Power(RealSurd(b^2,b^4*c^2),a^2)^(b^6*c^4)/(b^6)^2")["result_expression"] == "1"


def test_unresolved_full_symbolic_surfaces_fail_closed():
    for expr in ("s", "f", "At", "Bt", "Mod(f/u,72*(pq+xy))", "Delta/P=Sqrt(pq+u^72)^x^2"):
        item = one(expr)
        assert item["projection_class"] == UNSUPPORTED
        assert item["result_expression"] is None


def test_symbolic_constants_and_matrix_remain_exact_not_decimalized():
    assert one("Pi")["result_expression"] == "Pi"
    assert one("O")["result_expression"] == "O"
    assert one("E")["result_expression"] == "E"
    matrix = one("NcalcMatrixPower(...,4)")
    assert matrix["projection_class"] == SYMBOLIC
    assert matrix["result_expression"] == "exact_ordered_matrix_power_object"


def test_every_theorem_has_zero_canonical_authority():
    for theorem in THEOREMS:
        item = theorem.to_dict()
        assert item["source_rewrite_authorized"] is False
        assert item["canonical_vm81_mutation_authority"] is False
        assert item["canonical_hash72_mint_authority"] is False
        assert item["canonical_hash216_persistence_authority"] is False
        assert item["floating_point_canonical_authority"] is False


def test_unknown_projection_theorem_fails_closed():
    with pytest.raises(KeyError, match="NO_PROJECTION_THEOREM"):
        explain_projection("invented_scalar_projection")
