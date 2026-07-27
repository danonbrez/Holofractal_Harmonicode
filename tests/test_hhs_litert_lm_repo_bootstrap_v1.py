from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_litert_lm_is_a_declared_repository_dependency() -> None:
    provider_requirements = (ROOT / "requirements-litert-lm.txt").read_text(encoding="utf-8")
    root_requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert "litert-lm==0.14.0" in provider_requirements
    assert "-r requirements-litert-lm.txt" in root_requirements


def test_repository_launchers_are_shell_valid() -> None:
    scripts = [
        ROOT / "start.sh",
        ROOT / "tools" / "bootstrap_litert_lm.sh",
        ROOT / "tools" / "import_hhs_gemma4_model.sh",
        ROOT / "tools" / "start_hhs_gemma4_assistant.sh",
    ]
    subprocess.run(["bash", "-n", *map(str, scripts)], check=True)


def test_primary_start_path_models_gpu_provider_topologies() -> None:
    launcher = (ROOT / "start.sh").read_text(encoding="utf-8")

    assert 'HHS_LITERT_LM_PORT:-9379' in launcher
    assert 'HHS_LITERT_LM_BACKEND:-gpu' in launcher
    assert 'HHS_LITERT_LM_PROVIDER_MODE:-auto' in launcher
    assert 'HHS_LITERT_LM_STRICT_STARTUP:-0' in launcher
    assert 'probe_litert_lm_accelerator.py' in launcher
    assert 'bootstrap_litert_lm.sh" --print-bin' in launcher
    assert '"$litert_bin" serve' in launcher
    assert "verify_requested_model" in launcher
    assert "assistant-degraded mode" in launcher


def test_accelerator_probe_cpu_control_path() -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "probe_litert_lm_accelerator.py"),
            "--backend",
            "cpu",
            "--require",
        ],
        check=True,
    )


def test_model_import_contract_matches_hhs_provider_alias() -> None:
    importer = (ROOT / "tools" / "import_hhs_gemma4_model.sh").read_text(
        encoding="utf-8"
    )

    assert "litert-community/gemma-4-12B-it-litert-lm" in importer
    assert "gemma-4-12B-it.litertlm" in importer
    assert "gemma4-12b" in importer
