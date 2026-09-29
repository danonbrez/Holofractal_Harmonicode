"""Framework-free Harmonicode runtime-expression execution service.

This module is the computation surface shared by runtime services and HTTP
adapters. It intentionally imports no FastAPI, Starlette, Pydantic, Uvicorn, or
other web/application framework so guarded internal services can execute through
the HHS runtime without acquiring an external application dependency.
"""
from __future__ import annotations

from typing import Any, Dict

from hhs_runtime.harmonicode_constraint_solver_v1 import interpret_and_solve


async def execute_runtime_expression(expression: str) -> Dict[str, Any]:
    """Execute source through the inherited Harmonicode interpreter and solver."""
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("expression must be a non-empty Harmonicode source string")
    result = interpret_and_solve(expression)
    solver = result.get("solver", {})
    receipt = solver.get("receipt", {})
    return {
        "expression": expression,
        "status": receipt.get("status", "UNKNOWN"),
        "result": result,
        "transport": "harmonicode_interpreter_solver",
        "execution_performed": True,
        "full_receipt_hash72": result["full_receipt_hash72"],
    }


__all__ = ["execute_runtime_expression"]
