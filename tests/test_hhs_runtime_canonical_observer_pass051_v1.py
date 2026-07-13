from hhs_backend.runtime.hhs_runtime_canonical_observer_v1 import (
    runtime_canonical_observer_self_test,
    observe_external_surface,
    admit_runtime_identity,
)


def test_canonical_observer_self_test():
    assert runtime_canonical_observer_self_test()["ok"]


def test_provider_cannot_be_canonical():
    obs = observe_external_surface(surface_type="PROVIDER", surface_id="provider:x", payload="raw")
    rejected = admit_runtime_identity(
        observation=dict(obs, provider_is_canonical=True),
        translated_record={"schema": "HHS_TRANSLATED_PROVIDER_RESULT_V1"},
        authority_decision={"ok": True},
    )
    assert not rejected["ok"]
    assert "REJECT_PROVIDER_AS_CANONICAL_AUTHORITY" in rejected["reasons"]
