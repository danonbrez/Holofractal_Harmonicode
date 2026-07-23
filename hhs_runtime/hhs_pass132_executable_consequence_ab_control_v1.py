"""Compatibility surface for the recovered Pass 132 consequence service.

Historical identity note: this is a functional reconstruction, not the
byte-identical unavailable original source committed in the 2026-07-18 release.
"""
from hhs_runtime.hhs_pass132_reconstructed_replay_v1 import (
    Pass132ReconstructedReplayService,
    get_pass132_reconstructed_service,
    pass132_reconstructed_self_test,
)


def execute_consequences(payload):
    return get_pass132_reconstructed_service().execute(payload)


def replay_consequences(payload):
    return get_pass132_reconstructed_service().replay(payload)


def compare_consequences(payload):
    return get_pass132_reconstructed_service().compare(payload)
