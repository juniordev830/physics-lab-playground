"""Circle collision helpers for simple 2D rigid-body simulations."""
from dataclasses import dataclass
from math import isfinite
from .vector2 import Vector2
from .motion import Body2D


@dataclass(frozen=True)
class Circle:
    body: Body2D
    radius: float

    def __post_init__(self):
        if not isfinite(self.radius) or self.radius <= 0:
            raise ValueError('radius must be positive and finite')


def overlaps(a: Circle, b: Circle) -> bool:
    delta = a.body.position - b.body.position
    return delta.dot(delta) <= (a.radius + b.radius) ** 2


def resolve_velocity(a: Circle, b: Circle, restitution: float = 1.0) -> tuple[Body2D, Body2D]:
    """Apply a frictionless impulse; does not correct positional penetration."""
    if not isfinite(restitution) or not 0 <= restitution <= 1:
        raise ValueError('restitution must be between zero and one')
    delta = b.body.position - a.body.position
    normal = delta.normalized()
    if normal.magnitude() == 0:
        return a.body, b.body
    relative = b.body.velocity - a.body.velocity
    speed = relative.dot(normal)
    if speed >= 0 or not overlaps(a, b):
        return a.body, b.body
    impulse = -(1 + restitution) * speed / (1 / a.body.mass + 1 / b.body.mass)
    va = a.body.velocity - normal * (impulse / a.body.mass)
    vb = b.body.velocity + normal * (impulse / b.body.mass)
    return (Body2D(a.body.position, va, a.body.mass),
            Body2D(b.body.position, vb, b.body.mass))
