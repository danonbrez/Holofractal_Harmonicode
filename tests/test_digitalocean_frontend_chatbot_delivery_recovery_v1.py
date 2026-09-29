from __future__ import annotations

import subprocess
from pathlib import Path

from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "deployment" / "digitalocean" / "guarded_auto_update" / "install.sh"


def test_guarded_updater_assignments_use_physical_newlines() -> None:
    source = INSTALLER.read_text(encoding="utf-8")

    assert "\\nSTATIC_FIRST_CONFIGURATOR=" not in source
    assert "\\nNATIVE_BUILD=" not in source
    assert "\nSTATIC_FIRST_CONFIGURATOR=" in source
    assert "\nNATIVE_BUILD=" in source

    lines = source.splitlines()
    assignments = {
        line.split("=", 1)[0]: line
        for line in lines
        if line.startswith(
            (
                "RECOVERY_VERIFIER=",
                "STATIC_FIRST_CONFIGURATOR=",
                "NATIVE_BUILD=",
            )
        )
    }
    assert set(assignments) == {
        "RECOVERY_VERIFIER",
        "STATIC_FIRST_CONFIGURATOR",
        "NATIVE_BUILD",
    }
    subprocess.run(["bash", "-n", str(INSTALLER)], check=True)


def test_semantic_cache_prefers_explicit_production_state(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "explicit" / "semantic-cache.json"
    monkeypatch.setenv("HHS_LIVE_SEMANTIC_COMPOSITION_CACHE_PATH", str(target))
    monkeypatch.setenv("HHS_RUNTIME_OUTPUT_DIR", str(tmp_path / "fallback"))

    cache = SemanticCompositionCache()
    assert cache.path == target
    cache.save({"schema": "TEST"})
    assert target.is_file()


def test_semantic_cache_falls_back_to_runtime_output_dir(monkeypatch, tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    monkeypatch.delenv("HHS_LIVE_SEMANTIC_COMPOSITION_CACHE_PATH", raising=False)
    monkeypatch.setenv("HHS_RUNTIME_OUTPUT_DIR", str(runtime_root))

    cache = SemanticCompositionCache()
    expected = runtime_root / "hhs_live_semantic_composition_cache_pass217.json"
    assert cache.path == expected
    cache.save({"schema": "TEST"})
    assert expected.is_file()
