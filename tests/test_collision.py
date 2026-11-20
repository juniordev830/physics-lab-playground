import unittest
from src.physics.collision import Circle, overlaps, resolve_velocity
from src.physics.motion import Body2D
from src.physics.vector2 import Vector2


def circle(x, vx, mass=1, radius=1):
    return Circle(Body2D(Vector2(x, 0), Vector2(vx, 0), mass), radius)


class CollisionTests(unittest.TestCase):
    def test_overlapping_and_separated(self):
        self.assertTrue(overlaps(circle(0, 0), circle(2, 0)))
        self.assertFalse(overlaps(circle(0, 0), circle(3, 0)))

    def test_elastic_equal_mass_head_on(self):
        left, right = resolve_velocity(circle(0, 1), circle(2, -1))
        self.assertEqual(left.velocity, Vector2(-1, 0))
        self.assertEqual(right.velocity, Vector2(1, 0))

    def test_inelastic_collision(self):
        left, right = resolve_velocity(circle(0, 1), circle(2, -1), 0)
        self.assertEqual(left.velocity, Vector2(0, 0))
        self.assertEqual(right.velocity, Vector2(0, 0))

    def test_moving_apart_no_impulse(self):
        a, b = circle(0, -1), circle(2, 1)
        self.assertEqual(resolve_velocity(a, b), (a.body, b.body))

    def test_invalid_radius_and_restitution(self):
        with self.assertRaises(ValueError):
            circle(0, 0, radius=0)
        with self.assertRaises(ValueError):
            resolve_velocity(circle(0, 0), circle(2, 0), 2)


if __name__ == '__main__':
    unittest.main()
