"""Simple, deterministic Newtonian motion for 2D simulations."""
from dataclasses import dataclass
from math import isfinite
from .vector2 import Vector2


@dataclass(frozen=True)
class Body2D:
    position: Vector2
    velocity: Vector2
    mass: float

    def __post_init__(self):
        if not isfinite(self.mass) or self.mass <= 0:
            raise ValueError('mass must be positive and finite')


def step(body: Body2D, force: Vector2, dt: float) -> Body2D:
    """Semi-implicit Euler step: velocity first, then position."""
    if not isfinite(dt) or dt < 0:
        raise ValueError('dt must be nonnegative and finite')
    acceleration = force * (1.0 / body.mass)
    velocity = body.velocity + acceleration * dt
    position = body.position + velocity * dt
    return Body2D(position=position, velocity=velocity, mass=body.mass)
