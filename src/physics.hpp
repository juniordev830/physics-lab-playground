#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <stdexcept>
#include <vector>

namespace lab {

struct Vec2 {
    double x = 0;
    double y = 0;
};

struct Ball {
    Vec2 position;
    Vec2 velocity;
    double radius = 10.0;
};

class PhysicsWorld {
public:
    explicit PhysicsWorld(double width, double height, double gravity = 600.0, double restitution = 0.82)
        : width_(width), height_(height), gravity_(gravity), restitution_(restitution) {
        if (!std::isfinite(width) || !std::isfinite(height) || width <= 0 || height <= 0 ||
            !std::isfinite(gravity) || !std::isfinite(restitution) ||
            restitution < 0 || restitution > 1)
            throw std::invalid_argument("Invalid world dimensions or physics settings");
    }

    void add_ball(Ball ball) {
        if (!std::isfinite(ball.radius) || ball.radius <= 0 ||
            ball.radius * 2 > width_ || ball.radius * 2 > height_ ||
            !std::isfinite(ball.position.x) || !std::isfinite(ball.position.y) ||
            !std::isfinite(ball.velocity.x) || !std::isfinite(ball.velocity.y) ||
            balls_.size() >= 120)
            throw std::invalid_argument("Invalid or excessive ball");
        ball.position.x = std::clamp(ball.position.x, ball.radius, width_ - ball.radius);
        ball.position.y = std::clamp(ball.position.y, ball.radius, height_ - ball.radius);
        balls_.push_back(ball);
    }

    // Adjustable gravity keeps the simulation responsive to live UI controls.
    void set_gravity(double value) {
        if (!std::isfinite(value) || value < -2000.0 || value > 2000.0)
            throw std::invalid_argument("Gravity must be finite and between -2000 and 2000");
        gravity_ = value;
    }

    double gravity() const { return gravity_; }

    // Unit-mass kinetic energy diagnostic: illustrative, not measured joules.
    double kinetic_energy() const {
        double total = 0.0;
        for (const auto& ball : balls_)
            total += 0.5 * (ball.velocity.x * ball.velocity.x +
                            ball.velocity.y * ball.velocity.y);
        return total;
    }

    void clear() { balls_.clear(); }
    const std::vector<Ball>& balls() const { return balls_; }

    void step(double dt) {
        if (!std::isfinite(dt) || dt < 0 || dt > 0.05)
            throw std::invalid_argument("Step must be between zero and 50 ms");
        for (auto& ball : balls_) {
            ball.velocity.y += gravity_ * dt;
            ball.position.x += ball.velocity.x * dt;
            ball.position.y += ball.velocity.y * dt;
            if (ball.position.x < ball.radius) {
                ball.position.x = ball.radius;
                ball.velocity.x = std::abs(ball.velocity.x) * restitution_;
            } else if (ball.position.x > width_ - ball.radius) {
                ball.position.x = width_ - ball.radius;
                ball.velocity.x = -std::abs(ball.velocity.x) * restitution_;
            }
            if (ball.position.y < ball.radius) {
                ball.position.y = ball.radius;
                ball.velocity.y = std::abs(ball.velocity.y) * restitution_;
            } else if (ball.position.y > height_ - ball.radius) {
                ball.position.y = height_ - ball.radius;
                ball.velocity.y = -std::abs(ball.velocity.y) * restitution_;
            }
        }

        // Approximate, equal-mass pair collisions: suitable for a small demo, not a physics engine.
        for (std::size_t i = 0; i < balls_.size(); ++i) {
            for (std::size_t j = i + 1; j < balls_.size(); ++j) {
                auto& a = balls_[i];
                auto& b = balls_[j];
                const double dx = b.position.x - a.position.x;
                const double dy = b.position.y - a.position.y;
                const double d2 = dx * dx + dy * dy;
                const double needed = a.radius + b.radius;
                if (d2 >= needed * needed) continue;
                const double distance = std::sqrt(d2);
                const double nx = distance > 1e-9 ? dx / distance : 1.0;
                const double ny = distance > 1e-9 ? dy / distance : 0.0;
                const double overlap = (needed - distance) * 0.5;
                a.position.x -= nx * overlap;
                a.position.y -= ny * overlap;
                b.position.x += nx * overlap;
                b.position.y += ny * overlap;
                const double closing = (b.velocity.x - a.velocity.x) * nx +
                                       (b.velocity.y - a.velocity.y) * ny;
                if (closing < 0) {
                    const double impulse = -(1.0 + restitution_) * closing * 0.5;
                    a.velocity.x -= impulse * nx;
                    a.velocity.y -= impulse * ny;
                    b.velocity.x += impulse * nx;
                    b.velocity.y += impulse * ny;
                }
            }
        }
    }

private:
    double width_;
    double height_;
    double gravity_;
    double restitution_;
    std::vector<Ball> balls_;
};

} // namespace lab
