import unittest

from src.physics.forces import (
    SpringLink, UniformField, gravitational_pair_force,
    gravitational_potential_energy, net_forces, spring_pair_force,
    spring_potential_energy, total_potential_energy,
)
from src.physics.motion import Body2D
from src.physics.vector2 import Vector2


def body(x=0, vx=0, mass=1, y=0, vy=0):
    return Body2D(Vector2(x, y), Vector2(vx, vy), mass)


class UniformFieldTests(unittest.TestCase):
    def test_gravity_force_scales_with_mass(self):
        field = UniformField(Vector2(0, -9.8))
        self.assertEqual(field.force_on(body(mass=2)), Vector2(0, -19.6))

    def test_drag_opposes_velocity(self):
        field = UniformField(Vector2(0, 0), linear_drag=3)
        self.assertEqual(field.force_on(body(vx=4, vy=-2)), Vector2(-12, 6))

    def test_field_combines_gravity_and_drag(self):
        field = UniformField(Vector2(0, -10), linear_drag=2)
        self.assertEqual(field.force_on(body(vx=3, mass=2)), Vector2(-6, -20))

    def test_uniform_potential(self):
        field = UniformField(Vector2(0, -10))
        self.assertEqual(field.potential_energy(body(y=3, mass=2)), 60)

    def test_zero_field(self):
        self.assertEqual(UniformField(Vector2(0, 0)).force_on(body()), Vector2(0, 0))

    def test_reject_invalid_field(self):
        with self.assertRaises(ValueError):
            UniformField("down")
        for drag in (-1, float("nan"), float("inf")):
            with self.subTest(drag=drag), self.assertRaises(ValueError):
                UniformField(Vector2(0, 0), drag)

    def test_reject_invalid_body(self):
        with self.assertRaises(ValueError):
            UniformField(Vector2(0, 0)).force_on("body")
        with self.assertRaises(ValueError):
            UniformField(Vector2(0, 0)).potential_energy(None)


class SpringTests(unittest.TestCase):
    def test_rest_length_has_zero_force(self):
        self.assertEqual(spring_pair_force(body(0), body(2), 5, 2), Vector2(0, 0))

    def test_stretched_spring_attracts(self):
        self.assertEqual(spring_pair_force(body(0), body(3), 5, 2), Vector2(5, 0))

    def test_compressed_spring_repels(self):
        self.assertEqual(spring_pair_force(body(0), body(1), 5, 2), Vector2(-5, 0))

    def test_damping_resists_separation(self):
        self.assertEqual(
            spring_pair_force(body(0), body(2, vx=3), 0, 2, 2),
            Vector2(6, 0),
        )

    def test_damping_resists_approach(self):
        self.assertEqual(
            spring_pair_force(body(0), body(2, vx=-3), 0, 2, 2),
            Vector2(-6, 0),
        )

    def test_coincident_centers_have_deterministic_normal(self):
        self.assertEqual(spring_pair_force(body(0), body(0), 2, 1), Vector2(-2, 0))

    def test_coincident_centers_follow_relative_velocity(self):
        self.assertEqual(
            spring_pair_force(body(0), body(0, vy=1), 2, 1),
            Vector2(0, -2),
        )

    def test_potential_energy_at_rest(self):
        self.assertEqual(spring_potential_energy(body(0), body(2), 8, 2), 0)

    def test_potential_energy_extension(self):
        self.assertEqual(spring_potential_energy(body(0), body(4), 8, 2), 16)

    def test_invalid_spring_indices(self):
        for pair in ((-1, 0), (1, 1), (True, 1), (0, 1.5)):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                SpringLink(*pair, 1, 1)

    def test_invalid_spring_coefficients(self):
        for kwargs in (
            dict(stiffness=-1, rest_length=1),
            dict(stiffness=1, rest_length=-1),
            dict(stiffness=1, rest_length=1, damping=float("inf")),
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                SpringLink(0, 1, **kwargs)

    def test_invalid_spring_force_arguments(self):
        with self.assertRaises(ValueError):
            spring_pair_force(body(), body(2), -1, 1)
        with self.assertRaises(ValueError):
            spring_potential_energy(body(), body(2), 1, float("nan"))


class GravityTests(unittest.TestCase):
    def test_inverse_square_attraction(self):
        self.assertEqual(
            gravitational_pair_force(body(0, mass=2), body(2, mass=3), 1),
            Vector2(1.5, 0),
        )

    def test_gravity_points_toward_second_body(self):
        self.assertEqual(
            gravitational_pair_force(body(0, y=2), body(0, y=0), 1),
            Vector2(0, -0.25),
        )

    def test_zero_gravity(self):
        self.assertEqual(gravitational_pair_force(body(), body(2), 0), Vector2(0, 0))

    def test_coincident_centers_no_force(self):
        self.assertEqual(gravitational_pair_force(body(), body(), 1), Vector2(0, 0))

    def test_softened_gravity_is_weaker(self):
        a, b = body(0), body(2)
        self.assertLess(
            gravitational_pair_force(a, b, 1, softening=1).magnitude(),
            gravitational_pair_force(a, b, 1).magnitude(),
        )

    def test_gravitational_potential(self):
        self.assertEqual(
            gravitational_potential_energy(body(0, mass=2), body(2, mass=3), 1),
            -3,
        )

    def test_softened_coincident_potential(self):
        self.assertEqual(
            gravitational_potential_energy(body(), body(), 2, softening=1), -2,
        )

    def test_unsoftened_coincident_potential_rejected(self):
        with self.assertRaises(ValueError):
            gravitational_potential_energy(body(), body(), 1)

    def test_zero_constant_coincident_potential(self):
        self.assertEqual(gravitational_potential_energy(body(), body(), 0), 0)

    def test_invalid_gravity_values(self):
        for constant, softening in ((-1, 0), (1, -1), (float("nan"), 0)):
            with self.subTest(constant=constant, softening=softening):
                with self.assertRaises(ValueError):
                    gravitational_pair_force(body(), body(2), constant, softening)


class NetForceTests(unittest.TestCase):
    def test_empty_world(self):
        self.assertEqual(net_forces([]), [])

    def test_external_forces_preserve_order(self):
        forces = [Vector2(1, 0), Vector2(0, 2)]
        self.assertEqual(net_forces([body(), body(2)], external=forces), forces)

    def test_spring_forces_cancel(self):
        forces = net_forces(
            [body(0), body(3)], springs=[SpringLink(0, 1, 5, 2)],
        )
        self.assertEqual(forces, [Vector2(5, 0), Vector2(-5, 0)])

    def test_gravity_forces_cancel(self):
        forces = net_forces([body(0), body(2)], gravitational_constant=1)
        self.assertEqual(forces, [Vector2(0.25, 0), Vector2(-0.25, 0)])

    def test_combined_field_and_external(self):
        forces = net_forces(
            [body(mass=2)], field=UniformField(Vector2(0, -10)),
            external=[Vector2(5, 0)],
        )
        self.assertEqual(forces, [Vector2(5, -20)])

    def test_multiple_links_accumulate(self):
        forces = net_forces(
            [body(0), body(2), body(4)],
            springs=[SpringLink(0, 1, 2, 1), SpringLink(1, 2, 2, 1)],
        )
        self.assertEqual(forces, [Vector2(2, 0), Vector2(0, 0), Vector2(-2, 0)])

    def test_total_potential_combines_field_and_spring(self):
        bodies = [body(0, y=2, mass=2), body(4)]
        self.assertEqual(
            total_potential_energy(
                bodies, field=UniformField(Vector2(0, -10)),
                springs=[SpringLink(0, 1, 2, 0)],
            ),
            40 + 0.5 * 2 * 20,
        )

    def test_total_potential_zero_empty(self):
        self.assertEqual(total_potential_energy([]), 0)

    def test_reject_mismatched_external_forces(self):
        with self.assertRaises(ValueError):
            net_forces([body()], external=[])

    def test_reject_nonvector_external_force(self):
        with self.assertRaises(ValueError):
            net_forces([body()], external=["bad"])

    def test_reject_out_of_bounds_spring(self):
        with self.assertRaises(ValueError):
            net_forces([body()], springs=[SpringLink(0, 1, 1, 1)])

    def test_reject_invalid_field(self):
        with self.assertRaises(ValueError):
            net_forces([body()], field="gravity")

    def test_reject_invalid_body(self):
        with self.assertRaises(ValueError):
            net_forces(["body"])

    def test_reject_too_many_bodies(self):
        with self.assertRaises(ValueError):
            net_forces([body()] * 513)

    def test_input_bodies_not_mutated(self):
        bodies = [body(0), body(2)]
        net_forces(bodies, gravitational_constant=1)
        self.assertEqual(bodies, [body(0), body(2)])


if __name__ == "__main__":
    unittest.main()
