"""Recovered IEEE control projection over immutable Pass 132 execution records."""
from hhs_runtime.hhs_pass132_reconstructed_replay_v1 import get_pass132_reconstructed_service


def ieee_control_for_workload(workload_id: str):
    return get_pass132_reconstructed_service().foreign_model({"workload_id": workload_id})
