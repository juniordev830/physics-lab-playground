import math
import unittest

from src.physics.motion import (
    Body2D, center_of_mass, step, step_many, step_with_drag,
    total_kinetic_energy, total_momentum,
)
from src.physics.vector2 import Vector2


def body(x=0, vx=0, mass=1):
    return Body2D(Vector2(x, 0), Vector2(vx, 0), mass)


class MotionDiagnosticsTests(unittest.TestCase):
    def test_momentum(self):
        self.assertEqual(body(vx=3, mass=2).momentum(), Vector2(6, 0))

    def test_kinetic_energy(self):
        self.assertEqual(body(vx=3, mass=2).kinetic_energy(), 9)

    def test_total_momentum(self):
        self.assertEqual(
            total_momentum([body(vx=2, mass=3), body(vx=-3, mass=2)]),
            Vector2(0, 0),
        )

    def test_total_momentum_empty(self):
        self.assertEqual(total_momentum([]), Vector2(0, 0))

    def test_total_kinetic_energy(self):
        self.assertEqual(total_kinetic_energy([body(vx=2), body(vx=3)]), 6.5)

    def test_total_kinetic_energy_empty(self):
        self.assertEqual(total_kinetic_energy([]), 0)

    def test_center_of_mass_equal_masses(self):
        self.assertEqual(center_of_mass([body(x=0), body(x=10)]), Vector2(5, 0))

    def test_center_of_mass_weighted(self):
        self.assertEqual(
            center_of_mass([body(x=0, mass=3), body(x=8, mass=1)]),
            Vector2(2, 0),
        )

    def test_center_of_mass_empty_rejected(self):
        with self.assertRaises(ValueError):
            center_of_mass([])

    def test_step_many_matches_individual_steps(self):
        bodies = [body(x=1, vx=2), body(x=4, vx=-1, mass=2)]
        forces = [Vector2(3, 0), Vector2(0, 5)]
        actual = step_many(bodies, forces, 0.25)
        expected = [step(b, f, 0.25) for b, f in zip(bodies, forces)]
        self.assertEqual(actual, expected)
        self.assertEqual(bodies[0], body(x=1, vx=2))

    def test_step_many_rejects_mismatched_forces(self):
        with self.assertRaises(ValueError):
            step_many([body(), body()], [Vector2(0, 0)], 1)

    def test_step_many_empty(self):
        self.assertEqual(step_many([], [], 1), [])

    def test_step_many_rejects_excessive_bodies(self):
        bodies = [body()] * 10001
        forces = [Vector2(0, 0)] * 10001
        with self.assertRaises(ValueError):
            step_many(bodies, forces, 0.1)

    def test_drag_zero_matches_step(self):
        initial = body(x=1, vx=2, mass=2)
        force = Vector2(4, 0)
        self.assertEqual(step_with_drag(initial, force, 0.5, 0), step(initial, force, 0.5))

    def test_drag_reduces_speed(self):
        result = step_with_drag(body(vx=10), Vector2(0, 0), 1, 0.5)
        self.assertAlmostEqual(result.velocity.x, 10 * math.exp(-0.5))
        self.assertLess(result.kinetic_energy(), body(vx=10).kinetic_energy())

    def test_drag_zero_dt_returns_original(self):
        initial = body(vx=10)
        self.assertIs(step_with_drag(initial, Vector2(3, 0), 0, 10), initial)

    def test_drag_invalid_negative(self):
        with self.assertRaises(ValueError):
            step_with_drag(body(), Vector2(0, 0), 1, -1)

    def test_drag_invalid_nonfinite(self):
        with self.assertRaises(ValueError):
            step_with_drag(body(), Vector2(0, 0), 1, float("inf"))

    def test_invalid_force_type(self):
        with self.assertRaises(ValueError):
            step(body(), "not-a-vector", 1)

    def test_body_rejects_invalid_position(self):
        with self.assertRaises(ValueError):
            Body2D("wrong", Vector2(0, 0), 1)

    def test_body_rejects_invalid_velocity(self):
        with self.assertRaises(ValueError):
            Body2D(Vector2(0, 0), None, 1)

    def test_step_preserves_mass(self):
        initial = body(x=2, vx=3, mass=4)
        self.assertEqual(step(initial, Vector2(1, 2), 0.2).mass, 4)

    def test_step_many_preserves_order(self):
        result = step_many(
            [body(x=1), body(x=10)],
            [Vector2(0, 0), Vector2(0, 0)],
            1,
        )
        self.assertEqual([b.position.x for b in result], [1, 10])


if __name__ == "__main__":
    unittest.main()
