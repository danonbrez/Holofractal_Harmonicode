from pathlib import Path
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import default_workload, run, verify_replay


def run_pass082_1_offset_entangled_calibration(payload):
    repo = Path(__file__).resolve().parents[1]
    workload = payload.get("workload") or default_workload(
        repo,
        int(payload.get("branch_count", 2)),
        payload.get("allocation", "CONSECUTIVE"),
        combined=bool(payload.get("combined", False)),
        stride=int(payload.get("stride", 5)),
    )
    return verify_replay(repo, workload) if payload.get("verify_replay", True) else run(repo, workload)
