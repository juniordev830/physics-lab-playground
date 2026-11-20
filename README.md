# Physics Lab Playground

## Laboratório gráfico em SFML

**Status:** MVP gráfico 2D em C++17 e **SFML 3**, com gravidade, rebotes nas paredes/chão e colisões básicas entre bolas.

### Executar no Linux

Instale um compilador C++17, CMake e **SFML 3.0 ou superior, série 3.x**. No Ubuntu:

```bash
sudo apt-get install libsfml-dev cmake g++
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
./build/physics-lab
```

O pacote `libsfml-dev` de sua distribuição precisa disponibilizar SFML 3. Caso o pacote seja mais antigo, instale SFML 3 por outra fonte oficial compatível.

#### Controles
- **Clique esquerdo:** adiciona uma nova bola.
- **Espaço:** pausa ou retoma a simulação.
- **R:** reinicia com as oito bolas iniciais e restaura a gravidade padrão.
- **G:** liga ou desliga a gravidade durante a simulação.
- **Esc:** fecha o aplicativo.

O título da janela mostra a quantidade de partículas e o estado da simulação.

### Testes
```bash
ctest --test-dir build --output-on-failure
```

O GitHub Actions compila com SFML 3 e executa os testes de núcleo físico.

### Arquitetura
- `src/physics.hpp`: física independente da biblioteca gráfica.
- `src/main.cpp`: janela SFML, loop fixo, eventos e desenho.
- `tests/physics_test.cpp`: testes de física e validação.

### Limitações
Simulador aproximado, em 2D, com partículas circulares de massa equivalente; não é um motor físico completo. Ainda não há salvamento, reprodução de cenários, colisões com polígonos ou câmera 3D. É necessário ambiente gráfico para visualizar a aplicação.


### Laboratório de gravidade e energia (novo)

Pressione **G** para alternar a gravidade da demonstração entre **600 unidades/s²** e **0**, comparando trajetórias com e sem aceleração vertical. A barra de título exibe a gravidade atual e uma estimativa da **energia cinética somada das partículas**, com massa unitária para cada bola.

A biblioteca `src/physics.hpp` fornece acesso controlado à gravidade e ao cálculo de energia, com testes cobrindo gravidade zero e negativa, entrada inválida e estado vazio. O cálculo é um indicador didático, **não** energia em joules reais nem simulação física de precisão.

## Núcleo Python e planejamento

### Primeira versão

Uma tela 2D de laboratório com chão, um retângulo e uma esfera simulados. O usuário pode soltar objetos de alturas diferentes, pausar a simulação e reiniciar. O foco inicial é a consistência das regras, não renderização realista.

### Contrato físico inicial

- Posição e velocidade atualizadas usando delta de tempo controlado.
- Gravidade constante configurável por cenário.
- Colisão com o chão impede atravessamento evidente.
- Reinício restaura posição, velocidade e tempo.
- Entradas inválidas (massa negativa, dt negativo, NaN ou infinito) são rejeitadas.

### Critérios de aceitação

1. Um corpo largado em repouso acelera para baixo.
2. O mesmo cenário simulado com os mesmos passos gera resultado igual.
3. Pausar congela o estado sem acumular um salto brusco ao retomar.
4. Objeto não atravessa o chão após colisão.
5. Reiniciar permite repetir um experimento com parâmetros iguais.

### Desenvolvimento por etapas

- [ ] Definir unidades, integração numérica e limites de segurança.
- [ ] Implementar simulação pura com testes de movimento e colisão.
- [ ] Adicionar visualizador simples e controle de pausa/tempo.
- [ ] Registrar diferenças entre passo fixo e variável.
- [ ] Testar desempenho e documentação de execução antes de anunciar demo.

Não usar resultados aproximados do jogo como simulação física científica validada.

### Testes do núcleo Python

Modelo 2D de gravidade e colisão com chão, pausa e reinício; integração numérica semi-implícita.

O arquivo `core.py` contém a implementação executável em Python 3.11+ e `tests/test_core.py` cobre regras, entradas inválidas e repetibilidade. O núcleo Python roda de forma independente da versão visual.

Para executar a demonstração:

```bash
python core.py
```

Para verificar o comportamento:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

O GitHub Actions executa a suíte em cada PR. A lista de tarefas do roteiro acima descreve o objetivo completo do jogo e não deve ser interpretada como pronto para publicação.

---

## Núcleo matemático Python 2D

O projeto também oferece um núcleo educativo independente em Python 3.11+, sem dependências externas. Ele complementa o simulador C++/SFML, mas ainda não está conectado à interface gráfica.

## Executar e validar

```bash
python -m compileall -q src tests
python -m unittest discover -v -s tests -p 'test_*.py'
```

O GitHub Actions executa a suíte nas versões Python 3.11, 3.12 e 3.13.
Os testes verificam conservação de momento, restituição, forças, trajetórias,
paredes, validações, limites de recursos e imutabilidade.

## Simular um mundo com gravidade e paredes

```python
from src.physics.collision import Circle
from src.physics.motion import Body2D
from src.physics.vector2 import Vector2
from src.physics.world import (
    Bounds2D, WorldSettings, WorldSnapshot, simulate_world, world_metrics,
)

ball = Circle(Body2D(Vector2(0, 4), Vector2(2, 0), 1), radius=0.5)
initial = WorldSnapshot((ball,))
settings = WorldSettings(
    gravity=Vector2(0, -9.81),
    restitution=0.8,
    bounds=Bounds2D(-10, 0, 10, 10),
)
history = simulate_world(initial, settings, dt=0.01, steps=100, sample_every=10)
final = history[-1]
print(final.time, final.circles[0].body.position)
print(world_metrics(final, settings))
```

O estado é imutável: cada passo retorna um novo `WorldSnapshot`. A ordem de
resolução de contatos é determinística. `contacts` e `wall_hits` indicam
eventos detectados no último passo, não valores acumulados.

## Molas e gravitação entre corpos

```python
from src.physics.forces import SpringLink, UniformField, net_forces
from src.physics.motion import Body2D
from src.physics.vector2 import Vector2

bodies = [
    Body2D(Vector2(0, 0), Vector2(0, 0), 2),
    Body2D(Vector2(3, 0), Vector2(0, 0), 1),
]
forces = net_forces(
    bodies,
    field=UniformField(Vector2(0, -9.81)),
    springs=[SpringLink(0, 1, stiffness=5, rest_length=2, damping=0.5)],
    gravitational_constant=0.1,
    softening=0.1,
)
print(forces)
```

`net_forces` soma gravidade uniforme, molas, gravitação par a par e forças
externas, respeitando pares ação-reação. `total_potential_energy` calcula a
energia potencial conservativa (sem contabilizar perdas por amortecimento).
Em `WorldSettings`, `drag` representa o coeficiente de decaimento
exponencial da velocidade por segundo; em `UniformField`, `linear_drag`
representa força proporcional à velocidade.

## Registrar e analisar uma trajetória

```python
from src.physics.analysis import (
    sample_motion, trajectory_summary, trajectory_csv, crossing_times,
)
from src.physics.motion import Body2D
from src.physics.vector2 import Vector2

initial = Body2D(Vector2(0, 0), Vector2(5, 10), 1)
points = sample_motion(initial, Vector2(0, -9.81), dt=0.01, steps=200)
print(trajectory_summary(points))
print(crossing_times(points, axis="y", level=0, direction="falling"))
csv_text = trajectory_csv(points)
print(csv_text.splitlines()[0])
```

As análises incluem amostragem com força constante ou cronograma de forças,
distância percorrida, deslocamento, velocidade máxima, limites espaciais,
interpolação temporal, cruzamentos, reamostragem e aproximação mínima entre
trajetórias sincronizadas. O CSV contém somente valores numéricos.

## Organização

- `src/physics/vector2.py`: geometria vetorial e operações imutáveis.
- `src/physics/motion.py`: integração, arrasto, momento e energia cinética.
- `src/physics/collision.py`: contatos de círculos e impulsos.
- `src/physics/forces.py`: campos uniformes, molas e gravitação suavizada.
- `src/physics/world.py`: mundo de círculos, limites, simulação e métricas.
- `src/physics/analysis.py`: trajetórias, interpolação e exportação CSV.
- `tests/`: testes unitários de todos os componentes.

## Limites e hipóteses

O motor é uma **aproximação educativa**: não possui detecção contínua de
colisões, rotação de corpos rígidos, atrito tangencial nem restrições rígidas.
Passos grandes podem fazer corpos atravessarem uns aos outros. Contatos
múltiplos são resolvidos iterativamente e podem acumular erros numéricos.
O amortecimento, o arrasto e colisões inelásticas dissipam energia; somente
modelos conservativos ideais permitem esperar conservação aproximada.

Por segurança, o mundo limita a 256 círculos, o cálculo de forças a 512
corpos, e a simulação a 10.000 passos por chamada e 2.000 estados armazenados.
A detecção de contatos e a gravitação par a par têm custo quadrático. O
simulador não pretende substituir bibliotecas físicas de produção.

**Branch de desenvolvimento isolada. Não mesclar na `main` sem autorização.**
