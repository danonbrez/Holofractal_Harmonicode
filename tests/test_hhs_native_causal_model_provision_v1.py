from __future__ import annotations

from hashlib import sha256
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVISIONER_PATH = ROOT / "tools" / "provision_native_causal_model.py"
INSTALLER_PATH = ROOT / "tools" / "install_production_language_assets.py"
SERVICE_PATH = ROOT / "deploy" / "digitalocean" / "hhs-pass196-integrated-environment.service"
REQUIREMENTS_PATH = ROOT / "requirements-native-causal-lm.txt"


def _load_provisioner():
    spec = importlib.util.spec_from_file_location(
        "hhs_native_causal_provision_test_module",
        PROVISIONER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_production_native_causal_model_identity_is_pinned() -> None:
    module = _load_provisioner()

    assert module.MODEL_REPOSITORY == "HuggingFaceTB/SmolLM2-360M-Instruct"
    assert module.MODEL_REVISION == "a10cc1512eabd3dde888204e902eca88bddb4951"
    assert (
        module.MODEL_WEIGHT_SHA256
        == "e6bffe7435d7ddc10fd3b9a9efd429dafbacb1cb17015fb5562664e7532bf86e"
    )
    assert module.MODEL_ID == "smollm2-360m-instruct-a10cc1512ea"
    assert "model.safetensors" in module.REQUIRED_MODEL_FILES
    assert "training_args.bin" not in module.ALLOWED_MODEL_FILES
    assert "trainer_state.json" not in module.ALLOWED_MODEL_FILES
    assert "onnx" not in module.ALLOWED_MODEL_FILES


def test_native_causal_runtime_is_cpu_only_and_separately_pinned() -> None:
    module = _load_provisioner()
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    assert module.EXPECTED_RUNTIME_VERSIONS == {
        "transformers": "4.57.6",
        "torch": "2.14.1+cpu",
    }
    assert module.TORCH_CPU_INDEX_URL == "https://download.pytorch.org/whl/cpu"
    assert "transformers==4.57.6" in requirements
    assert "torch" not in requirements

    source = PROVISIONER_PATH.read_text(encoding="utf-8")
    assert "torch.version" in source
    assert '"cuda_version"' in source
    assert "TORCH_CPU_INDEX_URL" in source
    assert '"--index-url"' in source


def test_existing_model_verification_rejects_wrong_weight_identity(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _load_provisioner()
    monkeypatch.setattr(module, "_model_root", lambda: tmp_path)

    target = module.model_path()
    target.mkdir(parents=True)
    for name in module.REQUIRED_MODEL_FILES:
        (target / name).write_bytes(
            b"wrong-weight" if name == "model.safetensors" else b"{}"
        )

    try:
        module._verify_existing_model()
    except RuntimeError as exc:
        assert "weight identity mismatch" in str(exc)
    else:
        raise AssertionError("wrong native causal weight identity was accepted")


def test_existing_model_verification_accepts_exact_pinned_weight(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _load_provisioner()
    monkeypatch.setattr(module, "_model_root", lambda: tmp_path)

    payload = b"test-pinned-weight"
    monkeypatch.setattr(module, "MODEL_WEIGHT_SHA256", sha256(payload).hexdigest())

    target = module.model_path()
    target.mkdir(parents=True)
    for name in module.REQUIRED_MODEL_FILES:
        (target / name).write_bytes(
            payload if name == "model.safetensors" else b"{}"
        )

    report = module._verify_existing_model()
    assert report["revision"] == module.MODEL_REVISION
    assert report["model_weight_sha256"] == sha256(payload).hexdigest()
    assert report["network_download_required_after_provisioning"] is False


def test_production_language_installer_requires_real_causal_readiness() -> None:
    installer = INSTALLER_PATH.read_text(encoding="utf-8")

    for token in [
        "HHS_NATIVE_CAUSAL_LM_AUTO_PROVISION",
        "HHS_NATIVE_CAUSAL_LM_REQUIRED",
        '"provision_native_causal_model.py"',
        '"native_causal": native_causal',
        '"native_hhs_conversation_ready": native_ready',
        'native.get("ready")',
        'native_causal.get("ready")',
    ]:
        assert token in installer


def test_production_service_binds_exact_local_causal_model() -> None:
    service = SERVICE_PATH.read_text(encoding="utf-8")

    for token in [
        "Environment=HHS_NATIVE_CAUSAL_LM_REQUIRED=1",
        (
            "Environment=HHS_NATIVE_CAUSAL_LM_MODEL=/var/lib/hhs/models/"
            "native-causal/smollm2-360m-instruct-a10cc1512ea"
        ),
        "Environment=HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY=1",
        "Environment=HHS_NATIVE_LANGUAGE_GENERATION_TIMEOUT_SECONDS=60",
        "Environment=OMP_NUM_THREADS=2",
        "Environment=MKL_NUM_THREADS=2",
    ]:
        assert token in service
