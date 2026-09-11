"""HARMONICODE symmetric unit-product projection rule v1.

A symmetric ordered matrix/tensor algebra surface may open a new scalar
projection layer at ``a²=xy=1`` when, and only when, the active projection
profile provides exact witnesses that:

1. the complete surface has a declared involutive symmetry map;
2. every declared symmetry orbit is covered exactly once;
3. every orbit product closes to the multiplicative unit 1 in the registered
   projection domain; and
4. any self-symmetric center/fixed-point cell also closes to 1 under its own
   typed rule.

The result is a projection layer, not a native identity. In particular the rule
does not assert native ``a² ≡ xy``, does not commute ``xy`` with ``yx``, and
does not reconstruct a matrix/tensor from scalar 1.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence

FORMAT = "HHS_SPI_SYMMETRIC_UNIT_PRODUCT_PROJECTION_RULE_V1"
VERSION = "1.0.0"
PROFILE = "SYMMETRIC-UNIT-PRODUCT-LAYER-v1"


class SPISymmetricUnitProductError(ValueError):
    pass


def _q(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise SPISymmetricUnitProductError("unit-product proof requires exact non-float values")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise SPISymmetricUnitProductError(f"invalid exact scalar: {value!r}") from exc


def _exact_json(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"type": "EXACT_RATIONAL", "numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, tuple):
        return [_exact_json(v) for v in value]
    if isinstance(value, list):
        return [_exact_json(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _exact_json(value[k]) for k in sorted(value)}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise SPISymmetricUnitProductError(f"unsupported receipt type: {type(value).__name__}")


def _stable_json(value: Any) -> str:
    return json.dumps(_exact_json(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def symmetric_unit_product_projection(
    *,
    surface_id: str,
    surface_source: str,
    symmetry_orbits: Sequence[Mapping[str, Any]],
    total_component_count: int,
    profile_id: str = PROFILE,
) -> Dict[str, Any]:
    """Emit an exact ``a²=xy=1`` projection-layer receipt.

    ``symmetry_orbits`` entries must contain:
      * ``orbit_id``: stable identifier;
      * ``members``: non-empty ordered component identifiers;
      * ``product``: exact projected orbit product;
      * ``involution_closed``: True when the declared symmetry maps the orbit
        back to itself.

    The sum of member counts must equal ``total_component_count``. Overlapping
    component identifiers are rejected, ensuring full one-time coverage.
    """
    if not surface_id or not surface_source or not profile_id:
        raise SPISymmetricUnitProductError("surface/profile identity is required")
    if not isinstance(total_component_count, int) or isinstance(total_component_count, bool) or total_component_count <= 0:
        raise SPISymmetricUnitProductError("total_component_count must be a positive integer")
    if not symmetry_orbits:
        raise SPISymmetricUnitProductError("at least one symmetry orbit is required")

    normalized = []
    seen_members = set()
    covered = 0
    for orbit in symmetry_orbits:
        orbit_id = str(orbit.get("orbit_id", ""))
        members = tuple(str(v) for v in orbit.get("members", ()))
        if not orbit_id or not members:
            raise SPISymmetricUnitProductError("every symmetry orbit needs an id and members")
        if orbit.get("involution_closed") is not True:
            raise SPISymmetricUnitProductError(f"symmetry orbit {orbit_id} is not involution-closed")
        for member in members:
            if member in seen_members:
                raise SPISymmetricUnitProductError(f"surface component repeated across symmetry orbits: {member}")
            seen_members.add(member)
        covered += len(members)
        product = _q(orbit.get("product"))
        if product != 1:
            raise SPISymmetricUnitProductError(f"symmetry orbit {orbit_id} product is not unit: {product}")
        normalized.append({
            "orbit_id": orbit_id,
            "members": members,
            "product": product,
            "involution_closed": True,
            "unit_closed": True,
        })

    if covered != total_component_count:
        raise SPISymmetricUnitProductError(
            f"surface coverage mismatch: covered {covered}, expected {total_component_count}"
        )

    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_SYMMETRIC_UNIT_PRODUCT_PROJECTION_RECEIPT_V1",
        "format": FORMAT,
        "version": VERSION,
        "profile": profile_id,
        "surface_id": surface_id,
        "surface_source": surface_source,
        "surface_source_sha256": sha256(surface_source.encode("utf-8")).hexdigest(),
        "total_component_count": total_component_count,
        "covered_component_count": covered,
        "symmetry_orbit_count": len(normalized),
        "symmetry_orbits": normalized,
        "symmetry_complete": True,
        "all_orbit_products_unit": True,
        "projection_layer": {
            "a²": Fraction(1),
            "xy": Fraction(1),
            "relation": "a²=xy=1",
            "relation_kind": "SCALAR_PROJECTION_LAYER_ONLY",
        },
        "premises": [
            "registered primitive projection pi(a²)=1",
            "registered Pass129 rational membrane permits pi(xy)=1 in the unit-closure profile",
            "complete declared surface symmetry is witnessed exactly",
            "every symmetry-orbit product is exactly 1",
        ],
        "lost_information": [
            "native matrix/tensor topology is not reconstructible from the unit scalar layer",
            "native ordered xy/yx identity is not collapsed",
            "surface-specific symmetry/orbit provenance must remain attached",
        ],
        "reverse_lift_status": "none",
        "projection_only": True,
        "native_a2_xy_identity_authorized": False,
        "xy_yx_commutation_authorized": False,
        "canonical_admission_authority": False,
        "vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()
    return _exact_json(receipt)
