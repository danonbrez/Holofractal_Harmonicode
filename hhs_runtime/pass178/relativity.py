from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .exact import AlgebraicRoot, ExactPhysicsError, ExactRational, rational_vector


@dataclass(frozen=True)
class RelativisticParticle:
    particle_id: str
    mass: ExactRational
    charge: ExactRational
    position4: tuple[ExactRational, ExactRational, ExactRational, ExactRational]
    four_velocity: tuple[ExactRational, ExactRational, ExactRational, ExactRational]
    proper_step: ExactRational

    def __post_init__(self) -> None:
        if not self.particle_id:
            raise ExactPhysicsError("P178_RELATIVITY_PARTICLE_ID")
        if self.mass.num <= 0:
            raise ExactPhysicsError("P178_RELATIVITY_MASS_POSITIVE_REQUIRED")
        if self.proper_step.num <= 0:
            raise ExactPhysicsError("P178_RELATIVITY_PROPER_STEP_POSITIVE_REQUIRED")
        if len(self.position4) != 4 or len(self.four_velocity) != 4:
            raise ExactPhysicsError("P178_RELATIVITY_FOUR_VECTOR_ARITY")
        if minkowski_norm2(self.four_velocity) != ExactRational(1):
            raise ExactPhysicsError("P178_RELATIVITY_FOUR_VELOCITY_NOT_TIMELIKE_UNIT")

    def payload(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_178_RELATIVISTIC_PARTICLE_V1",
            "particle_id": self.particle_id,
            "mass": self.mass.as_pair(),
            "charge": self.charge.as_pair(),
            "position4": [v.as_pair() for v in self.position4],
            "four_velocity": [v.as_pair() for v in self.four_velocity],
            "proper_step": self.proper_step.as_pair(),
            "metric": "+---",
            "c_units": "DIMENSIONLESS_C_EQ_1_PROFILE",
        }


def minkowski_norm2(vector4: Iterable[ExactRational]) -> ExactRational:
    v = tuple(vector4)
    if len(v) != 4:
        raise ExactPhysicsError("P178_RELATIVITY_FOUR_VECTOR_ARITY")
    return v[0] * v[0] - v[1] * v[1] - v[2] * v[2] - v[3] * v[3]


def relativistic_free_step(particle: RelativisticParticle) -> RelativisticParticle:
    dtau = particle.proper_step
    next_position = tuple(
        x + u * dtau for x, u in zip(particle.position4, particle.four_velocity)
    )
    return RelativisticParticle(
        particle_id=particle.particle_id,
        mass=particle.mass,
        charge=particle.charge,
        position4=next_position,  # type: ignore[arg-type]
        four_velocity=particle.four_velocity,
        proper_step=particle.proper_step,
    )


def momentum_mass_shell(
    mass: Any,
    momentum3: Iterable[Any],
) -> dict[str, Any]:
    m = ExactRational.coerce(mass)
    if m.num <= 0:
        raise ExactPhysicsError("P178_RELATIVITY_MASS_POSITIVE_REQUIRED")
    p = rational_vector(momentum3)
    if len(p) != 3:
        raise ExactPhysicsError("P178_RELATIVITY_MOMENTUM3_ARITY")
    p2 = sum((x * x for x in p), ExactRational(0))
    energy2 = m * m + p2
    return {
        "schema": "HHS_PASS_178_MASS_SHELL_WITNESS_V1",
        "mass": m.as_pair(),
        "momentum3": [x.as_pair() for x in p],
        "energy_squared": energy2.as_pair(),
        "energy": AlgebraicRoot(energy2, 2, "POSITIVE_REAL").payload(),
        "equation": "E^2-p^2=m^2",
        "classification": "STANDARD_PHYSICS_EQUATION",
        "admitted_branch": "POSITIVE_ENERGY",
    }


def uniform_electric_momentum_candidate(
    momentum3: Iterable[Any],
    charge: Any,
    electric_field3: Iterable[Any],
    coordinate_step: Any,
) -> dict[str, Any]:
    p = rational_vector(momentum3)
    e = rational_vector(electric_field3)
    if len(p) != 3 or len(e) != 3:
        raise ExactPhysicsError("P178_RELATIVITY_VECTOR3_ARITY")
    q = ExactRational.coerce(charge)
    dt = ExactRational.coerce(coordinate_step)
    if dt.num <= 0:
        raise ExactPhysicsError("P178_RELATIVITY_COORDINATE_STEP_POSITIVE_REQUIRED")
    next_p = tuple(px + q * ex * dt for px, ex in zip(p, e))
    return {
        "schema": "HHS_PASS_178_UNIFORM_ELECTRIC_MOMENTUM_CANDIDATE_V1",
        "prior_momentum3": [x.as_pair() for x in p],
        "electric_field3": [x.as_pair() for x in e],
        "charge": q.as_pair(),
        "coordinate_step": dt.as_pair(),
        "next_momentum3": [x.as_pair() for x in next_p],
        "equation": "dp/dt=qE",
        "classification": "STANDARD_PHYSICS_EQUATION",
        "vm81_admitted": False,
    }
