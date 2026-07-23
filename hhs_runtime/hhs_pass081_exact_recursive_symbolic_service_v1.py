from pathlib import Path
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass079_native_opcode_registry_v1 import build_registry
from native_projects.hhs_vm81_native_exposure.hhs_pass080_constraint_membrane_v1 import canonical_membrane_state
from native_projects.hhs_exact_recursive_symbolic_runtime.hhs_pass081_runtime_v1 import execute, CALIBRATION_SOURCE

def run_pass081(payload):
    repo=Path(__file__).resolve().parents[1]
    state=canonical_membrane_state(payload.get('membrane_state'))
    binding=build_registry(repo)['entries'][0]
    req={'binding_root_hash72':binding['binding_root_hash72'],'authority_scope':binding['authority_scope'],'lease_status':payload.get('lease_status','ACTIVE_VALIDATED'),'vm81_lane_binding_status':'BOUND_WITNESSED','pre_state_root':product_root('hhs_vm81_pre_state_v1',stable(state)),'canonical_operand_commitment_status':'BOUND_WITNESSED','lease_boundary':payload.get('lease_boundary','SEQUENCE_1')}
    return execute(repo,payload.get('opcode',binding['native_opcode']),req,state,payload.get('source',CALIBRATION_SOURCE),max_iterations=int(payload.get('max_iterations',16)),substitutions=payload.get('substitutions',[]))
