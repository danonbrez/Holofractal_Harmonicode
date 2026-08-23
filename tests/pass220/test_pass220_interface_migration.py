from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class Pass220InterfaceMigrationTests(unittest.TestCase):
    def test_api_only_compositor_removes_legacy_static_mounts(self) -> None:
        source = (ROOT / "hhs_backend/api_server.py").read_text(encoding="utf-8")
        ast.parse(source)
        for route_name in (
            "hhs-storybook-reel-studio",
            "hhs-probability-hydration-studio",
            "hhs-visual-home",
        ):
            self.assertIn(route_name, source)
        self.assertIn("DEPRECATED_COMPATIBILITY_ONLY", source)
        self.assertIn("HHS_PASS220_NATIVE_LINUX_VM", source)
        self.assertIn("canonical_mutation_authority_created_here", source)
        self.assertIn("False", source)

    def test_legacy_visual_server_declares_deprecation(self) -> None:
        source = (ROOT / "hhs_backend/visual_server.py").read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn('WEB_FRONTEND_STATUS = "DEPRECATED_COMPATIBILITY_ONLY"', source)
        self.assertIn('PREFERRED_LOCAL_INTERFACE = "HHS_PASS220_NATIVE_LINUX_VM"', source)
        self.assertIn('"web_frontend_removed": False', source)
        self.assertIn('"native_vm_entrypoint": "start_vm.sh"', source)

    def test_launch_scripts_keep_interfaces_separate(self) -> None:
        api = (ROOT / "start_api.sh").read_text(encoding="utf-8")
        vm = (ROOT / "start_vm.sh").read_text(encoding="utf-8")
        web = (ROOT / "start_web_compat.sh").read_text(encoding="utf-8")
        self.assertIn("hhs_backend.api_server:app", api)
        self.assertNotIn("hhs_backend.visual_server:app", api)
        self.assertIn("hhs_pass220_linux_vm.hhs_linux_vm", vm)
        self.assertIn("DEPRECATED", web)
        self.assertIn("start.sh", web)


if __name__ == "__main__":
    unittest.main()
