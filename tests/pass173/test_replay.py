from __future__ import annotations

from hhs_verification.pass173.replay import InstallationReplay


def _capsule() -> dict[str, object]:
    return {
        "request": {"profile": "core"},
        "probe": {"platform": "Linux", "architecture": "x86_64"},
        "plan": {"resolved_profile": "core"},
        "artifacts": {
            "source": "source",
            "dependencies": "deps",
            "native": "native",
            "frontend": {},
            "provider": "disabled",
            "model": "skip",
        },
        "validation": {"passed": 12, "failed": 0},
    }


def test_logical_replay_is_deterministic() -> None:
    capsule = _capsule()
    first = InstallationReplay.logical(**capsule)
    second = InstallationReplay.logical(**capsule)
    assert first.matched is True
    assert first.input_identity == second.input_identity
    assert first.reconstructed_identity == second.reconstructed_identity


def test_clean_environment_comparison_detects_divergence() -> None:
    first = {"profile": "core", "result": "A", "temporary_path": "/tmp/a"}
    second = {"profile": "core", "result": "A", "temporary_path": "/tmp/b"}
    match = InstallationReplay.compare_clean_runs(
        first,
        second,
        platform_bound_fields=("temporary_path",),
    )
    assert match.matched is True

    mismatch = InstallationReplay.compare_clean_runs(first, {"profile": "runtime", "result": "A"})
    assert mismatch.matched is False
    assert mismatch.classification == "P173_FINAL_CLEAN_REPLAY_DIVERGENCE"
