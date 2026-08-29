from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VISUAL_SERVER = ROOT / "hhs_backend" / "visual_server.py"


class Pass193VisualRegistrationTests(unittest.TestCase):
    def test_pass193_router_is_explicitly_registered_before_public_federation(self) -> None:
        source = VISUAL_SERVER.read_text(encoding="utf-8")
        import_fragment = (
            "from hhs_backend.api.pass193_hypersolid_routes import router as "
            "pass193_hypersolid_router"
        )
        include_fragment = "app.include_router(pass193_hypersolid_router)"
        federation_fragment = "PUBLIC_API_REGISTRATION = register_public_api_federation(app)"
        self.assertIn(import_fragment, source)
        self.assertIn('if not _route_exists("/api/runtime/hypersolids/status"):', source)
        self.assertIn(include_fragment, source)
        self.assertIn(federation_fragment, source)
        self.assertLess(source.index(include_fragment), source.index(federation_fragment))

    def test_system_status_exposes_pass193_api_and_contract_identity(self) -> None:
        source = VISUAL_SERVER.read_text(encoding="utf-8")
        self.assertIn('"pass193_hypersolid_api": "/api/runtime/hypersolids"', source)
        self.assertIn(
            '"pass193_hypersolid_native_egress": '
            '"HHS-P193-RHFM-EPRP-NF-NC-SNFTE-VM81-H72-H216"',
            source,
        )


if __name__ == "__main__":
    unittest.main()
