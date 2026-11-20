import unittest
from src.physics.motion import Body2D, step
from src.physics.vector2 import Vector2


class MotionTests(unittest.TestCase):
    def test_constant_velocity(self):
        body = Body2D(Vector2(0, 0), Vector2(2, 3), 1)
        result = step(body, Vector2(0, 0), 2)
        self.assertEqual(result.position, Vector2(4, 6))
        self.assertEqual(result.velocity, Vector2(2, 3))

    def test_acceleration(self):
        body = Body2D(Vector2(0, 0), Vector2(0, 0), 2)
        result = step(body, Vector2(4, 0), 0.5)
        self.assertEqual(result.velocity, Vector2(1, 0))
        self.assertEqual(result.position, Vector2(0.5, 0))

    def test_zero_dt(self):
        body = Body2D(Vector2(1, 2), Vector2(3, 4), 5)
        self.assertEqual(step(body, Vector2(10, 10), 0), body)

    def test_invalid_mass(self):
        for mass in (0, -1, float('inf')):
            with self.subTest(mass=mass), self.assertRaises(ValueError):
                Body2D(Vector2(0, 0), Vector2(0, 0), mass)

    def test_invalid_dt(self):
        body = Body2D(Vector2(0, 0), Vector2(0, 0), 1)
        for dt in (-1, float('nan')):
            with self.subTest(dt=dt), self.assertRaises(ValueError):
                step(body, Vector2(0, 0), dt)


if __name__ == '__main__':
    unittest.main()
