"""HHS API package initialization.

Pass 201 loads the production public API federation projection before route
modules are composed. This preserves legacy V1 import paths while applying
canonical OpenAPI path-converter normalization.
"""
from hhs_backend.runtime import hhs_pass201_public_api_federation as _pass201_public_api_federation

__all__ = ["_pass201_public_api_federation"]
