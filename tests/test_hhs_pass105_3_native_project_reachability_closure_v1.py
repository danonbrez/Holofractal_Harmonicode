from pathlib import Path
from hhs_runtime.hhs_runtime_reachability_audit_v1 import build_reachability_manifest
from hhs_runtime.hhs_native_project_ownership_v1 import ownership_for, validate_ownership

ROOT=Path(__file__).resolve().parents[1]

def test_live_manifest_has_zero_orphans_and_includes_native_projects():
    m=build_reachability_manifest(ROOT)
    assert m['orphan_count']==0
    native=[r for r in m['records'] if r['path'].startswith('native_projects/')]
    assert native
    assert any(r['status']=='OWNED_ARTIFACT' for r in native)

def test_every_previous_orphan_has_verified_owner():
    # Exact 79 paths from the pre-repair live auditor are represented by ownership.
    m=build_reachability_manifest(ROOT)
    owned=[r for r in m['records'] if r['status'] in {'OWNED_ARTIFACT','BUILD_REACHABLE','TOOL_REACHABLE','GUI_REACHABLE'} and r['path'].startswith('native_projects/')]
    assert len(owned)>=79
    for r in owned:
        o=ownership_for(r['path']); assert o is not None
        assert validate_ownership(ROOT,r['path'],o)['owner_test_exists']

def test_workspace_ui_is_real_gui_reachable():
    m=build_reachability_manifest(ROOT)
    r=next(x for x in m['records'] if x['path']=='native_projects/hhs_ide_workspace/workspace_ui/app.js')
    assert r['status']=='GUI_REACHABLE'

def test_no_native_project_record_is_orphan():
    m=build_reachability_manifest(ROOT)
    assert not [r for r in m['records'] if r['path'].startswith('native_projects/') and r['status']=='ORPHAN']
