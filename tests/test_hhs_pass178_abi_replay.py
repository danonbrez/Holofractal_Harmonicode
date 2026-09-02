from hhs_runtime.pass163.vmrc import VMRCRuntime
from hhs_runtime.pass178.runtime import PhysicsAuthority
from hhs_runtime.pass178.templates import relativistic_lab_template

def test_vm81_admission_and_replay_chain():
    t=relativistic_lab_template();vm=VMRCRuntime();rt=PhysicsAuthority(vm81=vm)
    rt.ingest_source("s",t["source"].encode());rt.register_model(model_id="m",model_kind=t["model_kind"],source_id="s",parameters={})
    before=vm.epoch;initial=rt.admit_initial_state("m",t["initial_state"]);assert vm.epoch==before+1
    c=rt.step_candidate("m");assert c["authoritative_clock_advanced"] is False
    step=rt.commit_step("m",c);assert vm.epoch==before+2
    assert len(step["post_vm81_hash72_evidence"])==72 and len(step["state_hash216"])==216
    assert rt.replay("m")["deterministic_replay_chain"] is True

def test_missing_vm81_fails_closed():
    t=relativistic_lab_template();rt=PhysicsAuthority(vm81=None)
    rt.ingest_source("s",t["source"].encode());rt.register_model(model_id="m",model_kind=t["model_kind"],source_id="s",parameters={})
    try: rt.admit_initial_state("m",t["initial_state"])
    except Exception as e: assert "VM81_ADMISSION_AUTHORITY_REQUIRED" in str(e)
    else: raise AssertionError("missing VM81 accepted")
