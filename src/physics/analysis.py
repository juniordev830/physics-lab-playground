"""Trajectory recording, interpolation, diagnostics and CSV export.

The analysis functions are independent of graphics frameworks and operate on
immutable physics states, making experiments reproducible.
"""
from bisect import bisect_left
from collections.abc import Sequence
from dataclasses import dataclass
from io import StringIO
import csv
from math import isfinite

from .motion import Body2D, step, step_with_drag
from .vector2 import Vector2


@dataclass(frozen=True)
class TrajectoryPoint:
    time: float
    position: Vector2
    velocity: Vector2

    def __post_init__(self) -> None:
        if not isfinite(self.time) or self.time < 0:
            raise ValueError("Sample time must be finite and nonnegative")
        if not isinstance(self.position, Vector2) or not isinstance(self.velocity, Vector2):
            raise ValueError("Sample coordinates must be finite Vector2 values")


@dataclass(frozen=True)
class TrajectorySummary:
    duration: float
    distance: float
    displacement: Vector2
    average_speed: float
    peak_speed: float
    min_x: float
    min_y: float
    max_x: float
    max_y: float


def _validate_points(points: Sequence[TrajectoryPoint]) -> None:
    if not points:
        raise ValueError("At least one trajectory sample is required")
    if len(points) > 10001:
        raise ValueError("Too many trajectory samples")
    previous = None
    for point in points:
        if not isinstance(point, TrajectoryPoint):
            raise ValueError("Expected TrajectoryPoint samples")
        if previous is not None and point.time <= previous:
            raise ValueError("Sample times must be strictly increasing")
        previous = point.time


def sample_motion(
    initial: Body2D, force: Vector2, dt: float, steps: int, *,
    drag: float = 0.0,
) -> tuple[TrajectoryPoint, ...]:
    """Include initial state and each subsequent semi-implicit Euler step."""
    if not isinstance(initial, Body2D) or not isinstance(force, Vector2):
        raise ValueError("Expected a body and Vector2 force")
    if not isfinite(dt) or dt <= 0:
        raise ValueError("Sample time step must be positive and finite")
    if type(steps) is not int or not 0 <= steps <= 10000:
        raise ValueError("Steps must be an integer between 0 and 10000")
    if not isfinite(drag) or drag < 0:
        raise ValueError("Drag must be finite and nonnegative")
    body = initial
    points = [TrajectoryPoint(0, body.position, body.velocity)]
    for index in range(1, steps + 1):
        body = step_with_drag(body, force, dt, drag) if drag else step(body, force, dt)
        points.append(TrajectoryPoint(index * dt, body.position, body.velocity))
    return tuple(points)


def sample_force_schedule(
    initial: Body2D, forces: Sequence[Vector2], dt: float,
) -> tuple[TrajectoryPoint, ...]:
    """One constant force per interval, suitable for scripted experiments."""
    if not isinstance(initial, Body2D):
        raise ValueError("Expected a Body2D")
    if not isfinite(dt) or dt <= 0:
        raise ValueError("Sample time step must be positive and finite")
    if len(forces) > 10000:
        raise ValueError("Too many scheduled forces")
    body = initial
    points = [TrajectoryPoint(0, body.position, body.velocity)]
    for index, force in enumerate(forces, 1):
        if not isinstance(force, Vector2):
            raise ValueError("Scheduled forces must be Vector2 values")
        body = step(body, force, dt)
        points.append(TrajectoryPoint(index * dt, body.position, body.velocity))
    return tuple(points)


def trajectory_summary(points: Sequence[TrajectoryPoint]) -> TrajectorySummary:
    _validate_points(points)
    distance = sum(
        points[index - 1].position.distance_to(points[index].position)
        for index in range(1, len(points))
    )
    duration = points[-1].time - points[0].time
    displacement = points[-1].position - points[0].position
    speeds = [point.velocity.magnitude() for point in points]
    return TrajectorySummary(
        duration, distance, displacement,
        distance / duration if duration else 0.0,
        max(speeds),
        min(point.position.x for point in points),
        min(point.position.y for point in points),
        max(point.position.x for point in points),
        max(point.position.y for point in points),
    )


def interpolate_point(
    points: Sequence[TrajectoryPoint], time: float,
) -> TrajectoryPoint:
    """Linearly interpolate position and velocity within recorded samples."""
    _validate_points(points)
    if not isfinite(time) or not points[0].time <= time <= points[-1].time:
        raise ValueError("Requested time is outside recorded samples")
    times = [point.time for point in points]
    index = bisect_left(times, time)
    if index < len(points) and points[index].time == time:
        return points[index]
    before, after = points[index - 1], points[index]
    fraction = (time - before.time) / (after.time - before.time)
    return TrajectoryPoint(
        time, before.position.lerp(after.position, fraction),
        before.velocity.lerp(after.velocity, fraction),
    )


def crossing_times(
    points: Sequence[TrajectoryPoint], *, axis: str, level: float,
    direction: str = "any",
) -> tuple[float, ...]:
    """Times a piecewise-linear path crosses a horizontal or vertical line.

    A segment lying entirely on the line is ignored. Duplicate crossings at
    a shared vertex are returned only once.
    """
    _validate_points(points)
    if axis not in ("x", "y") or direction not in ("any", "rising", "falling"):
        raise ValueError("Invalid crossing axis or direction")
    if not isfinite(level):
        raise ValueError("Crossing level must be finite")
    result: list[float] = []
    for before, after in zip(points, points[1:]):
        first = getattr(before.position, axis) - level
        second = getattr(after.position, axis) - level
        if first == second:
            continue
        if first * second > 0:
            continue
        rising = second > first
        if direction == "rising" and not rising:
            continue
        if direction == "falling" and rising:
            continue
        fraction = -first / (second - first)
        time = before.time + fraction * (after.time - before.time)
        if not result or time != result[-1]:
            result.append(time)
    return tuple(result)


def resample_trajectory(
    points: Sequence[TrajectoryPoint], interval: float,
) -> tuple[TrajectoryPoint, ...]:
    """Regular-time samples including the exact final recorded time."""
    _validate_points(points)
    if not isfinite(interval) or interval <= 0:
        raise ValueError("Resampling interval must be positive and finite")
    start, end = points[0].time, points[-1].time
    steps = int((end - start) / interval)
    if steps > 9999:
        raise ValueError("Resampling would exceed 10,001 samples")
    result = [interpolate_point(points, start + index * interval) for index in range(steps + 1)]
    if result[-1].time != end:
        result.append(points[-1])
    return tuple(result)


def closest_approach(
    first: Sequence[TrajectoryPoint], second: Sequence[TrajectoryPoint],
) -> tuple[float, float]:
    """Closest separation on two identically sampled timelines."""
    _validate_points(first)
    _validate_points(second)
    if len(first) != len(second):
        raise ValueError("Trajectories must have matching sample counts")
    for a, b in zip(first, second):
        if a.time != b.time:
            raise ValueError("Trajectories must have identical sample times")
    point = min(
        zip(first, second),
        key=lambda pair: pair[0].position.distance_to(pair[1].position),
    )
    return point[0].time, point[0].position.distance_to(point[1].position)


def trajectory_csv(points: Sequence[TrajectoryPoint]) -> str:
    """Export numeric samples using CSV quoting and deterministic columns."""
    _validate_points(points)
    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("time", "x", "y", "vx", "vy", "speed"))
    for point in points:
        writer.writerow((
            point.time, point.position.x, point.position.y,
            point.velocity.x, point.velocity.y, point.velocity.magnitude(),
        ))
    return output.getvalue()
