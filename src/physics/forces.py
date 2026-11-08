"""Composable forces for the deterministic 2D physics laboratory.

All functions return new values and never mutate input bodies. Pairwise
interactions obey Newton's third law by adding equal and opposite forces.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite, sqrt

from .motion import Body2D
from .vector2 import Vector2


def _nonnegative(value: float, label: str) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError(f"{label} must be finite and nonnegative")


@dataclass(frozen=True)
class UniformField:
    """Uniform acceleration plus linear resistance (force = -drag * velocity)."""

    acceleration: Vector2
    linear_drag: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.acceleration, Vector2):
            raise ValueError("Acceleration must be a Vector2")
        _nonnegative(self.linear_drag, "Linear drag")

    def force_on(self, body: Body2D) -> Vector2:
        if not isinstance(body, Body2D):
            raise ValueError("Field requires a Body2D")
        return self.acceleration * body.mass - body.velocity * self.linear_drag

    def potential_energy(self, body: Body2D) -> float:
        """Conservative potential of the uniform acceleration only."""
        if not isinstance(body, Body2D):
            raise ValueError("Field requires a Body2D")
        return -body.mass * self.acceleration.dot(body.position)


@dataclass(frozen=True)
class SpringLink:
    """Zero-based indices of bodies joined by a damped radial Hooke spring."""

    first: int
    second: int
    stiffness: float
    rest_length: float
    damping: float = 0.0

    def __post_init__(self) -> None:
        if type(self.first) is not int or type(self.second) is not int:
            raise ValueError("Spring indices must be integers")
        if self.first < 0 or self.second < 0 or self.first == self.second:
            raise ValueError("Spring must connect two distinct nonnegative indices")
        _nonnegative(self.stiffness, "Stiffness")
        _nonnegative(self.rest_length, "Rest length")
        _nonnegative(self.damping, "Damping")


def spring_pair_force(
    first: Body2D, second: Body2D, stiffness: float,
    rest_length: float, damping: float = 0.0,
) -> Vector2:
    """Force on first body; apply its negative to second body.

    A coincident pair uses relative velocity as a normal, or the +X axis
    if both are stationary. This makes the singular case deterministic.
    """
    _nonnegative(stiffness, "Stiffness")
    _nonnegative(rest_length, "Rest length")
    _nonnegative(damping, "Damping")
    delta = second.position - first.position
    distance = delta.magnitude()
    if distance:
        normal = delta / distance
    else:
        relative = second.velocity - first.velocity
        normal = relative.normalized() if relative.magnitude() else Vector2(1, 0)
    radial_speed = (second.velocity - first.velocity).dot(normal)
    return normal * (stiffness * (distance - rest_length) + damping * radial_speed)


def spring_potential_energy(
    first: Body2D, second: Body2D, stiffness: float, rest_length: float,
) -> float:
    _nonnegative(stiffness, "Stiffness")
    _nonnegative(rest_length, "Rest length")
    extension = first.position.distance_to(second.position) - rest_length
    return 0.5 * stiffness * extension * extension


def gravitational_pair_force(
    first: Body2D, second: Body2D, constant: float, softening: float = 0.0,
) -> Vector2:
    """Attractive inverse-square force with Plummer softening.

    Returns zero at coincident centers. Softening is a distance, not
    squared distance; the denominator is (r^2 + softening^2)^(3/2).
    """
    _nonnegative(constant, "Gravitational constant")
    _nonnegative(softening, "Softening")
    if constant == 0:
        return Vector2(0, 0)
    delta = second.position - first.position
    distance_squared = delta.magnitude_squared() + softening * softening
    if distance_squared == 0:
        return Vector2(0, 0)
    scale = constant * first.mass * second.mass / (
        distance_squared * sqrt(distance_squared)
    )
    return delta * scale


def gravitational_potential_energy(
    first: Body2D, second: Body2D, constant: float, softening: float = 0.0,
) -> float:
    _nonnegative(constant, "Gravitational constant")
    _nonnegative(softening, "Softening")
    distance = sqrt(
        (second.position - first.position).magnitude_squared()
        + softening * softening
    )
    if distance == 0:
        if constant == 0:
            return 0.0
        raise ValueError("Unsoftened potential is undefined at coincident centers")
    return -constant * first.mass * second.mass / distance


def _validate_bodies(bodies: Sequence[Body2D]) -> None:
    if len(bodies) > 512:
        raise ValueError("Pairwise forces are limited to 512 bodies")
    if any(not isinstance(body, Body2D) for body in bodies):
        raise ValueError("All bodies must be Body2D instances")


def _validate_links(links: Sequence[SpringLink], count: int) -> None:
    if len(links) > 4096:
        raise ValueError("Too many spring links")
    for link in links:
        if not isinstance(link, SpringLink):
            raise ValueError("Spring links must be SpringLink instances")
        if link.first >= count or link.second >= count:
            raise ValueError("Spring index is outside the body list")


def net_forces(
    bodies: Sequence[Body2D], *,
    field: UniformField | None = None,
    springs: Sequence[SpringLink] = (),
    gravitational_constant: float = 0.0,
    softening: float = 0.0,
    external: Sequence[Vector2] | None = None,
) -> list[Vector2]:
    """Sum independent forces with no changes to the original bodies."""
    _validate_bodies(bodies)
    _validate_links(springs, len(bodies))
    _nonnegative(gravitational_constant, "Gravitational constant")
    _nonnegative(softening, "Softening")
    if field is not None and not isinstance(field, UniformField):
        raise ValueError("Field must be a UniformField")
    if external is not None:
        if len(external) != len(bodies):
            raise ValueError("External forces must match body count")
        if any(not isinstance(force, Vector2) for force in external):
            raise ValueError("External forces must be Vector2 instances")
    result = [
        (field.force_on(body) if field else Vector2(0, 0))
        + (external[index] if external is not None else Vector2(0, 0))
        for index, body in enumerate(bodies)
    ]
    for link in springs:
        force = spring_pair_force(
            bodies[link.first], bodies[link.second],
            link.stiffness, link.rest_length, link.damping,
        )
        result[link.first] = result[link.first] + force
        result[link.second] = result[link.second] - force
    if gravitational_constant:
        for first in range(len(bodies)):
            for second in range(first + 1, len(bodies)):
                force = gravitational_pair_force(
                    bodies[first], bodies[second],
                    gravitational_constant, softening,
                )
                result[first] = result[first] + force
                result[second] = result[second] - force
    return result


def total_potential_energy(
    bodies: Sequence[Body2D], *,
    field: UniformField | None = None,
    springs: Sequence[SpringLink] = (),
    gravitational_constant: float = 0.0,
    softening: float = 0.0,
) -> float:
    """Potential energy from conservative fields, springs and gravity.

    Dissipative spring damping and linear drag have no potential energy.
    """
    _validate_bodies(bodies)
    _validate_links(springs, len(bodies))
    _nonnegative(gravitational_constant, "Gravitational constant")
    _nonnegative(softening, "Softening")
    if field is not None and not isinstance(field, UniformField):
        raise ValueError("Field must be a UniformField")
    energy = sum(field.potential_energy(b) for b in bodies) if field else 0.0
    for link in springs:
        energy += spring_potential_energy(
            bodies[link.first], bodies[link.second],
            link.stiffness, link.rest_length,
        )
    if gravitational_constant:
        for first in range(len(bodies)):
            for second in range(first + 1, len(bodies)):
                energy += gravitational_potential_energy(
                    bodies[first], bodies[second],
                    gravitational_constant, softening,
                )
    return energy
