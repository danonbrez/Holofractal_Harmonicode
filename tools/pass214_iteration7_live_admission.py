#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_iteration7_live_admission_ablation_v1 import (
    build_ablation_plan,
    create_live_admission,
    inspect_default_runtime,
    validate_recorded_admission,
)


def load_json(path: str | None):
    if path is None:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | None, payload):
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
    print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pass 214 Iteration 7 live Pass 213 admission bridge")
    parser.add_argument("--mode", choices=("inspect", "admit", "validate"), default="inspect")
    parser.add_argument("--trusted-anchor-json")
    parser.add_argument("--verifier-bundle-json")
    parser.add_argument("--trust-bundle")
    parser.add_argument("--admission-json")
    parser.add_argument("--nonce", default="pass214-iteration7-live-admission")
    parser.add_argument("--timestamp-ns", type=int)
    parser.add_argument("--output")
    parser.add_argument("--plan-output")
    args = parser.parse_args()

    if args.mode == "inspect":
        report = inspect_default_runtime(
            trusted_anchor_mapping=load_json(args.trusted_anchor_json),
            verifier_bundle_mapping=load_json(args.verifier_bundle_json),
            trust_bundle_path=args.trust_bundle,
        )
        write_json(args.output, report)
        return 0

    if args.mode == "validate":
        if not args.admission_json:
            parser.error("--admission-json is required for --mode validate")
        admission = validate_recorded_admission(load_json(args.admission_json))
        report = {
            "schema": "HHS_PASS_214_ITERATION_7_RECORDED_ADMISSION_VALIDATION_V1",
            "structurally_valid": True,
            "admission_root_hash216": admission["admission_root_hash216"],
            "live_recheck_required_before_execution": True,
            "migration_active": False,
            "authority_promoted": False,
            "pass215_authorized": False,
        }
        write_json(args.output, report)
        return 0

    if not (args.trusted_anchor_json and args.verifier_bundle_json and args.trust_bundle):
        parser.error("--mode admit requires --trusted-anchor-json, --verifier-bundle-json, and --trust-bundle")
    from hhs_backend.runtime.hhs_pass213_governed_surface_v2 import get_default_pass213_surface
    from hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1 import get_default_native_dispatch_service

    admission = create_live_admission(
        surface=get_default_pass213_surface(),
        dispatch_service=get_default_native_dispatch_service(),
        trusted_anchor_mapping=load_json(args.trusted_anchor_json),
        verifier_bundle_mapping=load_json(args.verifier_bundle_json),
        trust_bundle_path=args.trust_bundle,
        nonce=args.nonce,
        requested_timestamp_ns=args.timestamp_ns or time.time_ns(),
    )
    plan = build_ablation_plan(admission)
    write_json(args.output, admission)
    if args.plan_output:
        Path(args.plan_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.plan_output).write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
