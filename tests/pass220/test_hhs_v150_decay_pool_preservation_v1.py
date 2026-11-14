from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
V147 = ROOT / "applications/runtime_os/HHS_Alpha_V147_WebGL_120Hz_Independent_Observation.html"
V150 = ROOT / "applications/runtime_os/HHS_Alpha_V150_Decay_Pool_Observation.html"
MARKER = "<!-- V150: cumulative native observation with local decay-pool read-only provenance. -->\n"
BEGIN = "    /* V150 additive observation of the EXISTING physical decay producer."
END = "    function dtFrame()"
MODULES = (
    "hhs_gui/rendering/hhs_harmonicode_render_packet_v1.js",
    "hhs_gui/rendering/hhs_observation_graph_cache_v1.js",
    "hhs_gui/rendering/hhs_native_observation_binding_v1.js",
    "hhs_gui/rendering/hhs_webgl_observation_sampler_v1.js",
    "hhs_gui/rendering/hhs_guarded_observation_transport_v1.js",
    "hhs_gui/rendering/hhs_runtime_os_native_observation_bootstrap_v1.js",
)


def test_v150_preserves_every_v147_byte_except_one_additive_observer():
    baseline = V147.read_text("utf-8")
    target = V150.read_text("utf-8")
    assert sha256(V147.read_bytes()).hexdigest() == "61d8d6b39b5730f95868bb1aad9f8b5fae3643fe913a1f48c68c77a9a3c6959c"
    assert target.count(MARKER) == 1
    candidate, appended = target.split(MARKER, 1)
    original_prefix, suffix = baseline.rsplit("</body>", 1)
    assert appended.endswith("</body>" + suffix)
    assert candidate.count(BEGIN) == 1
    before, extra = candidate.split(BEGIN, 1)
    assert END in extra
    _, after = extra.split(END, 1)
    assert before + END + after == original_prefix
    assert "decayCount++;" in candidate
    assert "virtualDecay(forceIdx)" in candidate


def test_v150_historical_module_snapshot_is_preserved_in_order():
    target = V150.read_text("utf-8")
    _, appended = target.split(MARKER, 1)
    sections = re.findall(
        r'<script data-hhs-pass220-native-observation="([^"]+)">\n(.*?)\n</script>',
        appended, re.DOTALL,
    )
    assert tuple(name for name, _ in sections) == MODULES
    for name, script in sections:
        assert script.strip()
        assert "function" in script
    assert "readLocalDecayPool()" in sections[-1][1]
