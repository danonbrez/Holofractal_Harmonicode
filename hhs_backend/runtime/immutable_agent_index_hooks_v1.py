"""Runtime entry point for immutable agent-index cognition hooks."""
from ._immutable_agent_source_capsule_v1 import execute as _execute
_execute("hhs_backend/runtime/immutable_agent_index_hooks_v1.py", globals())
del _execute
