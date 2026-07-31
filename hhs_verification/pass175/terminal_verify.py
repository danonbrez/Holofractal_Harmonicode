#!/usr/bin/env python3
"""Execute terminal Pass 175 verification through inherited Pass 174/VM81 authority."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hhs_runtime.pass174 import Pass174Runtime
from hhs_runtime.pass175 import (
    EncryptedHash216Store,
    HydratedMicrocodeStore,
    Pass175Runtime,
    TerminalPass175Runtime,
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--native-root", required=True)
    parser.add_argument(
        "--output",
        default="evidence/pass175/generated/PASS_175_TERMINAL_COMPLETION_RECEIPT.json",
    )
    args = parser.parse_args()

    repository_root = Path(args.repository_root).resolve()
    native_root = Path(args.native_root).resolve()
    output = (repository_root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="hhs-pass175-terminal-") as temporary:
        state_root = Path(temporary)
        authority = Pass174Runtime(repository_root=repository_root)
        base = Pass175Runtime(
            authority=authority,
            microcode_store=HydratedMicrocodeStore(state_root / "base_microcode.jsonl"),
        )
        secure = EncryptedHash216Store(
            state_root / "hash216_microcode.sqlite3",
            key_path=state_root / "hash216_microcode.key",
        )
        runtime = TerminalPass175Runtime(
            base_runtime=base,
            secure_store=secure,
            repository_root=repository_root,
        )
        hydration = runtime.cold_hydrate_terminal(seal=True)
        receipt = runtime.terminal_verification(native_root=native_root, require_boot=True)
        receipt["verification_environment"] = {
            "repository_root": repository_root.name,
            "native_root_name": native_root.name,
            "hydration_store_root_sha256": hydration["secure_store"]["store_root_sha256"],
            "vercel_status_considered": False,
            "external_deployment_quota_is_not_acceptance_gate": True,
        }
        body = dict(receipt)
        body.pop("repository_receipt_sha256", None)
        receipt["repository_receipt_sha256"] = sha256(
            b"HHS-P175-TERMINAL-REPOSITORY-RECEIPT\0" + canonical(body)
        ).hexdigest()
        output.write_text(
            json.dumps(receipt, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        secure.close()

    if not receipt.get("terminal_pass175_completion"):
        print(output.read_text(encoding="utf-8"))
        return 1
    print(json.dumps({
        "classification": receipt["classification"],
        "output": str(output),
        "receipt_sha256": receipt["receipt_sha256"],
        "repository_receipt_sha256": receipt["repository_receipt_sha256"],
        "terminal_pass175_completion": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
