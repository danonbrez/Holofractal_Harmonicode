from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "evidence/pass219/hhs_rational_p_manifold_lane5_v1.wl"
OUTPUT = ROOT / "evidence/pass219/hhs_rational_p_manifold_lane5_v1.output.json"
RECEIPT = ROOT / "evidence/pass219/hhs_rational_p_manifold_lane5_v1.receipt.json"


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_wolfram_receipt_binds_exact_source_and_output() -> None:
    receipt = json.loads(RECEIPT.read_text())
    assert receipt["schema"] == "HHS_PASS219_RATIONAL_P_MANIFOLD_LANE5_WOLFRAM_RECEIPT_V1"

    assert SOURCE.stat().st_size == receipt["source_bytes"] == 5404
    assert OUTPUT.stat().st_size == receipt["output_bytes"] == 1749
    assert _digest(SOURCE) == receipt["source_sha256"]
    assert _digest(OUTPUT) == receipt["output_sha256"]


def test_macro_rational_p_manifold_projection() -> None:
    for P in [Fraction(n) for n in range(-36, 37) if n != 0]:
        p = P - 1
        q = P + 1
        assert p + q == 2 * P
        assert q - p == 2
        assert p * q == P * P - 1
        correction = ((q - p) * P) / (p + q)
        assert correction == 1
        assert P * P == p * q + correction
        assert P == (p + q) / 2


def test_wolfram_positive_and_negative_guards() -> None:
    output = json.loads(OUTPUT.read_text())

    macro = output["macroTheorem"]
    assert macro["status"] == "PROVEN_EXACT_PROJECTION"
    assert macro["PCount"] == 72
    assert macro["allRowsPass"] is True
    assert macro["rationalityBidirectionalOnGate"] is True

    phase = output["phaseGate"]
    assert phase["status"] == "PROVEN_EXACT_LANE5_WITNESS"
    assert phase["operation64SupportCount"] == 16
    assert phase["supportPerVM81"] == 1296
    assert phase["bypassPerVM81"] == 3888
    assert phase["supportOps"] == [
        4, 5, 6, 7, 16, 17, 18, 19,
        44, 45, 46, 47, 56, 57, 58, 59,
    ]
    assert all(phase["algebra"].values())

    coupled = output["coupledCompatibility"]
    assert coupled["status"] == "EXECUTED_EXACT_CANDIDATE_SWEEP"
    assert coupled["combinedStateSlotChecks"] == 373248
    assert coupled["combinedStateSlotPasses"] == 373248
    assert coupled["phaseBearingChecks"] == 93312
    assert coupled["nonPhaseChecks"] == 279936
    assert coupled["allPass"] is True

    guards = output["negativeGuards"]
    assert guards["bridgeOnlyGridCells"] == 5184
    assert guards["bridgeOnlyVerifiedStates"] == 752
    assert guards["bridgeOnlyPValuesWithMultiplePQPairs"] == 72
    assert guards["bridgeAloneDoesNotEstablishSingleParameterAuthority"] is True
    assert guards["rationalityAloneDoesNotForceOrderedPhaseGate"] is True

    cex = guards["rationalityOnlyVisibleSubconstraintsCounterexample"]
    assert cex["bridge"] is True
    assert cex["deltaGate"] is True
    assert cex["xyGate"] is True
    assert cex["xSquared"] == "1"
    assert cex["imaginaryPhaseForced"] is False

    authority = output["authority"]
    assert authority["wholeSystemSingleParameterStatus"] == "OPEN_FULL_MANIFOLD_OBLIGATION"
    assert authority["phaseGateIsIndependentConstraint"] is True
    assert authority["scalarProjectionDoesNotGrantNativeSubstitution"] is True
    assert authority["canonicalVM81MutationAuthority"] is False
    assert authority["canonicalHash72Authority"] is False
    assert authority["canonicalHash216Authority"] is False
