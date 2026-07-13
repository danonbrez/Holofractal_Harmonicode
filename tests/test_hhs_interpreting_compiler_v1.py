from hhs_backend.runtime.hhs_interpreting_compiler_v1 import interpreting_compiler_self_test
from hhs_backend.runtime.hhs_compiler_ir_v1 import compiler_ir_self_test

def test_interpreting_compiler_self_test():
    result = interpreting_compiler_self_test()
    assert result["ok"]
    assert not result["result"]["execution_authorized"]
    assert not result["unsupported_target_rejection"]["ok"]

def test_compiler_ir_self_test():
    result = compiler_ir_self_test()
    assert result["ok"]
    assert result["artifact"]["target"] == "HHS_IR"
