from __future__ import annotations

from pathlib import Path
from hashlib import sha256
import re

ROOT = Path(__file__).resolve().parents[2]
V147 = ROOT / "applications/runtime_os/HHS_Alpha_V147_WebGL_120Hz_Independent_Observation.html"
V150 = ROOT / "applications/runtime_os/HHS_Alpha_V150_Decay_Pool_Observation.html"
V151 = ROOT / "applications/runtime_os/HHS_Alpha_V151_Admitted_Geometry_WebGL.html"
MARKER150 = "<!-- V150: cumulative native observation with local decay-pool read-only provenance. -->\n"
MARKER151 = "<!-- V151: native C11 command root and admitted geometry WebGL presenter; V150 physical decay observer preserved. -->\n"
MODULES = (
    "hhs_gui/rendering/hhs_harmonicode_render_packet_v1.js",
    "hhs_gui/rendering/hhs_observation_graph_cache_v1.js",
    "hhs_gui/rendering/hhs_native_observation_binding_v1.js",
    "hhs_gui/rendering/hhs_webgl_observation_sampler_v1.js",
    "hhs_gui/rendering/hhs_guarded_observation_transport_v1.js",
    "hhs_gui/rendering/hhs_native_webgl_frame_presenter_v1.js",
    "hhs_gui/rendering/hhs_runtime_os_native_observation_bootstrap_v1.js",
)


def test_v151_preserves_v150_existing_source_except_updated_module_embeds():
    old = V150.read_text("utf-8")
    new = V151.read_text("utf-8")
    assert sha256(V147.read_bytes()).hexdigest() == "61d8d6b39b5730f95868bb1aad9f8b5fae3643fe913a1f48c68c77a9a3c6959c"
    old_prefix = old.split(MARKER150, 1)[0]
    new_prefix = new.split(MARKER151, 1)[0]
    assert new_prefix == old_prefix
    assert "HHS_V150_LOCAL_DECAY_POOL_OBSERVATION_V1" in new_prefix
    assert "virtualDecay(forceIdx)" in new_prefix
    assert "const fractalSeeds=[];" in new_prefix


def test_v151_frozen_embeds_preserve_seven_historical_modules():
    new = V151.read_text("utf-8")
    _, inserted = new.split(MARKER151, 1)
    sections = re.findall(
        r'<script data-hhs-pass220-native-observation="([^"]+)">\n(.*?)\n</script>',
        inserted,
        flags=re.DOTALL,
    )
    assert tuple(path for path, _ in sections) == MODULES
    for path, body in sections:
        assert body.strip()
        assert "function" in body
    assert "presentNativeFrame" in sections[-1][1]
    assert "command_manifest_bound_before_vm81_admission" in sections[-3][1]
    assert "NativeWebGLFramePresenter" in sections[-2][1]
