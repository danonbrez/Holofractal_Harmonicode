from __future__ import annotations

import json
from pathlib import Path

from hhs_runtime.pass219.lane5_universal_abi_kernel_interceptor import (
    audit_runtime_kernel_crossings,
)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    report = audit_runtime_kernel_crossings(root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["production_acceptance"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
