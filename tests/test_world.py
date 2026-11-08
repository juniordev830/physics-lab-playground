import unittest

from src.physics.collision import Circle
from src.physics.forces import SpringLink
from src.physics.motion import Body2D
from src.physics.vector2 import Vector2
from src.physics.world import (
    Bounds2D, WorldSettings, WorldSnapshot, advance_world,
    contact_pairs, simulate_world, world_metrics,
)


def circle(x=0, vx=0, mass=1, radius=0.5, y=0, vy=0):
    return Circle(Body2D(Vector2(x, y), Vector2(vx, vy), mass), radius)


def world(*circles):
    return WorldSnapshot(tuple(circles))


class WorldValidationTests(unittest.TestCase):
    def test_empty_world_is_valid(self):
        self.assertEqual(world().circles, ())

    def test_reject_list_instead_of_tuple(self):
        with self.assertRaises(ValueError):
            WorldSnapshot([circle()])

    def test_reject_non_circle(self):
        with self.assertRaises(ValueError):
            WorldSnapshot(("not-circle",))

    def test_reject_negative_time(self):
        with self.assertRaises(ValueError):
            WorldSnapshot((), time=-1)

    def test_reject_negative_counters(self):
        with self.assertRaises(ValueError):
            WorldSnapshot((), tick=-1)

    def test_reject_too_many_circles(self):
        with self.assertRaises(ValueError):
            WorldSnapshot((circle(),) * 257)

    def test_invalid_bounds(self):
        for args in ((0, 0, 0, 1), (0, 0, 1, -1), (0, 0, float("nan"), 1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                Bounds2D(*args)

    def test_bounds_fit_diameter(self):
        bounds = Bounds2D(-1, -1, 1, 1)
        self.assertTrue(bounds.fits(1))
        self.assertFalse(bounds.fits(1.1))

    def test_invalid_restitution(self):
        with self.assertRaises(ValueError):
            WorldSettings(restitution=1.1)

    def test_invalid_correction(self):
        with self.assertRaises(ValueError):
            WorldSettings(correction=-0.1)

    def test_invalid_drag(self):
        with self.assertRaises(ValueError):
            WorldSettings(drag=float("inf"))

    def test_invalid_solver_iterations(self):
        for iterations in (0, 17, True, 2.5):
            with self.subTest(iterations=iterations), self.assertRaises(ValueError):
                WorldSettings(solver_iterations=iterations)

    def test_invalid_gravity(self):
        with self.assertRaises(ValueError):
            WorldSettings(gravity=(0, -10))

    def test_invalid_bounds_type(self):
        with self.assertRaises(ValueError):
            WorldSettings(bounds=(0, 0, 1, 1))

    def test_invalid_spring_type(self):
        with self.assertRaises(ValueError):
            WorldSettings(springs=[])


class WorldIntegrationTests(unittest.TestCase):
    def test_empty_world_advances_clock(self):
        result = advance_world(world(), 0.1, WorldSettings())
        self.assertAlmostEqual(result.time, 0.1)
        self.assertEqual(result.tick, 1)

    def test_zero_step_returns_same_snapshot(self):
        initial = world(circle(1, 3))
        self.assertIs(advance_world(initial, 0, WorldSettings()), initial)

    def test_negative_step_rejected(self):
        with self.assertRaises(ValueError):
            advance_world(world(), -1, WorldSettings())

    def test_nonfinite_step_rejected(self):
        with self.assertRaises(ValueError):
            advance_world(world(), float("inf"), WorldSettings())

    def test_constant_velocity(self):
        result = advance_world(world(circle(1, 2)), 0.5, WorldSettings())
        self.assertEqual(result.circles[0].body.position, Vector2(2, 0))

    def test_gravity(self):
        settings = WorldSettings(gravity=Vector2(0, -10))
        result = advance_world(world(circle()), 0.5, settings)
        self.assertEqual(result.circles[0].body.velocity, Vector2(0, -5))
        self.assertEqual(result.circles[0].body.position, Vector2(0, -2.5))

    def test_drag_reduces_speed(self):
        result = advance_world(world(circle(vx=10)), 1, WorldSettings(drag=1))
        self.assertLess(result.circles[0].body.velocity.x, 10)

    def test_external_force(self):
        result = advance_world(
            world(circle(mass=2)), 0.5, WorldSettings(),
            external=[Vector2(4, 0)],
        )
        self.assertEqual(result.circles[0].body.velocity, Vector2(1, 0))

    def test_reject_external_force_length(self):
        with self.assertRaises(ValueError):
            advance_world(world(circle()), 1, WorldSettings(), external=[])

    def test_reject_spring_out_of_range(self):
        settings = WorldSettings(springs=(SpringLink(0, 2, 1, 1),))
        with self.assertRaises(ValueError):
            advance_world(world(circle(), circle(2)), 1, settings)

    def test_spring_pulls_toward_other_body(self):
        settings = WorldSettings(springs=(SpringLink(0, 1, 1, 1),))
        result = advance_world(world(circle(0), circle(3)), 0.1, settings)
        self.assertGreater(result.circles[0].body.velocity.x, 0)
        self.assertLess(result.circles[1].body.velocity.x, 0)

    def test_pair_gravity_is_symmetric(self):
        settings = WorldSettings(gravitational_constant=1, softening=0)
        result = advance_world(world(circle(0), circle(3)), 0.1, settings)
        self.assertAlmostEqual(
            result.circles[0].body.velocity.x,
            -result.circles[1].body.velocity.x,
        )

    def test_elastic_collision_exchanges_velocity(self):
        initial = world(circle(0, 1), circle(1, -1))
        result = advance_world(initial, 0.1, WorldSettings())
        self.assertEqual(result.circles[0].body.velocity, Vector2(-1, 0))
        self.assertEqual(result.circles[1].body.velocity, Vector2(1, 0))
        self.assertEqual(result.contacts, 1)

    def test_inelastic_collision_loses_energy(self):
        initial = world(circle(0, 1), circle(1, -1))
        result = advance_world(initial, 0.1, WorldSettings(restitution=0))
        self.assertEqual(result.circles[0].body.velocity, Vector2(0, 0))
        self.assertEqual(result.circles[1].body.velocity, Vector2(0, 0))

    def test_collision_correction_separates_bodies(self):
        result = advance_world(
            world(circle(0), circle(0.5)), 0.1, WorldSettings(),
        )
        distance = result.circles[0].body.position.distance_to(
            result.circles[1].body.position
        )
        self.assertAlmostEqual(distance, 1)

    def test_contact_pairs(self):
        snapshot = world(circle(0), circle(1), circle(5))
        self.assertEqual(contact_pairs(snapshot), ((0, 1),))

    def test_wall_reflects_right(self):
        settings = WorldSettings(bounds=Bounds2D(-2, -2, 2, 2))
        result = advance_world(world(circle(1, vx=4)), 1, settings)
        self.assertEqual(result.circles[0].body.position.x, 1.5)
        self.assertEqual(result.circles[0].body.velocity.x, -4)
        self.assertEqual(result.wall_hits, 1)

    def test_wall_reflects_bottom(self):
        settings = WorldSettings(bounds=Bounds2D(-2, -2, 2, 2))
        result = advance_world(world(circle(y=-1, vy=-3)), 1, settings)
        self.assertEqual(result.circles[0].body.position.y, -1.5)
        self.assertEqual(result.circles[0].body.velocity.y, 3)

    def test_inelastic_wall_stops_body(self):
        settings = WorldSettings(
            bounds=Bounds2D(-2, -2, 2, 2), restitution=0,
        )
        result = advance_world(world(circle(1, vx=4)), 1, settings)
        self.assertEqual(result.circles[0].body.velocity.x, 0)

    def test_wall_too_small_for_circle(self):
        settings = WorldSettings(bounds=Bounds2D(0, 0, 1, 1))
        with self.assertRaises(ValueError):
            advance_world(world(circle(radius=1)), 0.1, settings)

    def test_inputs_unchanged(self):
        initial = world(circle(0, 1))
        advance_world(initial, 1, WorldSettings())
        self.assertEqual(initial.circles[0].body.position, Vector2(0, 0))


class WorldMetricsTests(unittest.TestCase):
    def test_empty_metrics(self):
        metrics = world_metrics(world(), WorldSettings())
        self.assertEqual(metrics.kinetic_energy, 0)
        self.assertIsNone(metrics.center_of_mass)
        self.assertEqual(metrics.momentum, Vector2(0, 0))

    def test_kinetic_energy_and_momentum(self):
        metrics = world_metrics(world(circle(vx=3, mass=2)), WorldSettings())
        self.assertEqual(metrics.kinetic_energy, 9)
        self.assertEqual(metrics.momentum, Vector2(6, 0))

    def test_uniform_gravity_potential(self):
        metrics = world_metrics(
            world(circle(y=2, mass=3)),
            WorldSettings(gravity=Vector2(0, -10)),
        )
        self.assertEqual(metrics.potential_energy, 60)

    def test_mechanical_energy(self):
        metrics = world_metrics(
            world(circle(vx=2, y=2, mass=2)),
            WorldSettings(gravity=Vector2(0, -10)),
        )
        self.assertEqual(metrics.mechanical_energy, 44)

    def test_center_of_mass(self):
        metrics = world_metrics(
            world(circle(0, mass=3), circle(8, mass=1)), WorldSettings(),
        )
        self.assertEqual(metrics.center_of_mass, Vector2(2, 0))


class WorldHistoryTests(unittest.TestCase):
    def test_zero_steps_contains_initial(self):
        initial = world(circle())
        self.assertEqual(simulate_world(initial, WorldSettings(), 0.1, 0), (initial,))

    def test_records_every_step(self):
        history = simulate_world(world(circle(vx=1)), WorldSettings(), 1, 3)
        self.assertEqual(len(history), 4)
        self.assertEqual([s.tick for s in history], [0, 1, 2, 3])

    def test_stride_includes_final(self):
        history = simulate_world(
            world(circle(vx=1)), WorldSettings(), 1, 5, sample_every=2,
        )
        self.assertEqual([s.tick for s in history], [0, 2, 4, 5])

    def test_force_provider_receives_pre_step_state(self):
        ticks = []
        def provider(snapshot):
            ticks.append(snapshot.tick)
            return [Vector2(1, 0)]
        history = simulate_world(
            world(circle()), WorldSettings(), 1, 3, force_provider=provider,
        )
        self.assertEqual(ticks, [0, 1, 2])
        self.assertEqual(history[-1].circles[0].body.velocity.x, 3)

    def test_reject_too_many_steps(self):
        with self.assertRaises(ValueError):
            simulate_world(world(), WorldSettings(), 1, 10001)

    def test_reject_too_many_snapshots(self):
        with self.assertRaises(ValueError):
            simulate_world(world(), WorldSettings(), 1, 2000)

    def test_sparse_sampling_allows_longer_run(self):
        history = simulate_world(world(), WorldSettings(), 0.01, 3000, sample_every=100)
        self.assertEqual(len(history), 31)

    def test_reject_invalid_sample_interval(self):
        with self.assertRaises(ValueError):
            simulate_world(world(), WorldSettings(), 1, 1, sample_every=0)

    def test_reject_noncallable_force_provider(self):
        with self.assertRaises(ValueError):
            simulate_world(world(), WorldSettings(), 1, 1, force_provider=3)


if __name__ == "__main__":
    unittest.main()
