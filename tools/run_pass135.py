from __future__ import annotations
import argparse
from pathlib import Path
from hhs_runtime.hhs_pass135_ceuac_audit_v1 import run_audit

p=argparse.ArgumentParser()
p.add_argument("subject_archive",type=Path)
p.add_argument("--output",type=Path,default=Path("release_artifacts/pass135"))
a=p.parse_args()
print(run_audit(a.subject_archive,a.output))
