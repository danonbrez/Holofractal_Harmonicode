"""Pass 218 Iteration 20 governed Pass 166 model activation binding.

Iteration 20 does not turn a language model into truth or action authority. It
binds one exact, installed Pass 166 Word2Vec model to the Pass 218 relational-
cognition plane after inherited RuntimeOS writer authority is current. The
binding is nonverbatim, restartable, and idempotent. A model may be activated
through the inherited Pass 166 VM81 admission surface only when explicitly
enabled by host configuration; browser callers never receive that capability.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol
import json
import os
import re

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

PASS218_I20_MODEL_BINDING_VERSION = "HHS-P218-I20-P166-MODEL-BINDING-V1"
PASS218_I20_BINDING_SCHEMA = "HHS-P218-I20-P166-MODEL-BINDING-RECORD-V1"
PASS218_I20_STATUS_SCHEMA = "HHS-P218-I20-P166-MODEL-BINDING-STATUS-V1"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class Pass218I20ModelBindingError(RuntimeError):
    """Fail-closed Iteration 20 activation/binding error."""


class Pass166ModelServiceProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def inspect(self, model_id: str) -> dict[str, Any]: ...
    def verify(self, model_id: str) -> dict[str, Any]: ...
    def activate(
        self,
        model_id: str,
        *,
        expected_pass165_frontier: str | None = None,
    ) -> dict[str, Any]: ...
    def get_operation(self, operation_id: str) -> dict[str, Any]: ...


class LifecycleProtocol(Protocol):
    target: Any
    def status(self) -> dict[str, Any]: ...


class PostconditionProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _atomic_write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    raw = _canonical_bytes(payload) + b"\n"
    with temporary.open("wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    try:
        directory_fd = os.open(str(path.parent), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _require_hex64(value: str, code: str) -> str:
    normalized = str(value).strip().lower()
    if not _HEX64.fullmatch(normalized):
        raise Pass218I20ModelBindingError(code)
    return normalized


def _receipt_identity(
    receipt: Mapping[str, Any],
    code: str,
) -> dict[str, str]:
    operation_id = str(receipt.get("operation_id") or "").strip()
    operation_hash216 = str(receipt.get("operation_hash216") or "").strip()
    receipt_hash72 = str(receipt.get("receipt_hash72") or "").strip()
    if not operation_id or not operation_hash216 or not receipt_hash72:
        raise Pass218I20ModelBindingError(code)
    return {
        "operation_id": operation_id,
        "operation_hash216": operation_hash216,
        "receipt_hash72": receipt_hash72,
    }


@dataclass(frozen=True)
class Pass218I20ModelConfiguration:
    model_id: str
    expected_model_root: str
    expected_index_root: str
    activate_if_needed: bool = False

    def validated(self) -> "Pass218I20ModelConfiguration":
        model_id = self.model_id.strip()
        if not model_id:
            raise Pass218I20ModelBindingError("P218_I20_MODEL_ID_REQUIRED")
        return Pass218I20ModelConfiguration(
            model_id=model_id,
            expected_model_root=_require_hex64(
                self.expected_model_root,
                "P218_I20_EXPECTED_MODEL_ROOT_INVALID",
            ),
            expected_index_root=_require_hex64(
                self.expected_index_root,
                "P218_I20_EXPECTED_INDEX_ROOT_INVALID",
            ),
            activate_if_needed=bool(self.activate_if_needed),
        )


class Pass218Pass166ModelBinding:
    """Bind one exact Pass 166 model to Pass 218 relational cognition."""

    def __init__(
        self,
        *,
        state_root: str | os.PathLike[str],
        service: Pass166ModelServiceProtocol,
        lifecycle: LifecycleProtocol,
        postcondition_control: PostconditionProtocol | None,
        configuration: Pass218I20ModelConfiguration,
    ) -> None:
        self.state_root = Path(state_root).resolve()
        self.binding_path = self.state_root / "model_activation_i20.json"
        self.service = service
        self.lifecycle = lifecycle
        self.postcondition_control = postcondition_control
        self.configuration = configuration.validated()
        self.last_error_code: str | None = None
        self.activation_invocation_count = 0
        self.verification_invocation_count = 0
        self.binding_write_count = 0
        self._ready = False

    @staticmethod
    def _code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_") or text.startswith("P166_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _authority_snapshot(self) -> dict[str, Any]:
        status = self.lifecycle.status()
        if not bool(status.get("authority_ready")):
            raise Pass218I20ModelBindingError(
                "P218_I20_CURRENT_WRITER_AUTHORITY_REQUIRED"
            )
        if self.postcondition_control is not None:
            postcondition = self.postcondition_control.status()
            if bool(postcondition.get("distributed_postcondition_configured")):
                pending = postcondition.get(
                    "successful_closure_pending_verification_count"
                )
                if pending is None:
                    raise Pass218I20ModelBindingError(
                        "P218_I20_I19_POSTCONDITION_STATUS_UNAVAILABLE"
                    )
                if int(pending) != 0:
                    raise Pass218I20ModelBindingError(
                        "P218_I20_I19_EFFECT_VERIFICATION_PENDING"
                    )
        target = getattr(self.lifecycle, "target", None)
        if target is None or not hasattr(target, "root_hash72"):
            raise Pass218I20ModelBindingError(
                "P218_I20_CANONICAL_TARGET_REQUIRED"
            )
        canonical_root = str(target.root_hash72())
        if not canonical_root:
            raise Pass218I20ModelBindingError("P218_I20_CANONICAL_ROOT_REQUIRED")
        return {
            "canonical_root_hash72": canonical_root,
            "distributed_owner_id": status.get("distributed_owner_id"),
            "distributed_host_id": status.get("distributed_host_id"),
            "distributed_fence_epoch": status.get("distributed_fence_epoch"),
            "local_owner_id": status.get("owner_id"),
            "local_fence_epoch": status.get(
                "ownership_fence_epoch", status.get("fence_epoch")
            ),
            "split_brain_writer_permitted": bool(
                status.get("split_brain_writer_permitted", False)
            ),
        }

    def _inspect_model(self) -> dict[str, Any]:
        inspected = self.service.inspect(self.configuration.model_id)
        model = inspected.get("model")
        if not isinstance(model, Mapping):
            raise Pass218I20ModelBindingError(
                "P218_I20_P166_INSTALLED_MODEL_REQUIRED"
            )
        model_root = _require_hex64(
            str(model.get("canonical_model_root") or ""),
            "P218_I20_P166_MODEL_ROOT_INVALID",
        )
        index_root = _require_hex64(
            str(model.get("index_root") or ""),
            "P218_I20_P166_INDEX_ROOT_INVALID",
        )
        if model_root != self.configuration.expected_model_root:
            raise Pass218I20ModelBindingError(
                "P218_I20_P166_MODEL_ROOT_MISMATCH"
            )
        if index_root != self.configuration.expected_index_root:
            raise Pass218I20ModelBindingError(
                "P218_I20_P166_INDEX_ROOT_MISMATCH"
            )
        return dict(model)

    def _read_binding(self) -> dict[str, Any] | None:
        if not self.binding_path.exists():
            return None
        raw = json.loads(self.binding_path.read_text("utf-8"))
        if raw.get("schema") != PASS218_I20_BINDING_SCHEMA:
            raise Pass218I20ModelBindingError("P218_I20_BINDING_SCHEMA_INVALID")
        supplied = str(raw.get("binding_hash72") or "")
        body = {key: value for key, value in raw.items() if key != "binding_hash72"}
        expected = hash72_digest(
            {"domain": PASS218_I20_BINDING_SCHEMA},
            body,
        )
        if supplied != expected:
            raise Pass218I20ModelBindingError(
                "P218_I20_BINDING_HASH72_MISMATCH"
            )
        return raw

    def _validated_stored_receipt(
        self,
        existing_binding: Mapping[str, Any],
        *,
        field: str,
        stage: str,
        required_code: str,
        mismatch_code: str,
    ) -> tuple[dict[str, str], dict[str, Any]]:
        stored = existing_binding.get(field)
        if not isinstance(stored, Mapping):
            raise Pass218I20ModelBindingError(required_code)
        record = self.service.get_operation(str(stored.get("operation_id") or ""))
        identity = _receipt_identity(record, required_code)
        if identity != dict(stored) or str(record.get("stage") or "") != stage:
            raise Pass218I20ModelBindingError(mismatch_code)
        return identity, record

    def _activation_receipt(
        self,
        model: Mapping[str, Any],
        existing_binding: Mapping[str, Any] | None,
    ) -> dict[str, str]:
        if existing_binding is not None:
            identity, _ = self._validated_stored_receipt(
                existing_binding,
                field="pass166_activation_receipt",
                stage="ACTIVATION",
                required_code="P218_I20_P166_ACTIVATION_RECEIPT_REQUIRED",
                mismatch_code="P218_I20_P166_ACTIVATION_RECEIPT_MISMATCH",
            )
            return identity
        terminal = model.get("terminal_receipt")
        if (
            not isinstance(terminal, Mapping)
            or str(terminal.get("stage") or "") != "ACTIVATION"
        ):
            raise Pass218I20ModelBindingError(
                "P218_I20_PREEXISTING_ACTIVATION_RECEIPT_REQUIRED"
            )
        return _receipt_identity(
            terminal,
            "P218_I20_P166_ACTIVATION_RECEIPT_INCOMPLETE",
        )

    def _verification_receipt(
        self,
        existing_binding: Mapping[str, Any] | None,
    ) -> dict[str, str]:
        if existing_binding is not None:
            identity, record = self._validated_stored_receipt(
                existing_binding,
                field="pass166_verification_receipt",
                stage="COMPATIBILITY_VALIDATION",
                required_code="P218_I20_P166_VERIFICATION_RECEIPT_REQUIRED",
                mismatch_code="P218_I20_P166_VERIFICATION_RECEIPT_MISMATCH",
            )
            body = record.get("body")
            if (
                not isinstance(body, Mapping)
                or body.get("model_id") != self.configuration.model_id
                or body.get("canonical_model_root")
                != self.configuration.expected_model_root
                or body.get("index_root") != self.configuration.expected_index_root
                or body.get("verified") is not True
            ):
                raise Pass218I20ModelBindingError(
                    "P218_I20_P166_VERIFICATION_RECEIPT_MISMATCH"
                )
            return identity
        result = self.service.verify(self.configuration.model_id)
        receipt = result.get("receipt")
        if not isinstance(receipt, Mapping):
            raise Pass218I20ModelBindingError(
                "P218_I20_P166_VERIFICATION_RECEIPT_REQUIRED"
            )
        if str(receipt.get("stage") or "") != "COMPATIBILITY_VALIDATION":
            raise Pass218I20ModelBindingError(
                "P218_I20_P166_VERIFICATION_RECEIPT_MISMATCH"
            )
        body = receipt.get("body")
        if (
            not isinstance(body, Mapping)
            or body.get("model_id") != self.configuration.model_id
            or body.get("canonical_model_root")
            != self.configuration.expected_model_root
            or body.get("index_root") != self.configuration.expected_index_root
            or body.get("verified") is not True
        ):
            raise Pass218I20ModelBindingError(
                "P218_I20_P166_VERIFICATION_RECEIPT_MISMATCH"
            )
        self.verification_invocation_count += 1
        return _receipt_identity(
            receipt,
            "P218_I20_P166_VERIFICATION_RECEIPT_INCOMPLETE",
        )

    def synchronize(self) -> dict[str, Any]:
        """Perform/verify one governed activation and seal a restart-stable binding."""
        try:
            current_authority = self._authority_snapshot()
            model = self._inspect_model()
            existing_binding = self._read_binding()
            service_status = self.service.status()
            active_model_id = service_status.get("active_model_id")
            activation_receipt: dict[str, str] | None = None

            if active_model_id not in (None, self.configuration.model_id):
                raise Pass218I20ModelBindingError(
                    "P218_I20_DIFFERENT_P166_MODEL_ALREADY_ACTIVE"
                )
            if active_model_id is None:
                if existing_binding is not None:
                    raise Pass218I20ModelBindingError(
                        "P218_I20_BOUND_P166_MODEL_NO_LONGER_ACTIVE"
                    )
                if not self.configuration.activate_if_needed:
                    raise Pass218I20ModelBindingError(
                        "P218_I20_P166_MODEL_NOT_ACTIVE"
                    )
                result = self.service.activate(
                    self.configuration.model_id,
                    expected_pass165_frontier=(
                        str(service_status.get("pass165_frontier") or "") or None
                    ),
                )
                receipt = result.get("receipt")
                if not isinstance(receipt, Mapping):
                    raise Pass218I20ModelBindingError(
                        "P218_I20_P166_ACTIVATION_RECEIPT_REQUIRED"
                    )
                activation_receipt = _receipt_identity(
                    receipt,
                    "P218_I20_P166_ACTIVATION_RECEIPT_INCOMPLETE",
                )
                self.activation_invocation_count += 1
                model = self._inspect_model()

            if activation_receipt is None:
                activation_receipt = self._activation_receipt(
                    model,
                    existing_binding,
                )
            verification_receipt = self._verification_receipt(existing_binding)

            creation_authority = (
                existing_binding.get("binding_created_under_authority")
                if existing_binding is not None
                else current_authority
            )
            if not isinstance(creation_authority, Mapping):
                raise Pass218I20ModelBindingError(
                    "P218_I20_BINDING_AUTHORITY_PROVENANCE_INVALID"
                )
            body = {
                "schema": PASS218_I20_BINDING_SCHEMA,
                "version": PASS218_I20_MODEL_BINDING_VERSION,
                "model_id": self.configuration.model_id,
                "canonical_model_root": self.configuration.expected_model_root,
                "index_root": self.configuration.expected_index_root,
                "manifest_root": str(model.get("manifest_root") or ""),
                "package_digest": str(model.get("package_digest") or ""),
                "pass166_activation_receipt": activation_receipt,
                "pass166_verification_receipt": verification_receipt,
                "binding_created_under_authority": dict(creation_authority),
                "relational_cognition_provider": True,
                "distributional_relations_are_revisable_candidates": True,
                "browser_model_activation_permitted": False,
                "canonical_learning_commit_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "pass165_source_retaining_learning_commit_invoked": False,
                "verbatim_corpus_source_retained": False,
                "authoritative_float_weights_created": False,
            }
            record = {
                **body,
                "binding_hash72": hash72_digest(
                    {"domain": PASS218_I20_BINDING_SCHEMA},
                    body,
                ),
            }
            if existing_binding is not None:
                if dict(existing_binding) != record:
                    raise Pass218I20ModelBindingError(
                        "P218_I20_BINDING_REPLACEMENT_REQUIRES_NEW_ITERATION"
                    )
            else:
                _atomic_write(self.binding_path, record)
                self.binding_write_count += 1
            self._ready = True
            self.last_error_code = None
            return self.status()
        except Exception as exc:
            self._ready = False
            self.last_error_code = self._code(exc)
            if isinstance(exc, Pass218I20ModelBindingError):
                raise
            raise Pass218I20ModelBindingError(self.last_error_code) from exc

    def exact_provider(self) -> Any:
        """Return the existing I1 exact adapter only after I20 binding is ready."""
        if not self._ready:
            raise Pass218I20ModelBindingError(
                "P218_I20_MODEL_PROVIDER_NOT_READY"
            )
        from hhs_runtime.pass218.genesis import Pass166Word2VecAdapter

        return Pass166Word2VecAdapter(
            self.service,
            model_id=self.configuration.model_id,
        )

    def status(self) -> dict[str, Any]:
        binding: dict[str, Any] | None = None
        try:
            binding = self._read_binding()
        except Exception as exc:
            self._ready = False
            self.last_error_code = self._code(exc)
        service_status = self.service.status()
        active_exact = (
            service_status.get("active_model_id") == self.configuration.model_id
        )
        return {
            "schema": PASS218_I20_STATUS_SCHEMA,
            "version": PASS218_I20_MODEL_BINDING_VERSION,
            "configured": True,
            "model_id": self.configuration.model_id,
            "expected_model_root": self.configuration.expected_model_root,
            "expected_index_root": self.configuration.expected_index_root,
            "pass166_active_model_id": service_status.get("active_model_id"),
            "pass166_model_active_exact": active_exact,
            "binding_present": binding is not None,
            "binding_hash72": (
                None if binding is None else binding.get("binding_hash72")
            ),
            "relational_candidate_provider_ready": bool(
                self._ready and binding is not None and active_exact
            ),
            "activation_invocation_count": self.activation_invocation_count,
            "verification_invocation_count": self.verification_invocation_count,
            "binding_write_count": self.binding_write_count,
            "i20_error_code": self.last_error_code,
            "browser_model_activation_permitted": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "pass165_source_retaining_learning_commit_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }


__all__ = [
    "PASS218_I20_BINDING_SCHEMA",
    "PASS218_I20_MODEL_BINDING_VERSION",
    "PASS218_I20_STATUS_SCHEMA",
    "Pass218I20ModelBindingError",
    "Pass218I20ModelConfiguration",
    "Pass218Pass166ModelBinding",
]
