#include "physics.hpp"

#include <SFML/Graphics.hpp>
#include <algorithm>
#include <array>
#include <cmath>
#include <optional>
#include <string>

namespace {
constexpr unsigned WIDTH = 1100;
constexpr unsigned HEIGHT = 700;
constexpr double STEP = 1.0 / 120.0;

void populate(lab::PhysicsWorld& world) {
    world.clear();
    for (int i = 0; i < 8; ++i) {
        world.add_ball({{140.0 + i * 94.0, 75.0 + (i % 3) * 48.0},
                        {32.0 + i * 6.0, -15.0}, 18.0 + (i % 4) * 6.0});
    }
}
} // namespace

int main() {
    sf::RenderWindow window(sf::VideoMode({WIDTH, HEIGHT}), "Physics Lab Playground");
    window.setVerticalSyncEnabled(true);
    lab::PhysicsWorld physics(WIDTH, HEIGHT);
    populate(physics);

    sf::Clock clock;
    double accumulator = 0.0;
    bool paused = false;
    unsigned titleFrames = 0;
    const std::array<sf::Color, 6> palette = {
        sf::Color(88, 230, 248), sf::Color(255, 203, 107),
        sf::Color(255, 115, 154), sf::Color(153, 232, 129),
        sf::Color(172, 145, 255), sf::Color(255, 162, 102)
    };

    while (window.isOpen()) {
        while (const std::optional event = window.pollEvent()) {
            if (event->is<sf::Event::Closed>()) {
                window.close();
            }
            if (const auto* key = event->getIf<sf::Event::KeyPressed>()) {
                if (key->code == sf::Keyboard::Key::Escape) window.close();
                if (key->code == sf::Keyboard::Key::Space) paused = !paused;
                if (key->code == sf::Keyboard::Key::R) {
                    populate(physics);
                    paused = false;
                    accumulator = 0.0;
                }
            }
            if (const auto* mouse = event->getIf<sf::Event::MouseButtonPressed>()) {
                if (mouse->button == sf::Mouse::Button::Left && physics.balls().size() < 120) {
                    const double x = mouse->position.x;
                    const double y = mouse->position.y;
                    const double r = 12.0 + (physics.balls().size() % 5) * 5.0;
                    physics.add_ball({{x, y}, {70.0 - r * 3.0, -170.0}, r});
                }
            }
        }

        const double delta = std::min(0.10, static_cast<double>(clock.restart().asSeconds()));
        if (!paused) {
            accumulator += delta;
            while (accumulator >= STEP) {
                physics.step(STEP);
                accumulator -= STEP;
            }
        }

        window.clear(sf::Color(12, 22, 39));
        for (int x = 0; x <= static_cast<int>(WIDTH); x += 50) {
            sf::RectangleShape line({1.0f, static_cast<float>(HEIGHT)});
            line.setPosition({static_cast<float>(x), 0.0f});
            line.setFillColor(sf::Color(40, 63, 78, 95));
            window.draw(line);
        }
        for (int y = 0; y <= static_cast<int>(HEIGHT); y += 50) {
            sf::RectangleShape line({static_cast<float>(WIDTH), 1.0f});
            line.setPosition({0.0f, static_cast<float>(y)});
            line.setFillColor(sf::Color(40, 63, 78, 95));
            window.draw(line);
        }

        const auto& bodies = physics.balls();
        for (std::size_t i = 0; i < bodies.size(); ++i) {
            const auto& ball = bodies[i];
            const float radius = static_cast<float>(ball.radius);
            sf::CircleShape shape(radius, 48);
            shape.setOrigin({radius, radius});
            shape.setPosition({static_cast<float>(ball.position.x), static_cast<float>(ball.position.y)});
            shape.setFillColor(palette[i % palette.size()]);
            shape.setOutlineThickness(2.0f);
            shape.setOutlineColor(sf::Color(222, 250, 255));
            window.draw(shape);
        }
        if (++titleFrames >= 30) {
            window.setTitle("Physics Lab Playground | Particulas: " +
                std::to_string(bodies.size()) + (paused ? " | PAUSADO" : " | SIMULANDO") +
                " | Clique: adicionar | Espaco: pausar | R: reiniciar");
            titleFrames = 0;
        }
        window.display();
    }
    return 0;
}
