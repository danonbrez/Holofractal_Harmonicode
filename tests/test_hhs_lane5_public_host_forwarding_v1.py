"""Regression for public Host preservation at the Lane5 HTTP forwarding boundary."""
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[1]
GATEWAY = ROOT / "hhs_backend/lane5_ingress_gateway.py"


class TestPublicHostForwarding(unittest.TestCase):
    def test_gateway_preserves_host_at_forwarding_boundary(self):
        text = GATEWAY.read_text(encoding="utf-8")
        tree = ast.parse(text)
        fn = next(node for node in tree.body
                  if isinstance(node, ast.AsyncFunctionDef) and node.name == "_http_proxy")
        forwarded = ast.get_source_segment(text, fn)
        self.assertIn("_filtered_headers(raw_headers)", forwarded)
        self.assertIn('if name.lower() != b"content-length"', forwarded)
        self.assertNotIn('b"content-length", b"host"', forwarded)
        self.assertIn("http_client.build_request(", forwarded)
        self.assertIn("headers=headers", forwarded)

    def test_reserved_headers_are_still_filtered(self):
        text = GATEWAY.read_text(encoding="utf-8")
        tree = ast.parse(text)
        fn = next(node for node in tree.body
                  if isinstance(node, ast.FunctionDef) and node.name == "_filtered_headers")
        snippet = ast.get_source_segment(text, fn)
        self.assertIn("_HOP_BY_HOP", snippet)
        self.assertIn("_RESERVED_INGRESS_HEADER_PREFIX", snippet)
        self.assertIn("result.append((bytes(name), bytes(value)))", snippet)


if __name__ == "__main__":
    unittest.main()
