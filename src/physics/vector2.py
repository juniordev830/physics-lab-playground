"""Dependency-free 2D vector primitives for physics simulations."""
from dataclasses import dataclass
from math import hypot, isfinite


@dataclass(frozen=True)
class Vector2:
    x: float
    y: float

    def __post_init__(self):
        if not (isfinite(self.x) and isfinite(self.y)):
            raise ValueError('Vector components must be finite')

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def dot(self, other: 'Vector2') -> float:
        return self.x * other.x + self.y * other.y

    def magnitude(self) -> float:
        return hypot(self.x, self.y)

    def normalized(self) -> 'Vector2':
        length = self.magnitude()
        return Vector2(0.0, 0.0) if length == 0 else self * (1 / length)
