from fractions import Fraction
import json
import subprocess
import sys

import pytest

from hhs_runtime.hhs_gfe_log_constraint_v1 import (
    EqualityGatedLogWitness,
    GFEConstraintError,
    execute_calibration_suite,
    execute_gfe_trace,
)


def test_log_is_defined_by_equality_gated_inverse_phase_witness():
    w = EqualityGatedLogWitness.construct(Fraction(5, 4)).to_dict()
    assert w["sigma"] == "Log_H(5/4|unit=1)"
    assert w["g_inverse"] == "4/5"
    assert w["numeric_projection_authorized"] is False
    assert w["floating_point_authority_paths"] == 0
    assert "E_H^(Log_H(5/4|unit=1))==5/4" in w["equality_gate_chain"]


def test_identity_log_closes_exactly():
    t = execute_gfe_trace(1, label="EQ")
    assert t["log_witness"]["sigma"] == "0"
    assert t["theta"] == t["rho"] == "0"
    assert t["overall_status"] == "VERIFIED_CLOSED"


def test_reciprocal_polynomial_and_dual_log_residues_close():
    t = execute_gfe_trace(Fraction(5, 4), label="NEQ")
    assert t["g_inverse"] == "4/5"
    assert t["reciprocal_closure_residue"] == "0"
    assert t["polynomialized_residual"] == "0"
    assert t["dual_energy_cancellation_residue"] == "0"
    assert t["rho"] == "1/20"


def test_reciprocal_pair_has_equal_rho_but_distinct_theta():
    a = execute_gfe_trace(Fraction(3, 2))
    b = execute_gfe_trace(Fraction(2, 3))
    assert a["rho"] == b["rho"] == "1/6"
    assert a["theta"] != b["theta"]


def test_non_normalized_unit_is_not_silently_promoted_to_scalar_identity():
    t = execute_gfe_trace(Fraction(3, 1), unit=2)
    assert t["polynomialized_residual"] is None
    assert t["statuses"]["polynomialized_residual"] == "NOT_EVALUATED_NON_NORMALIZED_UNIT"
    assert t["overall_status"] == "CONDITIONALLY_CLOSED"


def test_float_boolean_zero_and_nonexact_inputs_rejected():
    for bad in [1.25, True, object()]:
        with pytest.raises(GFEConstraintError):
            execute_gfe_trace(bad)
    with pytest.raises(GFEConstraintError):
        execute_gfe_trace(0)
    with pytest.raises(GFEConstraintError):
        execute_gfe_trace(1, unit=0)


def test_suite_is_deterministic_and_all_normalized_cases_close():
    a = execute_calibration_suite()
    b = execute_calibration_suite()
    assert a == b
    assert a["all_closed"] is True
    assert a["reciprocal_pair_rho_equal"] is True
    assert a["floating_point_authority_paths"] == 0


def test_cli_surface_emits_replayable_json(tmp_path):
    out = tmp_path / "trace.json"
    proc = subprocess.run(
        [sys.executable, "-m", "hhs_runtime.hhs_gfe_log_constraint_v1", "--g", "5/4", "--output", str(out)],
        check=False, text=True, capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr
    disk = json.loads(out.read_text())
    stdout = json.loads(proc.stdout)
    assert disk == stdout
    assert disk["trace_root"]
