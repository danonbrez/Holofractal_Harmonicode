"""Repository test hooks for bounded cross-surface validation."""
from __future__ import annotations

import os
import sys


def pytest_sessionstart(session) -> None:
    """Run I16/I17 terminal proofs only inside the established I10 real-etcd root gate."""
    endpoint = os.environ.get("HHS_PASS218_I10_ETCD_TEST_ENDPOINT", "").strip()
    production_root_requested = any(
        str(argument).endswith("tests/test_runtime_os_production_root.py")
        for argument in sys.argv[1:]
    )
    if not endpoint or not production_root_requested:
        return

    from scripts.pass218_iteration16_consumption_validation import main as validate_i16_failover
    from scripts.pass218_iteration16_real_etcd_validation import main as validate_i16_real_etcd
    from scripts.pass218_iteration17_execution_validation import main as validate_i17_failover
    from scripts.pass218_iteration17_real_etcd_validation import main as validate_i17_real_etcd

    if validate_i16_failover() != 0:
        raise RuntimeError("P218_I16_TERMINAL_VALIDATOR_FAILED")
    if validate_i16_real_etcd() != 0:
        raise RuntimeError("P218_I16_REAL_ETCD_VALIDATOR_FAILED")
    if validate_i17_failover() != 0:
        raise RuntimeError("P218_I17_TERMINAL_VALIDATOR_FAILED")
    if validate_i17_real_etcd() != 0:
        raise RuntimeError("P218_I17_REAL_ETCD_VALIDATOR_FAILED")
