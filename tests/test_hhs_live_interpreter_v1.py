from hhs_backend.runtime.hhs_live_interpreter_v1 import live_interpreter_self_test

def test_live_interpreter_self_test():
    result = live_interpreter_self_test()
    assert result["ok"]
    assert result["result"]["exact_symbolic_value"] == {"numerator": 5, "denominator": 2}
    assert not result["host_eval_rejection"]["ok"]
