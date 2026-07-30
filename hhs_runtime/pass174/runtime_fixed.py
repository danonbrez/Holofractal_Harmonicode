from __future__ import annotations

from typing import Any, Sequence

from .codec import denormalize
from . import runtime as _runtime


class EncryptedVectorStore(_runtime.EncryptedVectorStore):
    def retrieve(
        self,
        identity: str,
        *,
        expected_incoming_tip: str,
        allowed_parents: Sequence[str | None],
    ) -> dict[str, Any]:
        normalized = super().retrieve(
            identity,
            expected_incoming_tip=expected_incoming_tip,
            allowed_parents=allowed_parents,
        )
        decoded = denormalize(normalized)
        if not isinstance(decoded, dict):
            raise _runtime.RetrievalError("decoded encrypted object is not a mapping")
        return decoded


# Base runtime name lookup is intentionally rebound to the reversible store.
# The execution authority remains the single Pass174Runtime instance owned by
# the canonical HHS server process.
_runtime.EncryptedVectorStore = EncryptedVectorStore


class Pass174Runtime(_runtime.Pass174Runtime):
    pass


AdmissionError = _runtime.AdmissionError
AuditResult = _runtime.AuditResult
DirectionalInfinity = _runtime.DirectionalInfinity
HarmonicOperator = _runtime.HarmonicOperator
PhaseGearCoordinate = _runtime.PhaseGearCoordinate
RationalComplex = _runtime.RationalComplex
RetrievalError = _runtime.RetrievalError
SparseFrameDelta = _runtime.SparseFrameDelta
VM81Frame5184 = _runtime.VM81Frame5184
