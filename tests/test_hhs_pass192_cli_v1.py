from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass192.cli import build_parser, dispatch


def authority(index: int) -> dict[str, object]:
    state = hash72_digest({"domain": "P192_CLI_STATE"}, {"index": index})
    receipt = hash72_digest({"domain": "P192_CLI_RECEIPT"}, {"index": index})
    return {
        "runtime": {"state_hash72": state},
        "receipt": {"state_hash72": state, "receipt_hash72": receipt},
        "authority_audit": {
            "ok": True,
            "state_hash72": state,
            "receipt_hash72": receipt,
        },
    }


class Pass192CLITests(unittest.TestCase):
    def test_required_shell_grammar_create_inspect_materialize_validate_replay(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "runtime"
            auth = Path(temp) / "authority.json"
            auth.write_text(json.dumps(authority(1)), encoding="utf-8")
            parser = build_parser()

            create = parser.parse_args([
                "--runtime-root", str(root),
                "tensor", "fibonacci", "create",
                "--cell", "0,0",
                "--authority-json", str(auth),
            ])
            tensor = dispatch(create)
            self.assertEqual(tensor["lo_shu_cell_coordinate"], [0, 0])

            inspect = parser.parse_args([
                "--runtime-root", str(root),
                "tensor", "fibonacci", "inspect", tensor["tensor_id"],
            ])
            self.assertEqual(dispatch(inspect)["tensor_id"], tensor["tensor_id"])

            materialize = parser.parse_args([
                "--runtime-root", str(root),
                "tensor", "fibonacci", "materialize", tensor["tensor_id"],
                "--depth", "1",
                "--authority-json", str(auth),
            ])
            self.assertEqual(dispatch(materialize)["node_count"], 50)

            validate = parser.parse_args([
                "--runtime-root", str(root),
                "tensor", "fibonacci", "validate", tensor["tensor_id"],
            ])
            self.assertTrue(dispatch(validate)["ok"])

            replay = parser.parse_args([
                "--runtime-root", str(root),
                "tensor", "fibonacci", "replay", tensor["tensor_id"],
            ])
            self.assertTrue(dispatch(replay)["ok"])


if __name__ == "__main__":
    unittest.main()
