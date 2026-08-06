"""Support fixture for Pass 213 API/CLI parity tests.

The original full fixture is retained here as a non-discovered support module.
The discovered test module subclasses it and corrects only the exact OpenAPI
mutation-route assertion.
"""
from tests.test_pass213_api_cli_v1 import Pass213Iteration9APIAndCLIParityTests

__all__ = ["Pass213Iteration9APIAndCLIParityTests"]
