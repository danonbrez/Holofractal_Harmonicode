from hhs_runtime.core_sandbox.hash72_collision_engine_v1 import collision_search
from hhs_runtime.testing.state_generator_v1 import state_generator
from hhs_runtime.core_sandbox.hash72_encoder_v1 import encode_state
from hhs_runtime.core_sandbox.enforce_wrapper_v1 import enforce_kernel


def run():
    result = collision_search(state_generator, encode_state, enforce_kernel)
    print(result)


if __name__ == "__main__":
    run()
