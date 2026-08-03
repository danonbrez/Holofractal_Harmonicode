from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


class DigitalOceanTLSRenewalAssetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.assets = cls.root / "deploy" / "digitalocean" / "tls"

    def test_shell_sources_parse(self) -> None:
        for name in ("hhs-tls-renew.sh", "install.sh"):
            result = subprocess.run(
                ["bash", "-n", str(self.assets / name)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_timer_is_persistent_and_bounded(self) -> None:
        timer = self.assets.joinpath("hhs-tls-renew.timer").read_text(
            encoding="utf-8"
        )
        self.assertIn("OnBootSec=5min", timer)
        self.assertIn("OnUnitActiveSec=12h", timer)
        self.assertIn("Persistent=true", timer)

    def test_watchdog_is_fail_closed_and_does_not_open_application_port(self) -> None:
        script = self.assets.joinpath("hhs-tls-renew.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("openssl", script)
        self.assertIn("-checkend", script)
        self.assertIn("-verify_return_error", script)
        self.assertIn("-verify_hostname", script)
        self.assertIn("-verify_ip", script)
        self.assertIn("-CApath /etc/ssl/certs", script)
        self.assertIn('certificate_valid_for "${renew_window_seconds}"', script)
        self.assertIn("nginx -t", script)
        self.assertIn("TLS_RENEWAL_FAILED_POSTCONDITION", script)
        self.assertIn("not extended beyond", script)
        self.assertNotIn("ufw allow 8080", script)
        self.assertNotIn("0.0.0.0:8080", script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
