from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
V147 = ROOT / "applications/runtime_os/HHS_Alpha_V147_WebGL_120Hz_Independent_Observation.html"
V149 = ROOT / "applications/runtime_os/HHS_Alpha_V149_Server_Owned_VMRC_Observation.html"
MARKER = "<!-- V149: server-owned VMRC snapshot admission; V147/148 cumulative preservation. -->\n"
MODULES = (
    "hhs_gui/rendering/hhs_harmonicode_render_packet_v1.js",
    "hhs_gui/rendering/hhs_observation_graph_cache_v1.js",
    "hhs_gui/rendering/hhs_native_observation_binding_v1.js",
    "hhs_gui/rendering/hhs_webgl_observation_sampler_v1.js",
    "hhs_gui/rendering/hhs_guarded_observation_transport_v1.js",
    "hhs_gui/rendering/hhs_runtime_os_native_observation_bootstrap_v1.js",
)


def test_v149_preserves_v147_source_bytes_without_rewriting_existing_features():
    source = V147.read_bytes()
    updated = V149.read_bytes()
    assert sha256(source).hexdigest() == "61d8d6b39b5730f95868bb1aad9f8b5fae3643fe913a1f48c68c77a9a3c6959c"
    assert updated.count(MARKER.encode()) == 1
    original_prefix, suffix = source.rsplit(b"</body>", 1)
    expanded_prefix, inserted = updated.split(MARKER.encode(), 1)
    assert expanded_prefix == original_prefix
    assert inserted.endswith(b"</body>" + suffix)


def test_v149_embedded_modules_match_repository_exact_source_and_order():
    src = V149.read_text("utf-8")
    _, inserted = src.split(MARKER, 1)
    sections = re.findall(
        r'<script data-hhs-pass220-native-observation="([^"]+)">\n(.*?)\n</script>',
        inserted,
        re.DOTALL,
    )
    assert tuple(name for name, _ in sections) == MODULES
    for name, body in sections:
        assert body == (ROOT / name).read_text("utf-8")
    assert "captureNativeSnapshot" in sections[-1][1]
    assert "payload.native_source_verified!==true" in sections[-2][1]
