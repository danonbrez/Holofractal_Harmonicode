from __future__ import annotations

from pathlib import Path
from hashlib import sha256
import re

ROOT = Path(__file__).resolve().parents[2]
V147 = ROOT / "applications/runtime_os/HHS_Alpha_V147_WebGL_120Hz_Independent_Observation.html"
V151 = ROOT / "applications/runtime_os/HHS_Alpha_V151_Admitted_Geometry_WebGL.html"
V152 = ROOT / "applications/runtime_os/HHS_Alpha_V152_Ordered_Physical_Geometry_Observation.html"
MARKER151 = "<!-- V151: native C11 command root and admitted geometry WebGL presenter; V150 physical decay observer preserved. -->\n"
MARKER152 = "<!-- V152: cumulative exact physical geometry observation; V151 admitted geometry presenter preserved. -->\n"
SOURCE_ANCHOR = "    let thPos=null, thVel=null, thMass=null, thGrp=null, thPhase=null, thPh4=null, thChg=null, nbCount=null;"
GEOMETRY_BEGIN = "    /* V152: read-only ordered particle geometry export from EXISTING thPos."
GEOMETRY_END = "    const tHead="
MODULES = (
    "hhs_gui/rendering/hhs_harmonicode_render_packet_v1.js",
    "hhs_gui/rendering/hhs_observation_graph_cache_v1.js",
    "hhs_gui/rendering/hhs_native_observation_binding_v1.js",
    "hhs_gui/rendering/hhs_webgl_observation_sampler_v1.js",
    "hhs_gui/rendering/hhs_guarded_observation_transport_v1.js",
    "hhs_gui/rendering/hhs_native_webgl_frame_presenter_v1.js",
    "hhs_gui/rendering/hhs_runtime_os_native_observation_bootstrap_v1.js",
)


def test_v152_preserves_v151_physics_and_decay_observer_except_additive_geometry():
    original = V151.read_text("utf-8")
    updated = V152.read_text("utf-8")
    old_prefix = original.split(MARKER151, 1)[0]
    new_prefix = updated.split(MARKER152, 1)[0]
    assert new_prefix.count(GEOMETRY_BEGIN) == 1
    pre, after = new_prefix.split(GEOMETRY_BEGIN, 1)
    assert GEOMETRY_END in after
    _, post = after.split(GEOMETRY_END, 1)
    assert pre + GEOMETRY_END + post == old_prefix
    assert "HHS_V150_LOCAL_DECAY_POOL_OBSERVATION_V1" in new_prefix
    assert "virtualDecay(forceIdx)" in new_prefix
    assert sha256(V147.read_bytes()).hexdigest() == "61d8d6b39b5730f95868bb1aad9f8b5fae3643fe913a1f48c68c77a9a3c6959c"


def test_v152_embeds_seven_current_native_modules_byte_identically():
    text = V152.read_text("utf-8")
    _, inserted = text.split(MARKER152, 1)
    sections = re.findall(
        r'<script data-hhs-pass220-native-observation="([^"]+)">\n(.*?)\n</script>',
        inserted,
        flags=re.DOTALL,
    )
    assert tuple(name for name, _ in sections) == MODULES
    for path, body in sections:
        assert body == (ROOT / path).read_text("utf-8")
    assert "readLocalGeometry" in sections[-1][1]
    assert "NativeWebGLFramePresenter" in sections[-2][1]
