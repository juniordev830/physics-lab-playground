#include "physics.hpp"

#include <SFML/Graphics.hpp>
#include <algorithm>
#include <array>
#include <cmath>
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
    sf::RenderWindow window(sf::VideoMode(WIDTH, HEIGHT), "Physics Lab Playground");
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
        sf::Event event{};
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) window.close();
            if (event.type == sf::Event::KeyPressed && !event.key.repeat) {
                if (event.key.code == sf::Keyboard::Escape) window.close();
                if (event.key.code == sf::Keyboard::Space) paused = !paused;
                if (event.key.code == sf::Keyboard::R) {
                    populate(physics);
                    paused = false;
                    accumulator = 0.0;
                }
            }
            if (event.type == sf::Event::MouseButtonPressed &&
                event.mouseButton.button == sf::Mouse::Left && physics.balls().size() < 120) {
                const double x = event.mouseButton.x;
                const double y = event.mouseButton.y;
                const double r = 12.0 + (physics.balls().size() % 5) * 5.0;
                physics.add_ball({{x, y}, {70.0 - r * 3.0, -170.0}, r});
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
        sf::VertexArray grid(sf::Lines);
        for (int x = 0; x <= static_cast<int>(WIDTH); x += 50) {
            const sf::Color c(40, 63, 78, 95);
            grid.append(sf::Vertex(sf::Vector2f(static_cast<float>(x), 0), c));
            grid.append(sf::Vertex(sf::Vector2f(static_cast<float>(x), HEIGHT), c));
        }
        for (int y = 0; y <= static_cast<int>(HEIGHT); y += 50) {
            const sf::Color c(40, 63, 78, 95);
            grid.append(sf::Vertex(sf::Vector2f(0, static_cast<float>(y)), c));
            grid.append(sf::Vertex(sf::Vector2f(WIDTH, static_cast<float>(y)), c));
        }
        window.draw(grid);

        const auto& bodies = physics.balls();
        for (std::size_t i = 0; i < bodies.size(); ++i) {
            const auto& ball = bodies[i];
            sf::CircleShape shape(static_cast<float>(ball.radius), 48);
            shape.setOrigin(static_cast<float>(ball.radius), static_cast<float>(ball.radius));
            shape.setPosition(static_cast<float>(ball.position.x), static_cast<float>(ball.position.y));
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
