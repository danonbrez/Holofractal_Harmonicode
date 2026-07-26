"""Runtime entry point for the immutable agent SQL evidence index."""
from ._immutable_agent_source_capsule_v1 import execute as _execute
_execute("hhs_backend/runtime/immutable_agent_sql_index_v1.py", globals())
del _execute
