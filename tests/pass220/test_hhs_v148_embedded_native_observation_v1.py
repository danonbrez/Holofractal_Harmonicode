from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
V147 = ROOT / "applications/runtime_os/HHS_Alpha_V147_WebGL_120Hz_Independent_Observation.html"
V148 = ROOT / "applications/runtime_os/HHS_Alpha_V148_Native_Observation_Bridge.html"
MARKER = "<!-- V148: additive Pass220 native GFX4 observation bridge; V147 physics and renderer preserved. -->\n"
MODULES = [
    "hhs_gui/rendering/hhs_harmonicode_render_packet_v1.js",
    "hhs_gui/rendering/hhs_observation_graph_cache_v1.js",
    "hhs_gui/rendering/hhs_native_observation_binding_v1.js",
    "hhs_gui/rendering/hhs_webgl_observation_sampler_v1.js",
    "hhs_gui/rendering/hhs_guarded_observation_transport_v1.js",
    "hhs_gui/rendering/hhs_runtime_os_native_observation_bootstrap_v1.js",
]


def test_v147_source_preserved_exactly_as_v148_parent():
    original = V147.read_bytes()
    updated = V148.read_bytes()
    assert sha256(original).hexdigest() == "61d8d6b39b5730f95868bb1aad9f8b5fae3643fe913a1f48c68c77a9a3c6959c"
    assert updated.count(MARKER.encode()) == 1
    prefix, inserted = updated.split(MARKER.encode(), 1)
    before_body, closing_body = original.rsplit(b"</body>", 1)
    assert prefix == before_body
    assert closing_body.endswith(b"</html>")
    assert inserted.endswith(b"</body>" + closing_body)


def test_all_embedded_native_modules_are_exact_repository_sources_in_order():
    original = V147.read_text("utf-8")
    updated = V148.read_text("utf-8")
    prefix, injected = updated.split(MARKER, 1)
    assert prefix == original.rsplit("</body>", 1)[0]
    for path in MODULES:
        token = '<script data-hhs-pass220-native-observation="' + path + '">\n'
        assert injected.count(token) == 1
    sections = re.findall(
        r'<script data-hhs-pass220-native-observation="([^"]+)">\n(.*?)\n</script>',
        injected, flags=re.DOTALL,
    )
    assert [path for path, _ in sections] == MODULES
    for path, body in sections:
        assert body == (ROOT / path).read_text("utf-8")
    assert all("src=" not in body for _, body in sections)
