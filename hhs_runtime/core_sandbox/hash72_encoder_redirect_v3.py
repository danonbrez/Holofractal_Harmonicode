# Redirect all legacy encoder calls to locked kernel path

from hhs_runtime.core_sandbox.hash72_encoder_locked_v2 import encode_state as _locked_encode


def encode_state(*args, **kwargs):
    return _locked_encode(*args, **kwargs)
