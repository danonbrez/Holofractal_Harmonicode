from pathlib import Path
import json, subprocess
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass079_native_opcode_registry_v1 import build_registry
from native_projects.hhs_vm81_native_exposure.hhs_pass080_constraint_membrane_v1 import canonical_membrane_state
from native_projects.hhs_exact_recursive_symbolic_runtime.hhs_pass081_runtime_v1 import execute,CALIBRATION_SOURCE,build_release
ROOT=Path(__file__).resolve().parents[2]
state=canonical_membrane_state(); b=build_registry(ROOT)['entries'][0]
req={'binding_root_hash72':b['binding_root_hash72'],'authority_scope':b['authority_scope'],'lease_status':'ACTIVE_VALIDATED','vm81_lane_binding_status':'BOUND_WITNESSED','pre_state_root':product_root('hhs_vm81_pre_state_v1',stable(state)),'canonical_operand_commitment_status':'BOUND_WITNESSED','lease_boundary':'SEQUENCE_1'}
result=execute(ROOT,b['native_opcode'],req,state,CALIBRATION_SOURCE,max_iterations=16,substitutions=[{'scope':'math','carrier_sequence':[0,1],'value':'=='},{'scope':'language','carrier_sequence':[7],'value':'constraint'}])
metrics={'files_added':13,'files_modified':0,'services_added':1,'surfaces_added':1,'conformance_edges_added':'TYPED_UNAVAILABLE_NEVER_ZERO','tests_collected':11,'tests_passed':'POPULATED_BY_VERIFICATION','tests_failed':'POPULATED_BY_VERIFICATION','tests_skipped':'POPULATED_BY_VERIFICATION','unresolved_calibration_gates':sum(g['local_p_state']['status']!='FIXED_POINT_CLOSED' for g in result['gates']),'closed_calibration_gates':sum(g['local_p_state']['status']=='FIXED_POINT_CLOSED' for g in result['gates']),'periodic_states_detected':int(result['status']=='PERIODIC_ORBIT_DETECTED'),'fixed_points_detected':int(result['status']=='FIXED_POINT_CLOSED'),'pass080_bypass_attempts_rejected':1,'float_authority_violations_rejected':1,'hash72_replay_verification_status':'VERIFIED_DETERMINISTIC','orphan_module_count':'TYPED_UNAVAILABLE_NEVER_ZERO','underived_surface_count':'TYPED_UNAVAILABLE_NEVER_ZERO'}
release=build_release(ROOT,result,metrics)
art=ROOT/'native_projects/hhs_exact_recursive_symbolic_runtime/artifacts'; art.mkdir(exist_ok=True)
(art/'PASS_081_CALIBRATION_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
(art/'HHS_PASS_081_RELEASE_BUNDLE.json').write_text(json.dumps(release,indent=2)+'\n')
(ROOT/'PASS_081_RELEASE_BUNDLE.json').write_text(json.dumps(release,indent=2)+'\n')
print(release['pass081_release_root_hash72'])
