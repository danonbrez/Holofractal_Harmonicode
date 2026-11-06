"""Regression checks for the non-authoritative Modules 27–72 exact probes."""
from hhs_runtime.hhs_pass220_modules27_72_exact_probes_v1 import (
    CHECKS, EXPLICIT_OPEN, MODULES, execute, matrix_product,
)

def test_exact_probe_families():
    for _, (_, checker) in CHECKS.items():
        checker()

def test_no_false_full_module_or_vm81_admission():
    result = execute()
    assert len(MODULES) == 46
    assert all(c["status"] == "PASS" for c in result["checks"])
    assert all(state in ("OPEN", "NOT_FULLY_VERIFIED")
               for state in result["module_status"].values())
    assert set(result["explicit_open_gates"]) == {str(m) for m in EXPLICIT_OPEN}
    assert result["whole_course_proved"] is False
    assert result["canonical_vm81_admission"] is False
    assert result["hash72_minted"] is False
    assert result["hash216_minted"] is False

def test_matrix_contraction_is_strict():
    try:
        matrix_product([[1,2,3]], [[1,2],[3,4]])
    except ValueError as exc:
        assert "axis mismatch" in str(exc)
    else:
        raise AssertionError("must reject incompatible tensor axes")
