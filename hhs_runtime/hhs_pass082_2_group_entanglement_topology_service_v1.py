from pathlib import Path
from native_projects.hhs_bifurcation_calibration.hhs_pass082_2_group_entanglement_topology_v1 import default_workload, run, verify_replay, workload_registry, build_artifacts

class Pass0822GroupEntanglementTopologyService:
    def __init__(self, repo: Path): self.repo=Path(repo)
    def run(self, workload): return run(self.repo, workload)
    def verify_replay(self, workload): return verify_replay(self.repo, workload)
    def registry(self): return workload_registry(self.repo)
    def build_artifacts(self): return build_artifacts(self.repo)
