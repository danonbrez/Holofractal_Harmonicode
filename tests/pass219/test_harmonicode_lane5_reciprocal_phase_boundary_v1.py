from hhs_runtime.harmonicode_lane5_reciprocal_phase_boundary_v1 import (
    DELTA_CANCEL_FORBIDDEN,
    DELTA_RECURRENCE,
    GAMMA_X,
    GLOBAL_DENOMINATOR,
    INFINITY_BOUNDARY,
    P_DELTA_FIXED_POINT,
    P_GENERATOR,
    P_NOT_INFINITY,
    P_SCALE_CLOSURE,
    PROHIBITED_REWRITES,
    RECIPROCAL_DELTA,
    RECIPROCAL_INFINITY,
    phase_gear,
    reciprocal_phase_chain,
    theorem_record,
    validate_t5184_002,
)


def test_reciprocal_chain_is_directional_not_scalar_inverse():
    chain = reciprocal_phase_chain()
    assert chain["source"] == "∞->∆->x=Γ_x"
    assert chain["edges"][0] == {
        "from": "∞", "to": "∆", "operator": "R", "ordered": True
    }
    assert chain["edges"][1] == {
        "from": "∆", "to": "x", "operator": "R", "ordered": True
    }
    assert chain["ordinary_inverse_semantics"] is False
    assert chain["involutive_reciprocal_assumed"] is False


def test_gamma_x_preserves_verbatim_phase_gear_and_order():
    gear = phase_gear()
    assert gear["source"] == GAMMA_X == "Γ_x=u^(18/72mod72)*u^36"
    assert gear["ordered_factors"] == ("u^(18/72mod72)", "u^36")
    assert gear["phase_fraction_source"] == "18/72mod72"
    assert gear["scalar_exponent_combination_authority"] is False
    assert gear["factor_reordering_authority"] is False


def test_core_equations_are_present_without_delta_cancellation():
    theorem = theorem_record()
    sources = {law["source"] for law in theorem["laws"]}
    for source in (
        GLOBAL_DENOMINATOR,
        P_GENERATOR,
        INFINITY_BOUNDARY,
        RECIPROCAL_INFINITY,
        RECIPROCAL_DELTA,
        P_NOT_INFINITY,
        P_SCALE_CLOSURE,
        DELTA_RECURRENCE,
        P_DELTA_FIXED_POINT,
        DELTA_CANCEL_FORBIDDEN,
    ):
        assert source in sources
    assert theorem["authority"]["delta_cancellation_authority"] is False


def test_p_and_infinity_remain_distinct_despite_shared_boundary_numerator():
    theorem = theorem_record()
    assert theorem["boundary_fixed_points"]["p_distinct_from_infinity"] is True
    assert theorem["boundary_fixed_points"]["delta_cancellable"] is False
    assert P_NOT_INFINITY in {law["source"] for law in theorem["laws"]}


def test_every_nested_object_keeps_the_same_universal_denominator():
    theorem = theorem_record()
    objects = theorem["nested_boundary_manifest"]["objects"]
    assert objects
    assert {item["global_denominator"] for item in objects} == {GLOBAL_DENOMINATOR}
    assert all(item["boundary_condition"] is True for item in objects)
    assert all(
        item["independent_normalization_authority"] is False
        for item in objects
    )


def test_prohibited_rewrites_cover_cancellation_identity_and_scalarization():
    theorem = theorem_record()
    pairs = {
        (item["source"], item["forbidden_target"])
        for item in theorem["prohibited_rewrites"]
    }
    assert pairs == set(PROHIBITED_REWRITES)
    assert ("(∞∆)/∆", "∞") in pairs
    assert ("P∆=∞∆", "P=∞") in pairs
    assert ("∆^-1*∆", "1") in pairs
    assert (
        "u^(18/72mod72)*u^36",
        "u^(18/72mod72+36)",
    ) in pairs


def test_1_52_serializer_is_inherited_not_reimplemented():
    theorem = theorem_record()
    binding = theorem["serializer_binding"]
    assert binding["result"] == "PASS"
    assert binding["transcription_operation"] == "transcribe_5184"
    assert binding["ingress_egress_same_operation"] is True
    assert binding["nested_payloads_remain_typed"] is True


def test_t5184_002_validation_passes_all_twenty_checks():
    report = validate_t5184_002()
    assert report["result"] == "PASS"
    assert report["check_count"] == 20
    assert all(report["checks"].values())
    assert report["law_count"] == 12
    assert report["prohibited_rewrite_count"] == 7
