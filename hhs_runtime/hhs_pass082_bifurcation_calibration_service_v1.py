from pathlib import Path
from native_projects.hhs_bifurcation_calibration.hhs_pass082_bifurcation_benchmark_v1 import default_workload, run, verify_replay

def run_pass082_bifurcation(payload):
    repo=Path(__file__).resolve().parents[1]
    workload=payload.get('workload') or default_workload(repo,int(payload.get('branch_count',2)),int(payload.get('ast_nodes',16)))
    return verify_replay(repo,workload) if payload.get('verify_replay',True) else run(repo,workload)
