# Physics Lab Playground

**Status:** MVP gráfico 2D em C++17 e **SFML 3**, com gravidade, rebotes nas paredes/chão e colisões básicas entre bolas.

## Executar no Linux

Instale um compilador C++17, CMake e **SFML 3.0 ou superior, série 3.x**. No Ubuntu:

```bash
sudo apt-get install libsfml-dev cmake g++
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
./build/physics-lab
```

O pacote `libsfml-dev` de sua distribuição precisa disponibilizar SFML 3. Caso o pacote seja mais antigo, instale SFML 3 por outra fonte oficial compatível.

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

O GitHub Actions compila com SFML 3 e executa os testes de núcleo físico.

## Arquitetura
- `src/physics.hpp`: física independente da biblioteca gráfica.
- `src/main.cpp`: janela SFML, loop fixo, eventos e desenho.
- `tests/physics_test.cpp`: testes de física e validação.

## Limitações
Simulador aproximado, em 2D, com partículas circulares de massa equivalente; não é um motor físico completo. Ainda não há salvamento, reprodução de cenários, colisões com polígonos ou câmera 3D. É necessário ambiente gráfico para visualizar a aplicação.
