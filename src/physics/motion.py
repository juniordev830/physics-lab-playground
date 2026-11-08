"""Deterministic Newtonian motion and conservation diagnostics for 2D bodies."""
from dataclasses import dataclass
from math import exp, isfinite
from collections.abc import Sequence

from .vector2 import Vector2


@dataclass(frozen=True)
class Body2D:
    position: Vector2
    velocity: Vector2
    mass: float

    def __post_init__(self) -> None:
        if not isinstance(self.position, Vector2) or not isinstance(self.velocity, Vector2):
            raise ValueError("Position and velocity must be finite Vector2 values")
        if not isfinite(self.mass) or self.mass <= 0:
            raise ValueError("Mass must be positive and finite")

    def momentum(self) -> Vector2:
        return self.velocity * self.mass

    def kinetic_energy(self) -> float:
        return 0.5 * self.mass * self.velocity.magnitude_squared()


def _validate_step(force: Vector2, dt: float) -> None:
    if not isinstance(force, Vector2):
        raise ValueError("Force must be a Vector2")
    if not isfinite(dt) or dt < 0:
        raise ValueError("Time step must be nonnegative and finite")


def step(body: Body2D, force: Vector2, dt: float) -> Body2D:
    """Semi-implicit Euler step: velocity first, then position."""
    _validate_step(force, dt)
    acceleration = force / body.mass
    velocity = body.velocity + acceleration * dt
    position = body.position + velocity * dt
    return Body2D(position=position, velocity=velocity, mass=body.mass)


def step_with_drag(body: Body2D, force: Vector2, dt: float, drag: float) -> Body2D:
    """Approximate linear drag with exponential velocity decay per step."""
    _validate_step(force, dt)
    if not isfinite(drag) or drag < 0:
        raise ValueError("Drag coefficient must be nonnegative and finite")
    if dt == 0:
        return body
    velocity = (body.velocity + force / body.mass * dt) * exp(-drag * dt)
    return Body2D(body.position + velocity * dt, velocity, body.mass)


def step_many(bodies: Sequence[Body2D], forces: Sequence[Vector2], dt: float) -> list[Body2D]:
    """Advance every body with its corresponding force, without mutation."""
    if len(bodies) != len(forces):
        raise ValueError("Each body must have exactly one force")
    if len(bodies) > 10000:
        raise ValueError("Too many bodies for one integration step")
    return [step(body, force, dt) for body, force in zip(bodies, forces)]


def total_momentum(bodies: Sequence[Body2D]) -> Vector2:
    result = Vector2(0.0, 0.0)
    for body in bodies:
        result = result + body.momentum()
    return result


def total_kinetic_energy(bodies: Sequence[Body2D]) -> float:
    return sum(body.kinetic_energy() for body in bodies)


def center_of_mass(bodies: Sequence[Body2D]) -> Vector2:
    if not bodies:
        raise ValueError("Center of mass requires at least one body")
    total_mass = sum(body.mass for body in bodies)
    weighted = Vector2(0.0, 0.0)
    for body in bodies:
        weighted = weighted + body.position * body.mass
    return weighted / total_mass
