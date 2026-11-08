# Physics Lab Playground — núcleo matemático Python

Esta branch implementa um laboratório **2D em Python 3.11+**, sem dependências
externas, com vetores imutáveis, movimento Newtoniano, colisões circulares,
forças compostas, simulação em etapas e análise de trajetórias. O simulador
gráfico C++/SFML está em outra PR; **o núcleo Python não está integrado à UI**.

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
