from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / "deploy/digitalocean/hhs-pass196-integrated-environment.service"


def test_production_mutable_state_roots_stay_out_of_checkout() -> None:
    text = UNIT.read_text(encoding="utf-8")
    required = {
        "Environment=HHS_REPO_ROOT=/opt/hhs/app",
        "Environment=HHS_STORYBOOK_REEL_ARTIFACT_ROOT=/var/lib/hhs/storybook-reels",
        "Environment=HHS_VULKAN_RUNTIME_ROOT=/var/lib/hhs/vulkan-runtime",
        "Environment=HHS_PASS203_STATE_ROOT=/var/lib/hhs/pass203",
        "Environment=HHS_PASS204_STATE_ROOT=/var/lib/hhs/pass204",
        "Environment=HHS_RUNTIME_CERTIFICATION_DIR=/var/lib/hhs/runtime-certification",
        "Environment=HHS_GRAPHICS_HYDRATION_ROOT=/var/lib/hhs/graphics-hydration",
        "ReadWritePaths=/var/lib/hhs",
    }
    for expected in required:
        assert expected in text
    assert "ReadWritePaths=/opt/hhs/app" not in text


def test_storybook_runtime_has_explicit_production_state_binding() -> None:
    source = (
        ROOT / "hhs_backend/runtime/hhs_storybook_reel_v1.py"
    ).read_text(encoding="utf-8")
    assert 'os.environ.get("HHS_STORYBOOK_REEL_ARTIFACT_ROOT")' in source
