from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from hhs_backend.runtime import hhs_native_litert_lm_provider_v1 as provider_module


ROOT = Path(__file__).resolve().parents[1]
INSTALLER_PATH = ROOT / "tools" / "install_production_language_assets.py"
SERVICE_PATH = ROOT / "deploy" / "digitalocean" / "hhs-pass196-integrated-environment.service"
GENERATION_PATH = ROOT / "hhs_backend" / "runtime" / "hhs_pass220_native_causal_lm_generation_v1.py"
REQUIREMENTS_PATH = ROOT / "requirements-native-causal-lm.txt"

MODEL_REPO = "HuggingFaceTB/SmolLM2-135M-Instruct"
MODEL_REVISION = "ee72e5415c002e8fc0566a191a07c0b2b708875a"
MODEL_SHA256 = "5af571cbf074e6d21a03528d2330792e532ca608f24ac70a143f6b369968ab8c"
MODEL_ROOT = (
    "/var/lib/hhs/native-language/models/"
    "smollm2-135m-instruct-ee72e5415c002e8fc0566a191a07c0b2b708875a"
)


def _load_installer():
    spec = importlib.util.spec_from_file_location(
        "hhs_production_language_installer_test_module",
        INSTALLER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_native_causal_production_contract_is_pinned_and_cpu_bounded() -> None:
    installer = INSTALLER_PATH.read_text(encoding="utf-8")
    service = SERVICE_PATH.read_text(encoding="utf-8")
    generation = GENERATION_PATH.read_text(encoding="utf-8")
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    for token in [
        "torch==2.5.1+cpu",
        "transformers==4.46.3",
        "huggingface-hub==0.26.2",
        "safetensors==0.4.5",
        "tokenizers==0.20.3",
        "https://download.pytorch.org/whl/cpu",
    ]:
        assert token in requirements

    for token in [
        f'NATIVE_CAUSAL_MODEL_REPO = "{MODEL_REPO}"',
        f'NATIVE_CAUSAL_MODEL_REVISION = "{MODEL_REVISION}"',
        f'NATIVE_CAUSAL_MODEL_FILE_SHA256 = "{MODEL_SHA256}"',
        "snapshot_download(",
        "revision=NATIVE_CAUSAL_MODEL_REVISION",
        "_sha256_file(model_file)",
        "_native_causal_smoke(model_path)",
        '"HHS_PRODUCTION_LANGUAGE_ASSET_INSTALLATION_STATUS_V2"',
        '"native_generative_ready": native_generative_ready',
        "assistant_ready = bool(gemma.get(\"ready\") or native_generative_ready)",
        '"--strict-generation"',
    ]:
        assert token in installer

    for token in [
        f"Environment=HHS_NATIVE_CAUSAL_LM_MODEL={MODEL_ROOT}",
        "Environment=HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY=1",
        "Environment=HHS_NATIVE_CAUSAL_LM_CPU_FLOAT32=1",
        "Environment=HHS_NATIVE_CAUSAL_LM_MAX_NEW_TOKENS=128",
        "Environment=HHS_NATIVE_RESPONSE_BLOCK_MAX_NEW_TOKENS=128",
        "Environment=HHS_NATIVE_RESPONSE_MAX_BLOCKS=2",
        "Environment=HHS_NATIVE_LANGUAGE_GENERATION_TIMEOUT_SECONDS=60",
        "Environment=HF_HOME=/var/lib/hhs/native-language/hf-cache",
    ]:
        assert token in service

    assert 'model_kwargs["torch_dtype"] = torch.float32' in generation
    assert "eval_model = getattr(model, \"eval\", None)" in generation
    assert '"cpu_float32": _env_flag("HHS_NATIVE_CAUSAL_LM_CPU_FLOAT32", True)' in generation


def test_require_assistant_auto_installs_and_smokes_pinned_native_model(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installer = _load_installer()
    model_root = tmp_path / "model"
    calls: list[tuple[str, str | None]] = []

    monkeypatch.delenv("HHS_NATIVE_CAUSAL_LM_MODEL", raising=False)
    monkeypatch.delenv("HHS_NATIVE_CAUSAL_LM_AUTO_INSTALL", raising=False)
    monkeypatch.setattr(installer, "NATIVE_CAUSAL_MODEL_ROOT", model_root)
    monkeypatch.setattr(
        installer,
        "_install_native_causal_packages",
        lambda: {"ready": True, "installed_now": True},
    )

    def install_model():
        calls.append(("install", str(model_root)))
        return {
            "ready": True,
            "model_root": str(model_root),
            "repo_id": MODEL_REPO,
            "revision": MODEL_REVISION,
            "model_file_sha256": MODEL_SHA256,
        }

    def smoke(path: str):
        calls.append(("smoke", path))
        return {"ready": True, "returncode": 0}

    monkeypatch.setattr(installer, "_install_pinned_native_causal_model", install_model)
    monkeypatch.setattr(installer, "_native_causal_smoke", smoke)

    result = installer._native_causal_install(
        install_if_configured=True,
        require_assistant=True,
    )

    assert result["ready"] is True
    assert result["configured"] is True
    assert result["auto_install"] is True
    assert result["model_path"] == str(model_root)
    assert calls == [("install", str(model_root)), ("smoke", str(model_root))]
    assert installer.os.environ["HHS_NATIVE_CAUSAL_LM_MODEL"] == str(model_root)
    assert installer.os.environ["HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY"] == "1"
    assert installer.os.environ["HHS_NATIVE_CAUSAL_LM_CPU_FLOAT32"] == "1"
    assert installer.os.environ["HHS_NATIVE_CAUSAL_LM_MAX_NEW_TOKENS"] == "128"


class _NativeReadyTransport:
    def installation_status(self):
        return {
            "ready": True,
            "provider_id": "provider:hhs.local.text",
            "causal_lm": {"configured": True},
        }


def test_require_assistant_rejects_structural_native_readiness_without_generation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installer = _load_installer()
    monkeypatch.setattr(installer, "STATUS_PATH", tmp_path / "status.json")
    monkeypatch.setattr(
        installer,
        "_word2vec_install",
        lambda **kwargs: {"ready": False},
    )
    monkeypatch.setattr(
        installer,
        "_litert_cli_status",
        lambda: {"installed": False},
    )
    monkeypatch.setattr(
        installer,
        "_gemma_registry_status",
        lambda: {"ready": False},
    )
    monkeypatch.setattr(
        installer,
        "_native_causal_install",
        lambda **kwargs: {
            "ready": False,
            "configured": False,
            "model_path": None,
        },
    )
    monkeypatch.setattr(
        provider_module,
        "HHSNativeLiteRTLMTransport",
        _NativeReadyTransport,
    )

    with pytest.raises(RuntimeError, match="real causal generator"):
        installer.execute(
            install_if_configured=True,
            require_assistant=True,
        )


def test_native_generation_smoke_promotes_production_assistant_readiness(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installer = _load_installer()
    monkeypatch.setattr(installer, "STATUS_PATH", tmp_path / "status.json")
    monkeypatch.setattr(
        installer,
        "_word2vec_install",
        lambda **kwargs: {"ready": False},
    )
    monkeypatch.setattr(
        installer,
        "_litert_cli_status",
        lambda: {"installed": False},
    )
    monkeypatch.setattr(
        installer,
        "_gemma_registry_status",
        lambda: {"ready": False},
    )
    monkeypatch.setattr(
        installer,
        "_native_causal_install",
        lambda **kwargs: {
            "ready": True,
            "configured": True,
            "model_path": MODEL_ROOT,
            "smoke": {"ready": True},
        },
    )
    monkeypatch.setattr(
        provider_module,
        "HHSNativeLiteRTLMTransport",
        _NativeReadyTransport,
    )

    report = installer.execute(
        install_if_configured=True,
        require_assistant=True,
    )

    assert report["schema"] == "HHS_PRODUCTION_LANGUAGE_ASSET_INSTALLATION_STATUS_V2"
    assert report["assistant_ready"] is True
    assert report["native_generative_ready"] is True
    assert report["selected_provider"] == "provider:hhs.local.text"
    assert report["native_causal"]["ready"] is True


def test_model_permission_normalization_includes_state_ancestor_traversal() -> None:
    source = INSTALLER_PATH.read_text(encoding="utf-8")
    assert 'state_root = Path("/var/lib/hhs")' in source
    assert "ancestors: list[Path] = []" in source
    assert "candidates = [*reversed(ancestors), model_root, *model_root.rglob(\"*\")]" in source
    assert "mode |= stat.S_IXGRP" in source
    assert '"traversal_root": str(state_root)' in source
