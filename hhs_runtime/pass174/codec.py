from __future__ import annotations

import base64
from fractions import Fraction
from typing import Any


def denormalize(value: Any) -> Any:
    """Reverse Pass 174 canonical tagged values after authenticated decoding."""
    if isinstance(value, list):
        return [denormalize(item) for item in value]
    if not isinstance(value, dict):
        return value
    value_type = value.get("type")
    if value_type == "integer" and set(value) == {"type", "value"}:
        return int(value["value"])
    if value_type == "boolean" and set(value) == {"type", "value"}:
        return bool(value["value"])
    if value_type == "rational" and set(value) == {"type", "numerator", "denominator"}:
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    if value_type == "bytes" and set(value) == {"type", "base64"}:
        return base64.b64decode(value["base64"], validate=True)
    return {str(key): denormalize(item) for key, item in value.items()}
