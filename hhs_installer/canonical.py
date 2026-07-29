from __future__ import annotations

from dataclasses import asdict, is_dataclass
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping
import json

from python.hhs_gfcc.core import inherited_hash72, inherited_hash216

INSTALLATION_IDENTITY_DOMAIN = "HHS-P172-INSTALLATION-IDENTITY-V1"
INSTALLATION_RECEIPT_DOMAIN = "HHS-P172-INSTALLATION-RECEIPT-V1"


class CanonicalizationError(ValueError):
    pass


def stable(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    elif is_dataclass(value):
        value = asdict(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Decimal):
        return {"decimal": format(value, "f")}
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, Mapping):
        return {str(key): stable(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [stable(item) for item in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, float):
        raise CanonicalizationError("P172_FLOAT_FORBIDDEN_IN_CANONICAL_IDENTITY")
    raise CanonicalizationError(f"P172_UNSUPPORTED_CANONICAL_TYPE:{type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        stable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def hash216(value: Any, *, domain: str = INSTALLATION_IDENTITY_DOMAIN) -> str:
    return inherited_hash216(canonical_bytes({"domain": domain, "value": stable(value)}))


def hash72(value: Any, *, domain: str = INSTALLATION_RECEIPT_DOMAIN) -> str:
    return inherited_hash72(canonical_bytes({"domain": domain, "value": stable(value)}))


def installation_identity(components: Mapping[str, Any]) -> str:
    required = {"contract", "source", "profile", "platform", "architecture", "dependencies", "native", "frontend", "provider", "model", "evidence"}
    missing = sorted(required - set(components))
    if missing:
        raise CanonicalizationError(f"P172_INSTALLATION_IDENTITY_COMPONENTS_MISSING:{','.join(missing)}")
    return hash216({key: components[key] for key in sorted(required)}, domain=INSTALLATION_IDENTITY_DOMAIN)
