"""Pass 215 Iteration 19 canonical component-order hardening.

The compact payload is serialized with JSON sort_keys=True.  Use the same sorted
component-name order before extraction so reconstruction never depends on source
mapping insertion order.  This does not change any Iteration-18 state content.
"""
from __future__ import annotations

from hhs_backend.runtime import hhs_pass215_iteration19_content_addressed_checkpoint_v1 as v1

v1.LARGE_COMPONENT_NAMES = tuple(sorted(v1.LARGE_COMPONENT_NAMES))

from hhs_backend.runtime.hhs_pass215_iteration19_content_addressed_checkpoint_v1 import *  # noqa: F401,F403,E402

execute_content_addressed_checkpoint_benchmark = v1.execute_content_addressed_checkpoint_benchmark
execute_content_addressed_checkpoint_benchmark_from_path = v1.execute_content_addressed_checkpoint_benchmark_from_path
validate_content_addressed_checkpoint_evidence = v1.validate_content_addressed_checkpoint_evidence
compare_content_addressed_checkpoint_replays = v1.compare_content_addressed_checkpoint_replays
compact_iteration18_checkpoint = v1.compact_iteration18_checkpoint
reconstruct_iteration18_checkpoint = v1.reconstruct_iteration18_checkpoint
restore_compacted_generation_session = v1.restore_compacted_generation_session
