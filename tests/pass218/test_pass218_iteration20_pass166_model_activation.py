from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_model_i20 import (
    PASS218_I20_STATUS_PATH,
    Pass218I20RuntimeModelControl,
    install_pass218_i20_model_control,
)
from hhs_runtime.pass166.common import Word2VecPackageManifest
from hhs_runtime.pass166.service import Word2VecService
from hhs_runtime.pass218.model_activation_i20 import (
    Pass218I20ModelBindingError,
    Pass218I20ModelConfiguration,
    Pass218Pass166ModelBinding,
)


class FakeTarget:
    def __init__(self, root: str = "h" * 72) -> None:
        self._root = root

    def root_hash72(self) -> str:
        return self._root


class FakeLifecycle:
    def __init__(self, *, ready: bool = True, fence: int = 7) -> None:
        self.ready = ready
        self.fence = fence
        self.target = FakeTarget()

    def status(self) -> dict:
        return {
            "authority_ready": self.ready,
            "owner_id": "local-owner",
            "ownership_fence_epoch": self.fence,
            "distributed_owner_id": "distributed-owner",
            "distributed_host_id": "host-a",
            "distributed_fence_epoch": self.fence,
            "split_brain_writer_permitted": False,
        }


class FakePostcondition:
    def __init__(self, *, configured: bool = True, pending: int | None = 0) -> None:
        self.configured = configured
        self.pending = pending

    def status(self) -> dict:
        return {
            "distributed_postcondition_configured": self.configured,
            "successful_closure_pending_verification_count": self.pending,
        }


def _source(path: Path, model_id: str) -> Path:
    raw = (
        b"4 3\n"
        b"king 1 1 0\n"
        b"queen 1 0.9 0.1\n"
        b"man 0.9 0 0\n"
        b"woman 0.9 -0.1 0.1\n"
    )
    source = path / f"{model_id}.txt"
    source.write_bytes(raw)
    return source.resolve()


def _manifest(source: Path, model_id: str) -> Word2VecPackageManifest:
    raw = source.read_bytes()
    return Word2VecPackageManifest(
        package_id=model_id,
        display_name=model_id,
        provider="HHS_I20_TEST_FIXTURE",
        source_uri=source.as_uri(),
        source_version="1",
        license_id="TEST-ONLY",
        license_uri="https://example.invalid/test-license",
        expected_byte_length=len(raw),
        expected_sha256=sha256(raw).hexdigest(),
        archive_type="NONE",
        vector_format="WORD2VEC_TEXT",
        vector_dimension=3,
        vocabulary_size=4,
        normalization_profile="CASE_FOLDED",
    )


def _installed_service(
    tmp_path: Path,
    *,
    model_id: str = "i20-toy",
    active: bool = False,
) -> tuple[Word2VecService, dict]:
    source = _source(tmp_path, model_id)
    service = Word2VecService(tmp_path / f"pass166-{model_id}")
    service.register_manifest(_manifest(source, model_id))
    result = service.install(
        model_id,
        accept_license=True,
        activate=active,
        offline_ready=True,
    )
    return service, result


def _binding(
    tmp_path: Path,
    service: Word2VecService,
    installed: dict,
    *,
    lifecycle: FakeLifecycle | None = None,
    postcondition: FakePostcondition | None = None,
    activate: bool = True,
) -> Pass218Pass166ModelBinding:
    return Pass218Pass166ModelBinding(
        state_root=tmp_path / "pass218-state",
        service=service,
        lifecycle=lifecycle or FakeLifecycle(),
        postcondition_control=postcondition or FakePostcondition(),
        configuration=Pass218I20ModelConfiguration(
            model_id=installed["model_id"],
            expected_model_root=installed["canonical_model_root"],
            expected_index_root=installed["index_root"],
            activate_if_needed=activate,
        ),
    )


def test_i20_activates_exact_installed_model_once_and_exposes_i1_provider(tmp_path: Path) -> None:
    service, installed = _installed_service(tmp_path, active=False)
    binding = _binding(tmp_path, service, installed)

    first = binding.synchronize()
    assert first["relational_candidate_provider_ready"] is True
    assert first["activation_invocation_count"] == 1
    assert first["verification_invocation_count"] == 1
    assert first["binding_write_count"] == 1
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["pass165_source_retaining_learning_commit_invoked"] is False
    assert service.status()["active_model_id"] == installed["model_id"]

    provider = binding.exact_provider()
    neighbors = provider.exact_neighbors("king", top_k=2)
    assert neighbors
    assert all(item.sign in (-1, 0, 1) for item in neighbors)

    second = binding.synchronize()
    assert second["binding_hash72"] == first["binding_hash72"]
    assert second["activation_invocation_count"] == 1
    assert second["verification_invocation_count"] == 1
    assert second["binding_write_count"] == 1


def test_i20_restart_reuses_exact_receipts_across_new_legitimate_writer_fence(tmp_path: Path) -> None:
    service, installed = _installed_service(tmp_path, active=False)
    first = _binding(
        tmp_path,
        service,
        installed,
        lifecycle=FakeLifecycle(fence=7),
    )
    first_status = first.synchronize()
    raw = json.loads(first.binding_path.read_text("utf-8"))
    first_activation_receipt = dict(raw["pass166_activation_receipt"])
    first_verification_receipt = dict(raw["pass166_verification_receipt"])
    assert raw["binding_created_under_authority"]["distributed_fence_epoch"] == 7
    assert service.get_operation(first_activation_receipt["operation_id"])["stage"] == "ACTIVATION"
    assert service.get_operation(first_verification_receipt["operation_id"])["stage"] == "COMPATIBILITY_VALIDATION"

    restarted = _binding(
        tmp_path,
        service,
        installed,
        lifecycle=FakeLifecycle(fence=8),
    )
    restarted_status = restarted.synchronize()
    assert restarted_status["binding_hash72"] == first_status["binding_hash72"]
    assert restarted_status["activation_invocation_count"] == 0
    assert restarted_status["verification_invocation_count"] == 0
    assert restarted_status["binding_write_count"] == 0
    replayed = json.loads(restarted.binding_path.read_text("utf-8"))
    assert replayed["binding_created_under_authority"]["distributed_fence_epoch"] == 7
    assert replayed["pass166_activation_receipt"] == first_activation_receipt
    assert replayed["pass166_verification_receipt"] == first_verification_receipt


def test_i20_preexisting_pass166_activation_can_be_bound_without_redispatch(tmp_path: Path) -> None:
    service, installed = _installed_service(tmp_path, active=True)
    binding = _binding(tmp_path, service, installed, activate=False)
    status = binding.synchronize()
    assert status["relational_candidate_provider_ready"] is True
    assert status["activation_invocation_count"] == 0
    assert status["verification_invocation_count"] == 1
    assert status["binding_write_count"] == 1


def test_i20_fails_closed_for_pending_effect_or_missing_writer_authority(tmp_path: Path) -> None:
    service, installed = _installed_service(tmp_path, active=False)
    pending = _binding(
        tmp_path,
        service,
        installed,
        postcondition=FakePostcondition(configured=True, pending=1),
    )
    with pytest.raises(Pass218I20ModelBindingError, match="P218_I20_I19_EFFECT_VERIFICATION_PENDING"):
        pending.synchronize()
    assert service.status()["active_model_id"] is None

    no_authority = _binding(
        tmp_path,
        service,
        installed,
        lifecycle=FakeLifecycle(ready=False),
    )
    with pytest.raises(Pass218I20ModelBindingError, match="P218_I20_CURRENT_WRITER_AUTHORITY_REQUIRED"):
        no_authority.synchronize()
    assert service.status()["active_model_id"] is None


def test_i20_rejects_model_identity_drift_and_tampered_binding(tmp_path: Path) -> None:
    service, installed = _installed_service(tmp_path, active=False)
    wrong = Pass218Pass166ModelBinding(
        state_root=tmp_path / "wrong-state",
        service=service,
        lifecycle=FakeLifecycle(),
        postcondition_control=FakePostcondition(),
        configuration=Pass218I20ModelConfiguration(
            model_id=installed["model_id"],
            expected_model_root="0" * 64,
            expected_index_root=installed["index_root"],
            activate_if_needed=True,
        ),
    )
    with pytest.raises(Pass218I20ModelBindingError, match="P218_I20_P166_MODEL_ROOT_MISMATCH"):
        wrong.synchronize()

    good = _binding(tmp_path, service, installed)
    good.synchronize()
    payload = json.loads(good.binding_path.read_text("utf-8"))
    payload["truth_promotion"] = True
    good.binding_path.write_text(json.dumps(payload), "utf-8")
    restarted = _binding(tmp_path, service, installed)
    with pytest.raises(Pass218I20ModelBindingError, match="P218_I20_BINDING_HASH72_MISMATCH"):
        restarted.synchronize()


def test_i20_runtime_os_surface_is_status_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, installed = _installed_service(tmp_path, active=False)
    monkeypatch.setenv("HHS_PASS166_STORAGE_DIR", str(service.root))
    monkeypatch.setenv("HHS_PASS218_P166_MODEL_ID", installed["model_id"])
    monkeypatch.setenv("HHS_PASS218_P166_MODEL_ROOT", installed["canonical_model_root"])
    monkeypatch.setenv("HHS_PASS218_P166_INDEX_ROOT", installed["index_root"])
    monkeypatch.setenv("HHS_PASS218_P166_ACTIVATE", "1")

    app = FastAPI()
    control = install_pass218_i20_model_control(
        app,
        FakeLifecycle(),
        FakePostcondition(),
        state_root=tmp_path / "runtime-state",
    )
    assert isinstance(control, Pass218I20RuntimeModelControl)
    with TestClient(app) as client:
        response = client.get(PASS218_I20_STATUS_PATH)
        assert response.status_code == 200
        payload = response.json()
        assert payload["relational_candidate_provider_ready"] is True
        assert payload["browser_model_activation_permitted"] is False
        assert client.post(PASS218_I20_STATUS_PATH).status_code == 405
