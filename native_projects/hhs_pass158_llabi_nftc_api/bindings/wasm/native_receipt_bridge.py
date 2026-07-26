#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
PROJECT = HERE.parents[2]
sys.path.insert(0, str(PROJECT / "bindings" / "python"))

from hhs_pass158_core import Context, ExactRational  # noqa: E402


def main() -> None:
    request = json.load(sys.stdin)
    definition = request["definition"]
    with Context() as context:
        native_definition, definition_receipt = context.register_definition(
            name=str(definition.get("name", "PASS158_WASM_OBJECT")),
            constraints=str(definition["constraints"]),
            symbols=",".join(str(item) for item in definition.get("orderedSymbols", [])) or "x",
            shape=[int(item) for item in definition["tensorShape"]],
        )
        response = {
            "kernelAuthority": "HHS_PASS158_NATIVE_ABI",
            "definitionId": native_definition.definition_id,
            "definitionReceipt": definition_receipt.serialize(),
            "definitionReplay": definition_receipt.replay(),
        }
        if request.get("mode") == "identity":
            print(json.dumps(response, sort_keys=True))
            return
        instance, instance_receipt = native_definition.instantiate(b"wasm-native-receipt-bridge")
        with instance.capability(commit=True) as capability:
            for symbol, binding in sorted(request.get("bindings", {}).items()):
                if binding.get("kind") != "RATIONAL":
                    raise ValueError("TYPE_MISMATCH")
                numerator, denominator = str(binding["value"]).split("/", 1)
                instance.bind_rational(
                    symbol,
                    ExactRational(int(numerator), int(denominator)),
                    capability,
                )
            projection, receipt = instance.project(str(request.get("profile", "IEEE754_BINARY64_CONTROL")))
        replay = receipt.replay()
        response.update(
            {
                "instanceReceipt": instance_receipt.serialize(),
                "projection": projection,
                "receipt": receipt.serialize(),
                "replay": replay,
                "replayVerified": replay["matched"],
            }
        )
        print(json.dumps(response, sort_keys=True))


if __name__ == "__main__":
    main()
