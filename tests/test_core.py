import unittest
from math import nan
from core import Body, World


class PhysicsTests(unittest.TestCase):
    def test_falling_is_deterministic(self):
        one = World(Body(0, 5))
        two = World(Body(0, 5))
        for _ in range(40):
            one.step(0.02)
            two.step(0.02)
        self.assertEqual(one.body, two.body)
        self.assertLess(one.body.y, 5)

    def test_ground_collision(self):
        world = World(Body(0, 0.1))
        for _ in range(30):
            world.step(0.02)
        self.assertEqual(world.body.y, 0)
        self.assertEqual(world.body.vy, 0)

    def test_pause_and_reset(self):
        world = World(Body(0, 2))
        world.pause()
        self.assertEqual(world.step(0.1).y, 2)
        self.assertEqual(world.time, 0)
        world.pause(False)
        world.step(0.1)
        world.reset()
        self.assertEqual(world.body, Body(0, 2))
        self.assertEqual(world.time, 0)

    def test_invalid_inputs_do_not_advance(self):
        world = World(Body(0, 1))
        for bad in (-1, 0, nan, float("inf"), 1):
            with self.assertRaises(ValueError):
                world.step(bad)
        self.assertEqual(world.time, 0)
        with self.assertRaises(ValueError):
            Body(0, 1, mass=-1)


if __name__ == "__main__":
    unittest.main()
