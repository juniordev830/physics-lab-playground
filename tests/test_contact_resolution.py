import unittest

from src.physics.collision import Circle, overlaps, resolve_contact, resolve_velocity
from src.physics.motion import Body2D, total_kinetic_energy, total_momentum
from src.physics.vector2 import Vector2


def circle(x, vx=0, mass=1, radius=1, y=0, vy=0):
    return Circle(
        Body2D(Vector2(x, y), Vector2(vx, vy), mass),
        radius,
    )


class ContactResolutionTests(unittest.TestCase):
    def test_separated_circles_unchanged(self):
        a, b = circle(0, 1), circle(10, -1)
        self.assertEqual(resolve_contact(a, b), (a, b))

    def test_tangent_circles_count_as_contact(self):
        self.assertTrue(overlaps(circle(0), circle(2)))

    def test_overlap_is_removed(self):
        a, b = resolve_contact(circle(0), circle(1.5))
        self.assertAlmostEqual(a.body.position.distance_to(b.body.position), 2)

    def test_heavier_body_moves_less(self):
        a, b = resolve_contact(circle(0, mass=10), circle(1, mass=1))
        left_shift = abs(a.body.position.x)
        right_shift = abs(b.body.position.x - 1)
        self.assertAlmostEqual(right_shift / left_shift, 10)

    def test_correction_zero_preserves_positions(self):
        a, b = circle(0, 1), circle(1.5, -1)
        left, right = resolve_contact(a, b, correction=0)
        self.assertEqual(left.body.position, a.body.position)
        self.assertEqual(right.body.position, b.body.position)
        self.assertNotEqual(left.body.velocity, a.body.velocity)

    def test_partial_correction(self):
        a, b = resolve_contact(circle(0), circle(1), correction=0.5)
        self.assertAlmostEqual(a.body.position.distance_to(b.body.position), 1.5)

    def test_elastic_collision_conserves_momentum(self):
        a, b = circle(0, 2, mass=3), circle(1.5, -1, mass=2)
        initial = total_momentum([a.body, b.body])
        left, right = resolve_contact(a, b, restitution=1)
        final = total_momentum([left.body, right.body])
        self.assertAlmostEqual(initial.x, final.x)
        self.assertAlmostEqual(initial.y, final.y)

    def test_elastic_collision_conserves_kinetic_energy(self):
        a, b = circle(0, 2, mass=3), circle(1.5, -1, mass=2)
        initial = total_kinetic_energy([a.body, b.body])
        left, right = resolve_contact(a, b, restitution=1)
        final = total_kinetic_energy([left.body, right.body])
        self.assertAlmostEqual(initial, final)

    def test_inelastic_collision_loses_kinetic_energy(self):
        a, b = circle(0, 2), circle(1.5, -2)
        before = total_kinetic_energy([a.body, b.body])
        left, right = resolve_contact(a, b, restitution=0)
        after = total_kinetic_energy([left.body, right.body])
        self.assertLess(after, before)

    def test_coincident_centers_are_separated(self):
        a, b = resolve_contact(circle(0), circle(0))
        self.assertAlmostEqual(a.body.position.distance_to(b.body.position), 2)

    def test_coincident_moving_bodies_exchange_velocity(self):
        a, b = resolve_contact(circle(0, 1), circle(0, -1))
        self.assertEqual(a.body.velocity, Vector2(-1, 0))
        self.assertEqual(b.body.velocity, Vector2(1, 0))

    def test_moving_apart_does_not_impulse(self):
        a, b = circle(0, -1), circle(1.5, 1)
        left, right = resolve_contact(a, b)
        self.assertEqual(left.body.velocity, a.body.velocity)
        self.assertEqual(right.body.velocity, b.body.velocity)

    def test_vertical_collision(self):
        a, b = circle(0, y=0, vy=2), circle(0, y=1.5, vy=-2)
        left, right = resolve_contact(a, b)
        self.assertEqual(left.body.velocity, Vector2(0, -2))
        self.assertEqual(right.body.velocity, Vector2(0, 2))

    def test_reject_negative_correction(self):
        with self.assertRaises(ValueError):
            resolve_contact(circle(0), circle(1), correction=-0.1)

    def test_reject_excessive_correction(self):
        with self.assertRaises(ValueError):
            resolve_contact(circle(0), circle(1), correction=1.1)

    def test_reject_nonfinite_correction(self):
        with self.assertRaises(ValueError):
            resolve_contact(circle(0), circle(1), correction=float("nan"))

    def test_reject_nonfinite_restitution(self):
        with self.assertRaises(ValueError):
            resolve_velocity(circle(0), circle(1), restitution=float("inf"))

    def test_reject_invalid_body(self):
        with self.assertRaises(ValueError):
            Circle("not-a-body", 1)

    def test_reject_invalid_radius(self):
        with self.assertRaises(ValueError):
            Circle(Body2D(Vector2(0, 0), Vector2(0, 0), 1), -1)

    def test_contact_does_not_mutate_inputs(self):
        a, b = circle(0, 1), circle(1.5, -1)
        resolve_contact(a, b)
        self.assertEqual(a.body.position, Vector2(0, 0))
        self.assertEqual(b.body.position, Vector2(1.5, 0))


if __name__ == "__main__":
    unittest.main()
