from hhs_runtime.harmonicode_directed_constraint_semantics_v1 import (
    formalize_source,
    validate_core_axioms,
)


def test_core_validation_passes_all_13_checks():
    report = validate_core_axioms()
    assert report["result"] == "PASS"
    assert report["check_count"] == 13
    assert all(report["checks"].values())
    assert report["unresolved_statement_count"] == 0


def test_rhs_is_constraint_source_and_lhs_is_dependent():
    result = formalize_source("AB=P^4")
    edge = result["directed_constraints"][0]
    assert edge["lhs_source"] == "AB"
    assert edge["rhs_source"] == "P^4"
    assert edge["dependency"] == "RHS_TO_LHS"
    assert edge["rhs_enforced_closure"] is True
    assert edge["lhs_dependent_manifold"] is True
    assert edge["local_asymmetry_generates_rhs"] is False


def test_ab_and_ba_remain_distinct_ordered_products():
    result = formalize_source("AB=P^4\nBA=P^4")
    nodes = [x for x in result["ordered_expressions"] if x["operator"] == "ORDERED_PRODUCT"]
    assert any(x["source"] == "AB" and x["reverse_source"] == "BA" for x in nodes)
    assert any(x["source"] == "BA" and x["reverse_source"] == "AB" for x in nodes)
    assert all(x["commutation_authorized"] is False for x in nodes)


def test_quotient_reciprocal_orientation_is_noncommutative():
    result = formalize_source("A/B≠B/A")
    nodes = [x for x in result["ordered_expressions"] if x["operator"] == "QUOTIENT"]
    assert any(x["source"] == "A/B" and x["reverse_source"] == "B/A" for x in nodes)
    assert any(x["source"] == "B/A" and x["reverse_source"] == "A/B" for x in nodes)
    assert all(x["reciprocal_noncommutative"] is True for x in nodes)


def test_nested_rationals_preserve_orthogonal_local_roles():
    result = formalize_source("((A/B)/(B/A))=P^4")
    nodes = [x for x in result["ordered_expressions"] if x["operator"] == "QUOTIENT"]
    parent = next(x for x in nodes if x["lhs_source"] == "A/B" and x["rhs_source"] == "B/A")
    assert parent["local_lhs_role"] == "LHS"
    assert parent["local_rhs_role"] == "RHS"
    assert parent["dependency"] == "RHS_TO_LHS"
    assert parent["local_asymmetry_generates_parent_closure"] is False


def test_metric_scalars_are_projection_witnesses_not_rewrites():
    result = formalize_source("a^2=1\nb^2=2\nc^2=3")
    projections = {x["native_source"]: x for x in result["scalar_projections"]}
    assert projections["a^2"]["projected_value"] == "1"
    assert projections["b^2"]["projected_value"] == "2"
    assert projections["c^2"]["projected_value"] == "3"
    for projection in projections.values():
        assert projection["projection"] == "pi_1D"
        assert projection["tensor_source_required"] is True
        assert projection["native_identity"] is False
        assert projection["substitution_authority"] is False


def test_equal_scalar_projection_does_not_create_native_identity():
    result = formalize_source("a^2=1\nx=1")
    projections = result["scalar_projections"]
    assert len(projections) == 1
    assert projections[0]["native_source"] == "a^2"
    assert result["authority"]["scalar_substitution_authority"] is False


def test_chain_dependency_is_right_to_left():
    result = formalize_source("X=Y=Z")
    pairs = [(x["lhs_source"], x["rhs_source"]) for x in result["directed_constraints"]]
    assert pairs == [("Y", "Z"), ("X", "Y")]


def test_local_asymmetry_never_promoted_to_global_closure_cause():
    result = formalize_source("AB=P^4\n((A/B)/(B/A))=P^4")
    assert all(x["local_asymmetry_generates_rhs"] is False for x in result["directed_constraints"])
    assert all(
        x["local_asymmetry_generates_parent_closure"] is False
        for x in result["ordered_expressions"]
    )
