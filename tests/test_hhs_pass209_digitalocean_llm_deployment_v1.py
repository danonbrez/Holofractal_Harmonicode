from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deployment" / "digitalocean" / "llm"


def test_pass209_contract_and_required_artifacts_exist() -> None:
    contract = json.loads(
        (ROOT / "contracts" / "pass209" / "PASS_209_CONTRACT.json").read_text(
            encoding="utf-8"
        )
    )
    assert contract["pass"] == 209
    assert contract["provider_hierarchy"][0]["model_id"] == "kimi-k3"
    assert contract["provider_hierarchy"][1]["model_id"] == "gemma-4-E2B-it"
    assert contract["native_backend_agent"]["user_facing_fallback"] is False
    assert contract["native_backend_agent"]["may_mutate_vm81_directly"] is False
    for relative in contract["required_artifacts"]:
        assert (ROOT / relative).is_file(), relative


def test_installer_pins_litert_model_and_never_embeds_a_secret() -> None:
    install = (DEPLOY / "install.sh").read_text(encoding="utf-8")
    assert "litert-lm==$LITERT_VERSION" in install
    assert "0.14.0" in install
    assert "litert-community/gemma-4-E2B-it-litert-lm" in install
    assert "gemma-4-E2B-it.litertlm" in install
    assert "181938105e0eefd105961417e8da75903eacda102c4fce9ce90f50b97139a63c" in install
    assert "MOONSHOT_API_KEY" in install
    assert "Set MOONSHOT_API_KEY" in install
    assert "replace-with-secret" not in install
    assert "Authorization: Bearer $API_KEY" in install
    assert "api_key_exposed" not in install


def test_systemd_orders_local_fallback_before_hhs_and_native_optimizer_after() -> None:
    gemma = (DEPLOY / "hhs-litert-lm-gemma4.service").read_text(encoding="utf-8")
    optimizer = (DEPLOY / "hhs-native-agi-optimizer.service").read_text(encoding="utf-8")
    install = (DEPLOY / "install.sh").read_text(encoding="utf-8")

    assert "User=hhs" in gemma
    assert "litert-lm serve --host 127.0.0.1 --port 9379" in gemma
    assert "ReadWritePaths=/var/lib/hhs/litert-lm" in gemma
    assert "After=network-online.target hhs.service" in optimizer
    assert "pass209_native_agi_optimizer_worker.py" in optimizer
    assert "ReadWritePaths=/var/lib/hhs/pass209" in optimizer
    assert "After=hhs-litert-lm-gemma4.service" in install
    assert "Wants=hhs-litert-lm-gemma4.service" in install
    assert "ExecStartPre=$INSTALL_ROOT/hhs-llm-preflight.sh" in install


def test_preflight_requires_kimi_configuration_and_registered_local_fallback() -> None:
    preflight = (DEPLOY / "hhs-llm-preflight.sh").read_text(encoding="utf-8")
    assert "MOONSHOT_API_KEY" in preflight
    assert "HHS_KIMI_K3_MODEL must be kimi-k3" in preflight
    assert "HHS_LITERT_LM_MODEL must be gemma-4-E2B-it" in preflight
    assert "HHS_LITERT_LM_BACKEND" in preflight
    assert "http://127.0.0.1:9379/v1/models" in preflight
    assert "native_agi_is_user_facing_provider" in preflight
    assert "runtime_mutation_admitted" in preflight


def test_public_assistant_routes_resolve_pass209_hierarchy() -> None:
    routes = (ROOT / "hhs_backend" / "api" / "litert_lm_assistant_routes.py").read_text(
        encoding="utf-8"
    )
    production = (
        ROOT / "hhs_backend" / "runtime" / "hhs_pass209_production_assistant_v1.py"
    ).read_text(encoding="utf-8")
    assert "DEFAULT_PASS209_PRODUCTION_ASSISTANT" in routes
    assert "KIMI_K3_AGENTIC_SWARM_API" in production
    assert "GEMMA4_LITERT_LM_FALLBACK" in production
    assert "native_agi_is_user_facing_provider" in production
    assert "HHS_NATIVE_LITERT_COMPATIBLE" not in production
