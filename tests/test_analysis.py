import csv
import io
import unittest

from src.physics.analysis import (
    TrajectoryPoint, closest_approach, crossing_times, interpolate_point,
    resample_trajectory, sample_force_schedule, sample_motion,
    trajectory_csv, trajectory_summary,
)
from src.physics.motion import Body2D
from src.physics.vector2 import Vector2


def body(x=0, vx=0, mass=1, y=0, vy=0):
    return Body2D(Vector2(x, y), Vector2(vx, vy), mass)


def point(t, x, y=0, vx=0, vy=0):
    return TrajectoryPoint(t, Vector2(x, y), Vector2(vx, vy))


class SampleMotionTests(unittest.TestCase):
    def test_zero_steps_returns_initial(self):
        self.assertEqual(
            sample_motion(body(2, 3), Vector2(0, 0), 1, 0),
            (point(0, 2, vx=3),),
        )

    def test_constant_velocity(self):
        points = sample_motion(body(1, 2), Vector2(0, 0), 0.5, 2)
        self.assertEqual([p.position.x for p in points], [1, 2, 3])
        self.assertEqual([p.time for p in points], [0, 0.5, 1])

    def test_acceleration(self):
        points = sample_motion(body(mass=2), Vector2(4, 0), 0.5, 2)
        self.assertEqual(points[-1].velocity.x, 2)
        self.assertEqual(points[-1].position.x, 1.5)

    def test_drag_reduces_speed(self):
        points = sample_motion(body(vx=10), Vector2(0, 0), 0.1, 10, drag=1)
        self.assertLess(points[-1].velocity.x, 10)
        self.assertGreater(points[-1].position.x, 0)

    def test_invalid_time_step(self):
        for dt in (0, -1, float("nan")):
            with self.subTest(dt=dt), self.assertRaises(ValueError):
                sample_motion(body(), Vector2(0, 0), dt, 1)

    def test_invalid_step_count(self):
        for steps in (-1, 10001, True):
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                sample_motion(body(), Vector2(0, 0), 1, steps)

    def test_invalid_drag(self):
        with self.assertRaises(ValueError):
            sample_motion(body(), Vector2(0, 0), 1, 1, drag=-1)

    def test_invalid_force_type(self):
        with self.assertRaises(ValueError):
            sample_motion(body(), "force", 1, 1)

    def test_force_schedule(self):
        points = sample_force_schedule(
            body(), [Vector2(1, 0), Vector2(-1, 0)], 1,
        )
        self.assertEqual([p.velocity.x for p in points], [0, 1, 0])
        self.assertEqual(points[-1].position.x, 2)

    def test_force_schedule_empty(self):
        self.assertEqual(sample_force_schedule(body(1), [], 1), (point(0, 1),))

    def test_force_schedule_invalid_force(self):
        with self.assertRaises(ValueError):
            sample_force_schedule(body(), [Vector2(0, 0), None], 1)

    def test_force_schedule_invalid_dt(self):
        with self.assertRaises(ValueError):
            sample_force_schedule(body(), [], 0)


class TrajectorySummaryTests(unittest.TestCase):
    def test_straight_line(self):
        summary = trajectory_summary((point(0, 0, vx=2), point(2, 4, vx=2)))
        self.assertEqual(summary.distance, 4)
        self.assertEqual(summary.duration, 2)
        self.assertEqual(summary.average_speed, 2)
        self.assertEqual(summary.displacement, Vector2(4, 0))
        self.assertEqual(summary.peak_speed, 2)

    def test_round_trip_distance_vs_displacement(self):
        summary = trajectory_summary((point(0, 0), point(1, 3), point(2, 0)))
        self.assertEqual(summary.distance, 6)
        self.assertEqual(summary.displacement, Vector2(0, 0))

    def test_bounding_box(self):
        summary = trajectory_summary((
            point(0, -1, 4), point(1, 3, -2), point(2, 2, 8),
        ))
        self.assertEqual(
            (summary.min_x, summary.min_y, summary.max_x, summary.max_y),
            (-1, -2, 3, 8),
        )

    def test_single_point(self):
        summary = trajectory_summary((point(5, 2),))
        self.assertEqual(summary.duration, 0)
        self.assertEqual(summary.distance, 0)
        self.assertEqual(summary.average_speed, 0)

    def test_empty_trajectory_rejected(self):
        with self.assertRaises(ValueError):
            trajectory_summary([])

    def test_duplicate_times_rejected(self):
        with self.assertRaises(ValueError):
            trajectory_summary((point(0, 0), point(0, 1)))

    def test_decreasing_times_rejected(self):
        with self.assertRaises(ValueError):
            trajectory_summary((point(1, 0), point(0, 1)))

    def test_invalid_sample_rejected(self):
        with self.assertRaises(ValueError):
            trajectory_summary((point(0, 0), "bad"))

    def test_nonfinite_sample_time_rejected(self):
        with self.assertRaises(ValueError):
            point(float("nan"), 0)


class InterpolationTests(unittest.TestCase):
    def setUp(self):
        self.points = (point(0, 0, vx=2), point(2, 4, vx=4))

    def test_interpolates_midpoint(self):
        result = interpolate_point(self.points, 1)
        self.assertEqual(result.position, Vector2(2, 0))
        self.assertEqual(result.velocity, Vector2(3, 0))

    def test_exact_endpoint_returns_original(self):
        self.assertIs(interpolate_point(self.points, 2), self.points[1])

    def test_outside_interval_rejected(self):
        with self.assertRaises(ValueError):
            interpolate_point(self.points, 3)

    def test_nonfinite_requested_time_rejected(self):
        with self.assertRaises(ValueError):
            interpolate_point(self.points, float("inf"))

    def test_resample_regular_grid(self):
        result = resample_trajectory(self.points, 0.5)
        self.assertEqual([p.time for p in result], [0, 0.5, 1, 1.5, 2])

    def test_resample_keeps_last_point(self):
        result = resample_trajectory(self.points, 0.7)
        self.assertEqual(result[-1], self.points[-1])
        self.assertEqual(len(result), 4)

    def test_resample_single_point(self):
        self.assertEqual(resample_trajectory((point(2, 3),), 1), (point(2, 3),))

    def test_resample_invalid_interval(self):
        with self.assertRaises(ValueError):
            resample_trajectory(self.points, 0)

    def test_resample_rejects_excessive_samples(self):
        with self.assertRaises(ValueError):
            resample_trajectory(self.points, 0.00001)


class CrossingTests(unittest.TestCase):
    def setUp(self):
        self.points = (point(0, -1), point(1, 1), point(2, -1))

    def test_crossing_both_directions(self):
        self.assertEqual(
            crossing_times(self.points, axis="x", level=0),
            (0.5, 1.5),
        )

    def test_rising_only(self):
        self.assertEqual(
            crossing_times(self.points, axis="x", level=0, direction="rising"),
            (0.5,),
        )

    def test_falling_only(self):
        self.assertEqual(
            crossing_times(self.points, axis="x", level=0, direction="falling"),
            (1.5,),
        )

    def test_vertex_crossing_deduplicated(self):
        points = (point(0, -1), point(1, 0), point(2, 1))
        self.assertEqual(crossing_times(points, axis="x", level=0), (1,))

    def test_flat_segment_ignored(self):
        points = (point(0, 0), point(1, 0), point(2, 1))
        self.assertEqual(crossing_times(points, axis="x", level=0), (1,))

    def test_vertical_axis(self):
        points = (point(0, 0, -2), point(2, 0, 2))
        self.assertEqual(crossing_times(points, axis="y", level=0), (1,))

    def test_no_crossing(self):
        self.assertEqual(crossing_times(self.points, axis="x", level=5), ())

    def test_invalid_axis(self):
        with self.assertRaises(ValueError):
            crossing_times(self.points, axis="z", level=0)

    def test_invalid_direction(self):
        with self.assertRaises(ValueError):
            crossing_times(self.points, axis="x", level=0, direction="left")


class ComparisonAndExportTests(unittest.TestCase):
    def test_closest_approach(self):
        first = (point(0, 0), point(1, 2), point(2, 4))
        second = (point(0, 5), point(1, 3), point(2, 0))
        self.assertEqual(closest_approach(first, second), (1, 1))

    def test_reject_different_sample_counts(self):
        with self.assertRaises(ValueError):
            closest_approach((point(0, 0),), (point(0, 0), point(1, 1)))

    def test_reject_different_sample_times(self):
        with self.assertRaises(ValueError):
            closest_approach((point(0, 0),), (point(1, 0),))

    def test_csv_header_and_numeric_values(self):
        rows = list(csv.reader(io.StringIO(trajectory_csv((point(0, 2, 3, 4, 0),)))))
        self.assertEqual(rows[0], ["time", "x", "y", "vx", "vy", "speed"])
        self.assertEqual([float(value) for value in rows[1]], [0, 2, 3, 4, 0, 4])

    def test_csv_contains_all_points(self):
        data = trajectory_csv((point(0, 0), point(1, 1), point(2, 2)))
        self.assertEqual(len(list(csv.reader(io.StringIO(data)))), 4)

    def test_csv_rejects_empty(self):
        with self.assertRaises(ValueError):
            trajectory_csv([])


if __name__ == "__main__":
    unittest.main()
