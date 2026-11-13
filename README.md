# Physics Lab Playground

Laboratório gráfico de física **planejado** para experimentar gravidade, colisões e objetos interativos.

> **Estado atual:** repositório de concepção, sem engine, simulação, cenas ou testes implementados.

## Primeira versão

Uma tela 2D de laboratório com chão, um retângulo e uma esfera simulados. O usuário pode soltar objetos de alturas diferentes, pausar a simulação e reiniciar. O foco inicial é a consistência das regras, não renderização realista.

## Contrato físico inicial

- Posição e velocidade atualizadas usando delta de tempo controlado.
- Gravidade constante configurável por cenário.
- Colisão com o chão impede atravessamento evidente.
- Reinício restaura posição, velocidade e tempo.
- Entradas inválidas (massa negativa, dt negativo, NaN ou infinito) são rejeitadas.

## Critérios de aceitação

1. Um corpo largado em repouso acelera para baixo.
2. O mesmo cenário simulado com os mesmos passos gera resultado igual.
3. Pausar congela o estado sem acumular um salto brusco ao retomar.
4. Objeto não atravessa o chão após colisão.
5. Reiniciar permite repetir um experimento com parâmetros iguais.

## Desenvolvimento por etapas

- [ ] Definir unidades, integração numérica e limites de segurança.
- [ ] Implementar simulação pura com testes de movimento e colisão.
- [ ] Adicionar visualizador simples e controle de pausa/tempo.
- [ ] Registrar diferenças entre passo fixo e variável.
- [ ] Testar desempenho e documentação de execução antes de anunciar demo.

Não usar resultados aproximados do jogo como simulação física científica validada.

## Primeiro incremento de código (em revisão)

Modelo 2D de gravidade e colisão com chão, pausa e reinício; integração numérica semi-implícita.

O arquivo `core.py` contém a implementação executável em Python 3.11+ e `tests/test_core.py` cobre regras, entradas inválidas e repetibilidade. Não há engine 3D, UI gráfica, asset ou build final nesta entrega; o protótipo é de **domínio/testes**.

Para executar a demonstração:

```bash
python core.py
```

Para verificar o comportamento:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

O GitHub Actions executa a suíte em cada PR. A lista de tarefas do roteiro acima descreve o objetivo completo do jogo e não deve ser interpretada como pronto para publicação.
