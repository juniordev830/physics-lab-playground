"""Immutable, bounded 2D circle world with discrete collision resolution.

The solver uses semi-implicit Euler and pairwise contacts. It is educational,
not continuous collision detection or a general rigid-body engine.
"""
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from math import isfinite

from .collision import Circle, overlaps, resolve_contact
from .forces import SpringLink, UniformField, net_forces, total_potential_energy
from .motion import Body2D, center_of_mass, step_with_drag, total_kinetic_energy, total_momentum
from .vector2 import Vector2


@dataclass(frozen=True)
class Bounds2D:
    left: float
    bottom: float
    right: float
    top: float

    def __post_init__(self) -> None:
        values = (self.left, self.bottom, self.right, self.top)
        if not all(isfinite(value) for value in values):
            raise ValueError("Bounds must be finite")
        if self.left >= self.right or self.bottom >= self.top:
            raise ValueError("Bounds must have positive width and height")

    def fits(self, radius: float) -> bool:
        return 2 * radius <= min(self.right - self.left, self.top - self.bottom)


@dataclass(frozen=True)
class WorldSettings:
    gravity: Vector2 = Vector2(0, 0)
    drag: float = 0.0
    restitution: float = 1.0
    correction: float = 1.0
    solver_iterations: int = 2
    bounds: Bounds2D | None = None
    springs: tuple[SpringLink, ...] = ()
    gravitational_constant: float = 0.0
    softening: float = 0.1

    def __post_init__(self) -> None:
        if not isinstance(self.gravity, Vector2):
            raise ValueError("Gravity must be Vector2")
        for value, label in (
            (self.drag, "Drag"),
            (self.gravitational_constant, "Gravitational constant"),
            (self.softening, "Softening"),
        ):
            if not isfinite(value) or value < 0:
                raise ValueError(f"{label} must be finite and nonnegative")
        for value, label in (
            (self.restitution, "Restitution"), (self.correction, "Correction"),
        ):
            if not isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{label} must be in [0, 1]")
        if type(self.solver_iterations) is not int or not 1 <= self.solver_iterations <= 16:
            raise ValueError("Solver iterations must be between 1 and 16")
        if self.bounds is not None and not isinstance(self.bounds, Bounds2D):
            raise ValueError("Bounds must be Bounds2D")
        if not isinstance(self.springs, tuple):
            raise ValueError("Springs must be a tuple")


@dataclass(frozen=True)
class WorldSnapshot:
    circles: tuple[Circle, ...]
    time: float = 0.0
    tick: int = 0
    contacts: int = 0
    wall_hits: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.circles, tuple) or len(self.circles) > 256:
            raise ValueError("World requires a tuple of at most 256 circles")
        if any(not isinstance(circle, Circle) for circle in self.circles):
            raise ValueError("World entries must be circles")
        if not isfinite(self.time) or self.time < 0:
            raise ValueError("World time must be finite and nonnegative")
        for value in (self.tick, self.contacts, self.wall_hits):
            if type(value) is not int or value < 0:
                raise ValueError("World counters must be nonnegative integers")


@dataclass(frozen=True)
class WorldMetrics:
    time: float
    tick: int
    kinetic_energy: float
    potential_energy: float
    momentum: Vector2
    center_of_mass: Vector2 | None
    contacts: int
    wall_hits: int

    @property
    def mechanical_energy(self) -> float:
        return self.kinetic_energy + self.potential_energy


def _confine(circle: Circle, bounds: Bounds2D, restitution: float) -> tuple[Circle, int]:
    if not bounds.fits(circle.radius):
        raise ValueError("Circle diameter exceeds world bounds")
    body = circle.body
    x, y = body.position.x, body.position.y
    vx, vy = body.velocity.x, body.velocity.y
    min_x, max_x = bounds.left + circle.radius, bounds.right - circle.radius
    min_y, max_y = bounds.bottom + circle.radius, bounds.top - circle.radius
    hits = 0
    if x < min_x or (x == min_x and vx < 0):
        x = min_x
        if vx < 0:
            vx = -vx * restitution
            hits += 1
    elif x > max_x or (x == max_x and vx > 0):
        x = max_x
        if vx > 0:
            vx = -vx * restitution
            hits += 1
    if y < min_y or (y == min_y and vy < 0):
        y = min_y
        if vy < 0:
            vy = -vy * restitution
            hits += 1
    elif y > max_y or (y == max_y and vy > 0):
        y = max_y
        if vy > 0:
            vy = -vy * restitution
            hits += 1
    return Circle(Body2D(Vector2(x, y), Vector2(vx, vy), body.mass), circle.radius), hits


def contact_pairs(snapshot: WorldSnapshot) -> tuple[tuple[int, int], ...]:
    """Indices of touching or overlapping circles in deterministic order."""
    if not isinstance(snapshot, WorldSnapshot):
        raise ValueError("Expected a WorldSnapshot")
    return tuple(
        (i, j)
        for i in range(len(snapshot.circles))
        for j in range(i + 1, len(snapshot.circles))
        if overlaps(snapshot.circles[i], snapshot.circles[j])
    )


def advance_world(
    snapshot: WorldSnapshot, dt: float, settings: WorldSettings,
    external: Sequence[Vector2] | None = None,
) -> WorldSnapshot:
    """Integrate forces, resolve contacts, then reflect off optional walls.

    A zero-length step is an identity operation. Large steps can tunnel
    through thin objects; choose dt small enough for the simulated speed.
    """
    if not isinstance(snapshot, WorldSnapshot) or not isinstance(settings, WorldSettings):
        raise ValueError("Expected a world snapshot and settings")
    if not isfinite(dt) or dt < 0:
        raise ValueError("Time step must be finite and nonnegative")
    bodies = [circle.body for circle in snapshot.circles]
    forces = net_forces(
        bodies, field=UniformField(settings.gravity),
        springs=settings.springs,
        gravitational_constant=settings.gravitational_constant,
        softening=settings.softening, external=external,
    )
    if settings.bounds is not None:
        for circle in snapshot.circles:
            if not settings.bounds.fits(circle.radius):
                raise ValueError("Circle diameter exceeds world bounds")
    if dt == 0:
        return snapshot
    circles = [
        Circle(step_with_drag(circle.body, force, dt, settings.drag), circle.radius)
        for circle, force in zip(snapshot.circles, forces)
    ]
    pairs: set[tuple[int, int]] = set()
    for _ in range(settings.solver_iterations):
        for i in range(len(circles)):
            for j in range(i + 1, len(circles)):
                if not overlaps(circles[i], circles[j]):
                    continue
                left, right = resolve_contact(
                    circles[i], circles[j], settings.restitution, settings.correction,
                )
                if left != circles[i] or right != circles[j]:
                    pairs.add((i, j))
                circles[i], circles[j] = left, right
    wall_hits = 0
    if settings.bounds is not None:
        for i, circle in enumerate(circles):
            circles[i], hits = _confine(circle, settings.bounds, settings.restitution)
            wall_hits += hits
    return WorldSnapshot(
        tuple(circles), snapshot.time + dt, snapshot.tick + 1,
        len(pairs), wall_hits,
    )


def world_metrics(snapshot: WorldSnapshot, settings: WorldSettings) -> WorldMetrics:
    if not isinstance(snapshot, WorldSnapshot) or not isinstance(settings, WorldSettings):
        raise ValueError("Expected a world snapshot and settings")
    bodies = [circle.body for circle in snapshot.circles]
    potential = total_potential_energy(
        bodies, field=UniformField(settings.gravity),
        springs=settings.springs,
        gravitational_constant=settings.gravitational_constant,
        softening=settings.softening,
    )
    return WorldMetrics(
        snapshot.time, snapshot.tick, total_kinetic_energy(bodies),
        potential, total_momentum(bodies),
        center_of_mass(bodies) if bodies else None,
        snapshot.contacts, snapshot.wall_hits,
    )


def simulate_world(
    initial: WorldSnapshot, settings: WorldSettings, dt: float, steps: int, *,
    sample_every: int = 1,
    force_provider: Callable[[WorldSnapshot], Sequence[Vector2]] | None = None,
) -> tuple[WorldSnapshot, ...]:
    """Return initial, periodic snapshots and final snapshot.

    Maximum 10,000 steps and 2,000 stored snapshots prevent accidental
    unbounded allocations. A force provider sees the pre-step snapshot.
    """
    if type(steps) is not int or not 0 <= steps <= 10000:
        raise ValueError("Steps must be an integer between 0 and 10000")
    if type(sample_every) is not int or sample_every < 1:
        raise ValueError("Sample interval must be a positive integer")
    if (steps // sample_every) + 2 > 2000:
        raise ValueError("Too many stored snapshots")
    if not isinstance(initial, WorldSnapshot) or not isinstance(settings, WorldSettings):
        raise ValueError("Expected a world snapshot and settings")
    if not isfinite(dt) or dt < 0:
        raise ValueError("Time step must be finite and nonnegative")
    if force_provider is not None and not callable(force_provider):
        raise ValueError("Force provider must be callable")
    current = initial
    history = [current]
    for index in range(1, steps + 1):
        external = force_provider(current) if force_provider else None
        current = advance_world(current, dt, settings, external)
        if index % sample_every == 0 or index == steps:
            history.append(current)
    return tuple(history)
