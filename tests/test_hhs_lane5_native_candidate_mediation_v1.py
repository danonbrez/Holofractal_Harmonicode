"""Focused typed bridge tests for the real native Lane 5 1.34 C ABI.

Mocks verify ABI copying and boundary checks only. A real signed model/VM81
candidate must be tested against the compiled C nucleus separately.
"""
from __future__ import annotations

import ctypes

import pytest

from hhs_backend.runtime.hhs_lane5_native_candidate_mediation_v1 import (
    MAX_REFS, NAMESPACE, VERSION, SIGNATURE_FIELDS,
    Lane5Request, Lane5Receipt, Lane5NativeMediationError,
    PreparedLane5Candidate, mediate_prepared_candidate,
)


def candidate():
    return PreparedLane5Candidate(
        signatures={name: 100 + i for i, name in enumerate(SIGNATURE_FIELDS)},
        hash216_references=(201, 202, 203),
        capability_references=(301, 302, 303, 304),
        learning_stage=4,
        raw5184="0" * 5184,
        ordered_transition_word216="A" * 72 + "B" * 72 + "C" * 72,
    )


class FakeCallable:
    def __init__(self, function):
        self.function = function
        self.restype = None
        self.argtypes = None

    def __call__(self, *args):
        return self.function(*args)


class FakeLane5Native:
    def __init__(self, *, decision=1, tamper=False, mutation=False, version=VERSION):
        self.decision = decision
        self.tamper = tamper
        self.mutation = mutation
        self.observed = None
        self.hhs_exact_pass219_lane5_nucleus_version = FakeCallable(lambda: version)
        self.hhs_exact_pass219_lane5_mediate_candidate = FakeCallable(self._mediate)

    def _mediate(self, req_ptr, receipt_ptr):
        req = ctypes.cast(req_ptr, ctypes.POINTER(Lane5Request)).contents
        receipt = ctypes.cast(receipt_ptr, ctypes.POINTER(Lane5Receipt)).contents
        self.observed = {
            "hash216_count": req.hash216_reference_count,
            "capability_count": req.capability_reference_count,
            "learning_stage": req.learning_stage,
            "rna_prepared_signature64": req.rna_prepared_signature64,
            "hash216_references": [
                req.hash216_reference_signature64[i]
                for i in range(req.hash216_reference_count)
            ],
            "capability_references": [
                req.capability_reference_signature64[i]
                for i in range(req.capability_reference_count)
            ],
        }
        receipt.struct_size = ctypes.sizeof(Lane5Receipt)
        receipt.version = req.version
        receipt.namespace_id = req.namespace_id
        receipt.decision = self.decision
        receipt.learning_stage = req.learning_stage
        receipt.hash216_reference_count = req.hash216_reference_count
        receipt.capability_reference_count = req.capability_reference_count
        for field in SIGNATURE_FIELDS:
            setattr(receipt, field, getattr(req, field))
        if self.tamper:
            receipt.parent_hash216_signature64 ^= 1
        receipt.closure_signature64 = 9001
        receipt.mediation_signature64 = 9002
        for name in (
            "hash216_references_validated", "capability_registry_validated",
            "exact_vm5184_bound", "rna_cell_wall_bound", "zero_sum_closure_passed",
            "candidate_only", "requires_environmental_admission",
        ):
            setattr(receipt, name, 1)
        if self.mutation:
            receipt.canonical_mutation_authority = 1
        return 0


def test_existing_native_struct_layout_and_source_preserving_witness():
    c = candidate()
    req = c.native_request()
    assert req.struct_size == ctypes.sizeof(Lane5Request)
    assert req.version == VERSION
    assert req.namespace_id == NAMESPACE
    assert req.hash216_reference_count == 3
    assert req.capability_reference_count == 4
    assert req.rna_prepared_signature64 == c.signatures["rna_prepared_signature64"]


def test_real_native_function_name_called_with_all_prepared_typed_evidence():
    library = FakeLane5Native()
    c = candidate()
    result = mediate_prepared_candidate(c, native_library=library)
    assert result["status"] == "CANDIDATE_READY_NOT_CANONICAL_MUTATION"
    assert result["raw5184_character_count"] == 5184
    assert result["ordered_transition_word216_length"] == 216
    assert result["raw_state_exposed_in_result"] is False
    assert "raw5184" not in result
    assert "ordered_transition_word216" not in result
    assert c.raw5184 == "0" * 5184  # trusted caller retains lossless state
    assert c.ordered_transition_word216 == "A" * 72 + "B" * 72 + "C" * 72
    assert result["native_hash216_reference_signatures"] == [201, 202, 203]
    assert result["requires_signed_environmental_vm81_admission"] is True
    assert result["canonical_mutation_admitted"] is False
    assert result["external_signature_provenance_independently_verified"] is False
    assert library.observed["rna_prepared_signature64"] == c.signatures["rna_prepared_signature64"]


@pytest.mark.parametrize("kwargs,error", [
    ({"raw5184": "0" * 5183}, "5184-character"),
    ({"ordered_transition_word216": "x" * 215}, "216-character"),
    ({"learning_stage": 1.0}, "integer required"),
    ({"hash216_references": ()}, "expected 1..64"),
    ({"hash216_references": (1,) * (MAX_REFS + 1)}, "expected 1..64"),
    ({"capability_references": (1, 0)}, "invalid exact unsigned range"),
    ({"signatures": {"request_signature64": 1}}, "all native prepared signature"),
])
def test_no_lossy_or_partial_scalar_projection(kwargs, error):
    import dataclasses
    with pytest.raises(Lane5NativeMediationError, match=error):
        dataclasses.replace(candidate(), **kwargs)


@pytest.mark.parametrize("native,error", [
    (FakeLane5Native(decision=2), "authority/closure invariant"),
    (FakeLane5Native(tamper=True), "receipt/provenance mismatch"),
    (FakeLane5Native(mutation=True), "authority/closure invariant"),
    (FakeLane5Native(version=VERSION + 1), "version mismatch"),
])
def test_native_receipt_does_not_bypass_closure_or_mutation_authority(native, error):
    with pytest.raises(Lane5NativeMediationError, match=error):
        mediate_prepared_candidate(candidate(), native_library=native)


def test_unprepared_prompt_response_not_accepted():
    with pytest.raises(Lane5NativeMediationError, match="typed prepared"):
        mediate_prepared_candidate({"prompt": "Hello", "response": "World"}, native_library=FakeLane5Native())


def test_prepared_signatures_cannot_be_replaced_after_native_validation():
    original = candidate()
    with pytest.raises(TypeError):
        original.signatures["rna_prepared_signature64"] = 0
    assert original.native_request().rna_prepared_signature64 == 108


def test_requested_native_rna_binding_preserves_other_exact_witnesses():
    import dataclasses

    baseline = candidate()
    signatures = dict(baseline.signatures)
    signatures["rna_prepared_signature64"] = 0
    signatures["rna_decision_signature64"] = 0
    bound = dataclasses.replace(
        baseline, signatures=signatures, native_rna_bind=True,
    )
    req = bound.native_request()
    assert req.rna_prepared_signature64 == 0
    assert req.rna_decision_signature64 == 0
    assert req.parent_hash216_signature64 == baseline.signatures["parent_hash216_signature64"]
    assert req.capability_registry_signature64 == baseline.signatures["capability_registry_signature64"]
    # Only the coupled native C++ RNA ingress may authenticate those fields.
    with pytest.raises(Lane5NativeMediationError, match="requires coupled"):
        mediate_prepared_candidate(bound, native_library=FakeLane5Native())


def test_partial_native_rna_binding_rejected():
    import dataclasses

    original = candidate()
    signatures = dict(original.signatures)
    signatures["rna_prepared_signature64"] = 0
    with pytest.raises(Lane5NativeMediationError, match="both signatures unset"):
        dataclasses.replace(original, signatures=signatures, native_rna_bind=True)


def test_bound_native_receipt_requires_authentic_computed_pair():
    import dataclasses
    from hhs_backend.runtime.hhs_lane5_native_candidate_mediation_v1 import (
        _receipt_projection,
    )
    c = candidate()
    signatures = dict(c.signatures)
    signatures["rna_prepared_signature64"] = 0
    signatures["rna_decision_signature64"] = 0
    bound = dataclasses.replace(c, signatures=signatures, native_rna_bind=True)
    native = FakeLane5Native()
    request = bound.native_request()
    receipt = Lane5Receipt()
    # A fake C function cannot supply the required authentically bound pair.
    native._mediate(ctypes.byref(request), ctypes.byref(receipt))
    with pytest.raises(Lane5NativeMediationError, match="did not bind signatures"):
        _receipt_projection(bound, request, receipt)
