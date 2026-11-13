"""Deterministic 2D toy physics model (metres, seconds; upward Y)."""
from dataclasses import dataclass, replace
from math import isfinite


def finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return float(value)


@dataclass(frozen=True)
class Body:
    x: float
    y: float
    vx: float = 0
    vy: float = 0
    mass: float = 1

    def __post_init__(self):
        for name in ("x", "y", "vx", "vy", "mass"):
            finite(getattr(self, name), name)
        if self.mass <= 0 or self.y < 0:
            raise ValueError("mass must be positive and body above the ground")


class World:
    """Semi-implicit Euler with a ground at y=0 and deterministic reset."""

    def __init__(self, body: Body, gravity: float = 9.81, restitution: float = 0):
        self.initial = body
        self.gravity = finite(gravity, "gravity")
        self.restitution = finite(restitution, "restitution")
        if self.gravity < 0 or not 0 <= self.restitution <= 1:
            raise ValueError("invalid gravity or restitution")
        self.reset()

    def reset(self):
        self.body = self.initial
        self.time = 0.0
        self.paused = False

    def pause(self, value: bool = True):
        if not isinstance(value, bool):
            raise ValueError("pause must be boolean")
        self.paused = value

    def step(self, dt: float):
        dt = finite(dt, "dt")
        if not 0 < dt <= 0.1:
            raise ValueError("dt must be between 0 and 0.1 seconds")
        if self.paused:
            return self.body
        b = self.body
        vy = b.vy - self.gravity * dt
        y = b.y + vy * dt
        if y < 0:
            y = 0.0
            vy = -vy * self.restitution
            if abs(vy) < 1e-8:
                vy = 0.0
        self.body = replace(b, x=b.x + b.vx * dt, y=y, vy=vy)
        self.time += dt
        return self.body


if __name__ == "__main__":
    world = World(Body(0, 5), restitution=0.4)
    for _ in range(100):
        world.step(0.02)
    print(f"After {world.time:.1f}s: height={world.body.y:.2f}m")
