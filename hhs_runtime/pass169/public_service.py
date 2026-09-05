"""Shared Pass 169 algebra public service.

CLI and HTTP surfaces call this same service.  The service does not create a
second VM81 authority and does not manufacture the missing canonical Pass169
corpus.  Exact source ingress is preserved as a noncanonical candidate record;
operations that require canonical algebra execution fail closed until the
contract-required corpus and runtime binding are present.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Mapping

from hhs_runtime.pass219.pass169_terminal_reconciliation import PASS169_CANONICAL_CORPUS_PATH
from hhs_runtime.pass219.pass169_terminal_gate_i167 import build_i167_pass169_terminal_gate
from hhs_runtime.pass169.runtime_binding import (
    CANONICAL_SOURCE_SHA256,
    Pass169CanonicalRuntimeBinding,
    Pass169RuntimeBindingError,
)

CONTRACT_ID = "HHS-P169-HSAE-VM81-ESCPR"
SURFACE_VERSION = "PASS219-I165-PASS169-PUBLIC-SURFACE-V1"
BASE_MAIN = "33fdd71c6bf04af4e3cfe0b86ce32dbdb0b7cf7d"
FIXED_RESOLUTION = "72^42=5184^21"

READ_OPERATIONS = frozenset({
    "status", "source", "tokens", "ast", "symbols", "constraints",
    "inspect", "receipt", "replay", "divergence", "export-proof", "validate",
})
MUTATING_OPERATIONS = frozenset({"admit", "commit", "reverse"})
CANDIDATE_OPERATIONS = frozenset({
    "typecheck", "normalize", "prove", "prove-constraint", "evaluate-candidate",
})


class Pass169PublicSurfaceError(RuntimeError):
    def __init__(self, code: str, *, http_status: int = 409, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.http_status = http_status
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "contract": CONTRACT_ID,
            "surface_version": SURFACE_VERSION,
            "error": self.code,
            "details": self.details,
            "canonical_state_mutated": False,
            "floating_point_canonical_authority": False,
        }


@dataclass(frozen=True)
class CandidateSource:
    source_id: str
    sha256: str
    byte_length: int
    text: str

    def public(self, *, include_text: bool = False) -> dict[str, Any]:
        out = {
            "source_id": self.source_id,
            "sha256": self.sha256,
            "byte_length": self.byte_length,
            "classification": "NONCANONICAL_EXACT_SOURCE_INGRESS",
            "canonical_pass169_corpus": False,
            "canonical_authority": False,
        }
        if include_text:
            out["source"] = self.text
        return out


class Pass169AlgebraService:
    """Transport-level Pass169 service with explicit fail-closed authority gates."""

    def __init__(
        self,
        repository_root: str | Path | None = None,
        *,
        authority_provider: Callable[[], Any] | None = None,
    ) -> None:
        self.repository_root = Path(repository_root or Path(__file__).resolve().parents[2]).resolve()
        self.authority_provider = authority_provider
        self._sources: dict[str, CandidateSource] = {}
        self._canonical_runtime = Pass169CanonicalRuntimeBinding(self.repository_root)

    def _reconciliation(self) -> dict[str, Any]:
        return build_i167_pass169_terminal_gate(self.repository_root)

    def _authority_snapshot(self) -> dict[str, Any]:
        if self.authority_provider is None:
            return {
                "canonical_gateway_bound": False,
                "authority_context_available": False,
                "new_vm81_authority": False,
            }
        try:
            context = self.authority_provider()
            status = context.status() if hasattr(context, "status") else {}
            return {
                "canonical_gateway_bound": True,
                "authority_context_available": True,
                "authority_contract": status.get("contract"),
                "runtime_mode": status.get("runtime_mode"),
                "singleton_vm81_authority": status.get("singleton_vm81_authority"),
                "new_vm81_authority": False,
            }
        except Exception as exc:  # status remains observable without fabricating authority
            return {
                "canonical_gateway_bound": True,
                "authority_context_available": False,
                "authority_error": f"{type(exc).__name__}:{exc}",
                "new_vm81_authority": False,
            }

    def status(self) -> dict[str, Any]:
        report = self._reconciliation()
        return {
            "ok": True,
            "contract": CONTRACT_ID,
            "surface_version": SURFACE_VERSION,
            "fixed_resolution": FIXED_RESOLUTION,
            "base_main": BASE_MAIN,
            "pass169_terminal_contract_verified": report["pass169_terminal_contract_verified"],
            "canonical_corpus_present": report["canonical_corpus"]["present"],
            "blockers": list(report["blockers"]),
            "frozen_evidence_verified": report["frozen_evidence"]["all_frozen_evidence_verified"],
            "authority": self._authority_snapshot(),
            "registered_candidate_sources": len(self._sources),
            "new_vm81_authority": False,
            "new_hash72_mint_authority": False,
            "hash216_persistence_authority": False,
            "floating_point_canonical_authority": False,
        }

    def register_source(self, source: str) -> dict[str, Any]:
        if not isinstance(source, str) or not source:
            raise Pass169PublicSurfaceError("PASS169_SOURCE_REQUIRED", http_status=400)
        data = source.encode("utf-8")
        digest = sha256(data).hexdigest()
        source_id = f"sha256:{digest}"
        if digest == CANONICAL_SOURCE_SHA256 and len(data) == 632:
            canonical = self.get_source(include_text=False)["source"]
            return {
                "ok": True,
                "contract": CONTRACT_ID,
                "source": canonical,
                "canonical_state_mutated": False,
                "canonical_pass169_corpus_replaced": False,
            }
        record = CandidateSource(source_id, digest, len(data), source)
        self._sources[source_id] = record
        return {
            "ok": True,
            "contract": CONTRACT_ID,
            "source": record.public(),
            "canonical_state_mutated": False,
            "canonical_pass169_corpus_replaced": False,
        }

    def get_source(self, source_id: str | None = None, *, include_text: bool = True) -> dict[str, Any]:
        if source_id and source_id != self._canonical_runtime.canonical_source_id:
            record = self._sources.get(source_id)
            if record is None:
                raise Pass169PublicSurfaceError("PASS169_SOURCE_ID_NOT_FOUND", http_status=404, details={"source_id": source_id})
            return {"ok": True, "contract": CONTRACT_ID, "source": record.public(include_text=include_text)}
        canonical = self.repository_root / PASS169_CANONICAL_CORPUS_PATH
        if not canonical.is_file():
            raise Pass169PublicSurfaceError(
                "PASS169_CANONICAL_CORPUS_ABSENT",
                details={"required_path": PASS169_CANONICAL_CORPUS_PATH.as_posix()},
            )
        data = canonical.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise Pass169PublicSurfaceError("PASS169_CANONICAL_CORPUS_NOT_UTF8", details={"error": str(exc)}) from exc
        return {
            "ok": True,
            "contract": CONTRACT_ID,
            "source": {
                "source_id": f"canonical:sha256:{sha256(data).hexdigest()}",
                "sha256": sha256(data).hexdigest(),
                "byte_length": len(data),
                "source": text if include_text else None,
                "classification": "CANONICAL_PASS169_CORPUS",
                "canonical_pass169_corpus": True,
            },
        }

    def _require_canonical_corpus(self) -> None:
        if not (self.repository_root / PASS169_CANONICAL_CORPUS_PATH).is_file():
            raise Pass169PublicSurfaceError(
                "PASS169_CANONICAL_CORPUS_ABSENT",
                details={"required_path": PASS169_CANONICAL_CORPUS_PATH.as_posix()},
            )

    def _runtime_execute(self, operation: str, **details: Any) -> dict[str, Any]:
        self._require_canonical_corpus()
        try:
            return self._canonical_runtime.dispatch(operation, **details)
        except Pass169RuntimeBindingError as exc:
            raise Pass169PublicSurfaceError(str(exc), details={"operation": operation, **details}) from exc

    def dispatch(self, operation: str, **params: Any) -> dict[str, Any]:
        op = operation.strip().lower()
        if op == "status":
            return self.status()
        if op == "source":
            return self.get_source(params.get("source_id"))
        if op == "register-source":
            return self.register_source(str(params.get("source", "")))
        if op in READ_OPERATIONS | MUTATING_OPERATIONS | CANDIDATE_OPERATIONS:
            return self._runtime_execute(op, **{k: v for k, v in params.items() if v is not None})
        raise Pass169PublicSurfaceError("PASS169_OPERATION_UNKNOWN", http_status=404, details={"operation": operation})


__all__ = [
    "BASE_MAIN",
    "CONTRACT_ID",
    "FIXED_RESOLUTION",
    "SURFACE_VERSION",
    "Pass169AlgebraService",
    "Pass169PublicSurfaceError",
]
