import math
import unittest
from src.physics.vector2 import Vector2


class Vector2Tests(unittest.TestCase):
    def test_add_and_subtract(self):
        self.assertEqual(Vector2(2, 3) + Vector2(4, 5), Vector2(6, 8))
        self.assertEqual(Vector2(4, 5) - Vector2(2, 3), Vector2(2, 2))

    def test_scale_and_dot(self):
        self.assertEqual(2 * Vector2(3, 4), Vector2(6, 8))
        self.assertEqual(Vector2(1, 2).dot(Vector2(3, 4)), 11)

    def test_magnitude_and_normalize(self):
        self.assertEqual(Vector2(3, 4).magnitude(), 5)
        self.assertTrue(math.isclose(Vector2(3, 4).normalized().magnitude(), 1))
        self.assertEqual(Vector2(0, 0).normalized(), Vector2(0, 0))

    def test_reject_non_finite(self):
        with self.assertRaises(ValueError):
            Vector2(float('nan'), 0)


if __name__ == '__main__':
    unittest.main()
