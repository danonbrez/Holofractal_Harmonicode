"""Validation entry point for the immutable agent SQL index."""
from hhs_backend.runtime._immutable_agent_source_capsule_v1 import execute as _execute
_execute("tests/test_hhs_immutable_agent_sql_index_v1.py", globals())
del _execute
