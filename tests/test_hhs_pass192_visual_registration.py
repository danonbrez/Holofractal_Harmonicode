from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Pass192VisualRegistrationTests(unittest.TestCase):
    def test_pass192_router_is_explicitly_registered_before_public_federation(self) -> None:
        text = (ROOT / "hhs_backend/visual_server.py").read_text(encoding="utf-8")
        import_marker = (
            "from hhs_backend.api.pass192_fibonacci_routes "
            "import router as pass192_fibonacci_router"
        )
        include_marker = (
            'if not _route_exists("/v1/tensors/fibonacci/status"):\n'
            "    app.include_router(pass192_fibonacci_router)"
        )
        federation_marker = (
            "PUBLIC_API_REGISTRATION = register_public_api_federation(app)"
        )
        self.assertIn(import_marker, text)
        self.assertIn(include_marker, text)
        self.assertLess(text.index(include_marker), text.index(federation_marker))
        self.assertIn(
            '"pass192_fibonacci_api": "/v1/tensors/fibonacci"',
            text,
        )
        self.assertIn(
            '"pass192_cellular_fibonacci": "HHS-P192-LSCFNT-MMD-VM81-H72-H216"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
