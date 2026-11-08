"""Frictionless circle contacts with impulses and mass-weighted overlap correction."""
from dataclasses import dataclass
from math import isfinite

from .vector2 import Vector2
from .motion import Body2D


@dataclass(frozen=True)
class Circle:
    body: Body2D
    radius: float

    def __post_init__(self) -> None:
        if not isinstance(self.body, Body2D):
            raise ValueError("Circle requires a Body2D")
        if not isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Radius must be positive and finite")


def overlaps(a: Circle, b: Circle) -> bool:
    delta = a.body.position - b.body.position
    return delta.magnitude_squared() <= (a.radius + b.radius) ** 2


def _contact_normal(a: Circle, b: Circle) -> Vector2:
    delta = b.body.position - a.body.position
    if delta.magnitude() > 0:
        return delta.normalized()
    relative = b.body.velocity - a.body.velocity
    if relative.magnitude() > 0:
        return -relative.normalized()
    return Vector2(1, 0)


def _validate_restitution(restitution: float) -> None:
    if not isfinite(restitution) or not 0 <= restitution <= 1:
        raise ValueError("Restitution must be between zero and one")


def resolve_velocity(
    a: Circle, b: Circle, restitution: float = 1.0,
) -> tuple[Body2D, Body2D]:
    """Apply a frictionless impulse to colliding and approaching bodies."""
    _validate_restitution(restitution)
    if not overlaps(a, b):
        return a.body, b.body
    normal = _contact_normal(a, b)
    relative = b.body.velocity - a.body.velocity
    closing_speed = relative.dot(normal)
    if closing_speed >= 0:
        return a.body, b.body
    inv_a, inv_b = 1 / a.body.mass, 1 / b.body.mass
    impulse = -(1 + restitution) * closing_speed / (inv_a + inv_b)
    va = a.body.velocity - normal * (impulse * inv_a)
    vb = b.body.velocity + normal * (impulse * inv_b)
    return (
        Body2D(a.body.position, va, a.body.mass),
        Body2D(b.body.position, vb, b.body.mass),
    )


def resolve_contact(
    a: Circle, b: Circle, restitution: float = 1.0,
    correction: float = 1.0,
) -> tuple[Circle, Circle]:
    """Resolve velocity and overlap; correction=0 disables position changes.

    Penetration is shared by inverse mass, so heavier bodies move less.
    This is a teaching approximation, not a continuous collision solver.
    """
    _validate_restitution(restitution)
    if not isfinite(correction) or not 0 <= correction <= 1:
        raise ValueError("Correction must be between zero and one")
    if not overlaps(a, b):
        return a, b
    va, vb = resolve_velocity(a, b, restitution)
    delta = b.body.position - a.body.position
    penetration = max(0.0, a.radius + b.radius - delta.magnitude())
    normal = _contact_normal(a, b)
    inv_a, inv_b = 1 / a.body.mass, 1 / b.body.mass
    offset = normal * (penetration * correction / (inv_a + inv_b))
    new_a = Body2D(a.body.position - offset * inv_a, va.velocity, a.body.mass)
    new_b = Body2D(b.body.position + offset * inv_b, vb.velocity, b.body.mass)
    return Circle(new_a, a.radius), Circle(new_b, b.radius)
