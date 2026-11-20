"""Immutable 2D vector operations for deterministic educational simulations."""
from dataclasses import dataclass
from math import cos, hypot, isfinite, sin


@dataclass(frozen=True)
class Vector2:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not (isfinite(self.x) and isfinite(self.y)):
            raise ValueError("Vector components must be finite")

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x - other.x, self.y - other.y)

    def __neg__(self) -> "Vector2":
        return Vector2(-self.x, -self.y)

    def __mul__(self, scalar: float) -> "Vector2":
        if not isfinite(scalar):
            raise ValueError("Scalar must be finite")
        return Vector2(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar: float) -> "Vector2":
        if not isfinite(scalar) or scalar == 0:
            raise ValueError("Divisor must be finite and nonzero")
        return Vector2(self.x / scalar, self.y / scalar)

    def dot(self, other: "Vector2") -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Vector2") -> float:
        """Signed scalar z-component of the 2D cross product."""
        return self.x * other.y - self.y * other.x

    def magnitude_squared(self) -> float:
        return self.dot(self)

    def magnitude(self) -> float:
        return hypot(self.x, self.y)

    def distance_to(self, other: "Vector2") -> float:
        return (self - other).magnitude()

    def normalized(self) -> "Vector2":
        length = self.magnitude()
        return Vector2(0.0, 0.0) if length == 0 else self / length

    def perpendicular(self) -> "Vector2":
        """Rotate by +90 degrees without trigonometric rounding."""
        return Vector2(-self.y, self.x)

    def rotated(self, radians: float) -> "Vector2":
        if not isfinite(radians):
            raise ValueError("Rotation must be finite")
        c, s = cos(radians), sin(radians)
        return Vector2(self.x * c - self.y * s, self.x * s + self.y * c)

    def clamp_magnitude(self, maximum: float) -> "Vector2":
        if not isfinite(maximum) or maximum < 0:
            raise ValueError("Maximum magnitude must be nonnegative and finite")
        length = self.magnitude()
        if length <= maximum:
            return self
        return self * (maximum / length)

    def lerp(self, other: "Vector2", fraction: float) -> "Vector2":
        if not isfinite(fraction) or not 0 <= fraction <= 1:
            raise ValueError("Interpolation fraction must be between zero and one")
        return self + (other - self) * fraction
