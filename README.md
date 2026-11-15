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
