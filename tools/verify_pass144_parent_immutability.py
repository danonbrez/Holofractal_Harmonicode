#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "reports/pass_144/PASS_143_PARENT_IMMUTABILITY_BASELINE.json"
ALLOWED_PREFIXES = (
    "docs/pass_144/", "whitepapers/pass_144/", "formal/lemmas/pass_144/",
    "reports/pass_144/", "tools/verify_pass144_parent_immutability.py",
    "tests/test_pass144_documentation_immutability.py", "PASS_144_RELEASE_MANIFEST.json"
)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    baseline = json.loads(BASELINE.read_text())
    errors=[]
    inherited={x['path']:x for x in baseline['files']}
    for rel, rec in inherited.items():
        p=ROOT/rel
        if not p.is_file(): errors.append(f"missing inherited file: {rel}"); continue
        if p.stat().st_size != rec['size']: errors.append(f"size changed: {rel}")
        if sha256(p) != rec['sha256']: errors.append(f"hash changed: {rel}")
    def transient(rel: str) -> bool:
        parts = rel.split('/')
        return '.pytest_cache' in parts or '__pycache__' in parts or rel.endswith('.pyc')
    current={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not transient(p.relative_to(ROOT).as_posix())}
    additions=sorted(current-set(inherited))
    for rel in additions:
        if not any(rel == pref or rel.startswith(pref) for pref in ALLOWED_PREFIXES):
            errors.append(f"non-documentation addition outside allowlist: {rel}")
    report={
        'schema':'HHS_PASS_144_PARENT_IMMUTABILITY_REPORT_V1',
        'parent_pass':143,
        'inherited_file_count':len(inherited),
        'addition_count':len(additions),
        'additions':additions,
        'status':'VERIFIED_IMMUTABLE' if not errors else 'FAILED',
        'errors':errors,
    }
    out=ROOT/'reports/pass_144/PASS_144_PARENT_IMMUTABILITY_REPORT.json'
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
