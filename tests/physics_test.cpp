#include "physics.hpp"

#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>

using lab::Ball;
using lab::PhysicsWorld;

static void check(bool condition) {
    if (!condition) throw std::runtime_error("Physics regression check failed");
}

int main() {
    {
        PhysicsWorld world(200, 200, 120);
        world.add_ball({{100, 50}, {0, 0}, 10});
        world.step(.05);
        check(world.balls()[0].velocity.y > 0);
        check(world.balls()[0].position.y > 50);
    }
    {
        PhysicsWorld world(200, 200, 0, .8);
        world.add_ball({{10, 50}, {-100, 0}, 10});
        world.step(.02);
        check(std::abs(world.balls()[0].position.x - 10.0) < 1e-9);
        check(world.balls()[0].velocity.x > 0);
    }
    {
        PhysicsWorld world(200, 200, 0);
        world.add_ball({{100, 190}, {0, 100}, 10});
        world.step(.02);
        check(world.balls()[0].position.y <= 190);
        check(world.balls()[0].velocity.y < 0);
    }
    {
        PhysicsWorld world(300, 300, 0, 1);
        world.add_ball({{100, 100}, {80, 0}, 10});
        world.add_ball({{119, 100}, {-80, 0}, 10});
        world.step(.001);
        check(world.balls()[0].velocity.x < 0);
        check(world.balls()[1].velocity.x > 0);
    }
    {
        PhysicsWorld world(200, 200);
        bool badBall = false, badStep = false;
        try { world.add_ball({{100, 100}, {0, 0}, -1}); }
        catch (const std::invalid_argument&) { badBall = true; }
        try { world.step(-.1); }
        catch (const std::invalid_argument&) { badStep = true; }
        check(badBall && badStep);
    }
    {
        PhysicsWorld world(200, 200, 600);
        world.add_ball({{50, 50}, {3, 4}, 10});
        check(std::abs(world.kinetic_energy() - 12.5) < 1e-9);
        check(std::abs(world.gravity() - 600) < 1e-9);
        world.set_gravity(0);
        world.step(.02);
        check(std::abs(world.balls()[0].velocity.y - 4) < 1e-9);
        check(std::abs(world.kinetic_energy() - 12.5) < 1e-9);
        world.set_gravity(-50);
        world.step(.02);
        check(world.balls()[0].velocity.y < 4);
        world.clear();
        check(world.kinetic_energy() == 0.0);
    }
    {
        PhysicsWorld world(200, 200);
        for (double invalid : {std::numeric_limits<double>::infinity(), 2001.0, -2001.0}) {
            bool rejected = false;
            try { world.set_gravity(invalid); }
            catch (const std::invalid_argument&) { rejected = true; }
            check(rejected);
            check(world.gravity() == 600.0);
        }
    }
    std::cout << "Physics core tests passed" << std::endl;
}
