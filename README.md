# Physics Lab Playground — núcleo matemático Python

Esta branch implementa um núcleo didático **2D em Python**, sem dependências
externas, com vetores imutáveis, integração Newtoniana, colisões circulares e
testes automatizados. O simulador gráfico C++/SFML está sendo desenvolvido em
uma PR separada; **este núcleo ainda não está conectado à interface gráfica**.

## Executar testes

Requer Python 3.11 ou superior:

```bash
python -m unittest discover -v -s tests -p 'test_*.py'
python -m compileall -q src tests
```

O workflow `.github/workflows/python-physics.yml` executa os testes nas
versões 3.11, 3.12 e 3.13.

## Exemplo de uso

```python
from src.physics.vector2 import Vector2
from src.physics.motion import Body2D, step, total_kinetic_energy
from src.physics.collision import Circle, resolve_contact

a = Circle(Body2D(Vector2(0, 0), Vector2(2, 0), 1), radius=1)
b = Circle(Body2D(Vector2(1.5, 0), Vector2(-2, 0), 1), radius=1)
a, b = resolve_contact(a, b, restitution=0.8)
print(a.body.velocity, b.body.velocity)
print(total_kinetic_energy([a.body, b.body]))

moving = step(a.body, Vector2(0, 9.81), 0.01)
print(moving.position)
```

## Componentes

- `vector2.py`: operações geométricas, rotação, produto vetorial,
  interpolação e limitação de magnitude.
- `motion.py`: Euler semi-implícito, arrasto exponencial, avanço em lote,
  momento linear, energia cinética e centro de massa.
- `collision.py`: detecção de contato, impulso com restituição e correção
  de sobreposição proporcional ao inverso das massas.
- `tests/`: regressões de geometria, movimento, conservação e validação.

## Limitações físicas

O método é uma **aproximação educativa**. Não implementa detecção contínua de
colisões, rotação de corpos rígidos, atrito tangencial, restrições ou
estabilização iterativa de múltiplos contatos. Em passos muito grandes, corpos
podem atravessar uns aos outros. Use passos pequenos e consistentes. A energia
cinética pode diminuir em colisões inelásticas ou quando há arrasto; a
conservação de energia só é esperada nos casos elásticos ideais.

Todas as alterações desta branch permanecem em PR separada, sem merge
automático na `main`.
