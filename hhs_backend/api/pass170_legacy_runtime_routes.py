"""Pass170 I180 public federation entry for governed legacy runtime HTTP routes."""
from hhs_backend.pass170_legacy_runtime_routes import build_pass170_legacy_runtime_router

router = build_pass170_legacy_runtime_router()

__all__ = ["router"]
