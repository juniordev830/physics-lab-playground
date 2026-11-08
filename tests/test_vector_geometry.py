import math
import unittest

from src.physics.vector2 import Vector2


class VectorGeometryTests(unittest.TestCase):
    def test_negation(self):
        self.assertEqual(-Vector2(3, -4), Vector2(-3, 4))

    def test_division(self):
        self.assertEqual(Vector2(8, 4) / 2, Vector2(4, 2))

    def test_reject_zero_division(self):
        with self.assertRaises(ValueError):
            Vector2(1, 2) / 0

    def test_reject_nonfinite_division(self):
        for value in (float("inf"), float("nan")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Vector2(1, 2) / value

    def test_reject_nonfinite_scale(self):
        with self.assertRaises(ValueError):
            Vector2(1, 2) * float("inf")

    def test_cross_product_sign(self):
        self.assertEqual(Vector2(1, 0).cross(Vector2(0, 1)), 1)
        self.assertEqual(Vector2(0, 1).cross(Vector2(1, 0)), -1)

    def test_cross_parallel_vectors(self):
        self.assertEqual(Vector2(2, 4).cross(Vector2(3, 6)), 0)

    def test_magnitude_squared(self):
        self.assertEqual(Vector2(3, 4).magnitude_squared(), 25)

    def test_distance_is_symmetric(self):
        a, b = Vector2(1, 2), Vector2(4, 6)
        self.assertEqual(a.distance_to(b), 5)
        self.assertEqual(a.distance_to(b), b.distance_to(a))

    def test_perpendicular(self):
        vector = Vector2(3, 4)
        self.assertEqual(vector.perpendicular(), Vector2(-4, 3))
        self.assertEqual(vector.dot(vector.perpendicular()), 0)

    def test_rotate_ninety_degrees(self):
        result = Vector2(2, 0).rotated(math.pi / 2)
        self.assertAlmostEqual(result.x, 0, places=10)
        self.assertAlmostEqual(result.y, 2, places=10)

    def test_rotate_full_circle(self):
        result = Vector2(3, 4).rotated(2 * math.pi)
        self.assertAlmostEqual(result.x, 3)
        self.assertAlmostEqual(result.y, 4)

    def test_reject_nonfinite_rotation(self):
        with self.assertRaises(ValueError):
            Vector2(1, 0).rotated(float("nan"))

    def test_clamp_large_vector(self):
        result = Vector2(6, 8).clamp_magnitude(5)
        self.assertAlmostEqual(result.magnitude(), 5)
        self.assertAlmostEqual(result.x, 3)
        self.assertAlmostEqual(result.y, 4)

    def test_clamp_short_vector_preserves_identity(self):
        vector = Vector2(3, 4)
        self.assertIs(vector.clamp_magnitude(5), vector)

    def test_clamp_zero_maximum(self):
        self.assertEqual(Vector2(1, 2).clamp_magnitude(0), Vector2(0, 0))

    def test_clamp_zero_vector(self):
        self.assertEqual(Vector2(0, 0).clamp_magnitude(3), Vector2(0, 0))

    def test_reject_negative_maximum(self):
        with self.assertRaises(ValueError):
            Vector2(1, 2).clamp_magnitude(-1)

    def test_lerp_endpoints(self):
        a, b = Vector2(1, 2), Vector2(5, 6)
        self.assertEqual(a.lerp(b, 0), a)
        self.assertEqual(a.lerp(b, 1), b)

    def test_lerp_midpoint(self):
        self.assertEqual(Vector2(0, 0).lerp(Vector2(10, 20), 0.5), Vector2(5, 10))

    def test_reject_lerp_extrapolation(self):
        for fraction in (-0.1, 1.1, float("nan")):
            with self.subTest(fraction=fraction), self.assertRaises(ValueError):
                Vector2(0, 0).lerp(Vector2(1, 1), fraction)

    def test_normalization_preserves_direction(self):
        vector = Vector2(6, 8).normalized()
        self.assertAlmostEqual(vector.x, 0.6)
        self.assertAlmostEqual(vector.y, 0.8)

    def test_original_vector_is_unchanged(self):
        vector = Vector2(3, 4)
        vector.rotated(0.5).clamp_magnitude(2)
        self.assertEqual(vector, Vector2(3, 4))


if __name__ == "__main__":
    unittest.main()
