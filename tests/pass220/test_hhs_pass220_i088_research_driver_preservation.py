"""Regression gate: hidden research wireframe must retain live physics drivers.

This structural test is deliberately scoped to the authoritative HTML on main.
It does not claim browser FPS, native E8 compression, or MP4 completion.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "examples" / "ParticleSimulation.html"


class ResearchDriverPreservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HTML.read_text(encoding="utf-8")

    def test_tesseract_not_mounted(self):
        self.assertNotIn("scene.add(tessGeo.lines);", self.source)
        self.assertIn("tessGeo.lines.visible=false;", self.source)
        self.assertIn("function updateTesseract(){", self.source)
        self.assertIn("projected[o]=x1*s;", self.source)

    def test_poincare_penrose_updates_when_hidden(self):
        match = re.search(
            r"function updatePhaseGeometry\(\)\s*\{(.*?)\n    \}",
            self.source,
            re.S,
        )
        self.assertIsNotNone(match, "Poincare-Penrose driver absent")
        body = match.group(1)
        self.assertIn("phaseBins.fill(0)", body)
        self.assertIn("phaseGeomGroup.visible=false;", body)
        self.assertNotIn("if(!phaseGeomGroup.visible) return;", body)

    def test_physics_and_light_dependency_order_preserved(self):
        source = self.source
        anchor = source.index("function animate() {")
        animation = source[anchor:anchor + 4600]
        phases = (
            "updateSpiralParticles()",
            "updatePhaseGeometry()",
            "syncParticleRenderBatches()",
            "window.HHSPhaseMembranes.sync()",
            "window.HHSLiquidLight.sync()",
            "renderer.render(scene, camera)",
        )
        positions = [animation.index(name) for name in phases]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("const steps=Math.max(1,Math.min(10,simParams.freqScale|0))", animation)

    def test_media_controls_and_source_frame_accounting(self):
        self.assertIn('id="hhs-repository-media-membrane"', self.source)
        for control in ('record', 'stop', 'play', 'live', 'save'):
            self.assertIn('hhs-i088-" + control', self.source)
        self.assertIn('C.track.requestFrame();C.frames++;', self.source)
        self.assertIn('C.sourceFPS', self.source)
        self.assertIn('canonicalMutation:false', self.source)
        self.assertIn('C.video.style.cssText=', self.source)
        self.assertIn('z-index:10050', self.source)
        self.assertIn('z-index:9000', self.source)

    def test_diagnostics_not_serialized_each_frame(self):
        self.assertIn('if(performance.now()-hhsLastDiagnosticStateMs>=2000)', self.source)

    def test_research_hiding_does_not_skip_phase_driver(self):
        self.assertIn('updatePhaseGeometry();', self.source)
        self.assertIn('phaseBins.fill(0)', self.source)

    def test_canonical_physics_not_replaced_by_media(self):
        self.assertIn("initSpiralParticles(false)", self.source)
        self.assertIn("initExchangeNuclei(true)", self.source)
        self.assertIn("initNinthNucleus()", self.source)


if __name__ == "__main__":
    unittest.main()
