# Physics Lab Playground

**Status:** MVP gráfico 2D em C++17 e SFML, com gravidade, rebote nas paredes e no chão, e colisões básicas entre bolas.

## Executar no Linux

Instale um compilador C++17, CMake e SFML 2.5 ou superior (série 2.x). No Ubuntu/Debian:

```bash
sudo apt-get install libsfml-dev cmake g++
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
./build/physics-lab
```

### Controles
- **Clique esquerdo:** adiciona uma nova bola.
- **Espaço:** pausa ou retoma a simulação.
- **R:** reinicia com as oito bolas iniciais.
- **Esc:** fecha o aplicativo.

O título da janela mostra a quantidade de partículas e o estado da simulação.

## Testes

```bash
ctest --test-dir build --output-on-failure
```

O workflow GitHub Actions compila o aplicativo com SFML e executa os testes.

## Arquitetura
- `src/physics.hpp`: física independente de qualquer biblioteca gráfica.
- `src/main.cpp`: janela SFML, loop de tempo fixo, eventos e renderização.
- `tests/physics_test.cpp`: testes do motor de colisão e validações.

## Limitações
Simulador **aproximado**, em 2D, com partículas circulares de massa equivalente; não é um motor físico completo. Ainda não há salvamento, reprodução de cenários, colisões com polígonos ou câmera 3D. Exige SFML instalado para abrir a interface gráfica.
