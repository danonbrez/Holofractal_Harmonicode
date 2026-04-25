"""
Core Sandbox Physics Model V1
=============================

Minimal deterministic physical adapter:
observation → symbolic constraints → state patch.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PhysicalObservation:
    sensor_id: str
    value: float
    timestamp: float


def map_observation_to_symbolic(obs: PhysicalObservation) -> Dict[str, Any]:
    return {
        "sensor": obs.sensor_id,
        "value": obs.value,
        "constraint": "a^2 = normalized_value",
        "normalized": abs(obs.value)
    }


def build_state_patch(symbolic: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "op": "SET",
        "path": f"sensors.{symbolic['sensor']}",
        "value": symbolic
    }
