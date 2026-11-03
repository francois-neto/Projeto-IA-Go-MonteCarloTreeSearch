# Projeto-IA-Go-MonteCarloTreeSearch

Jogo de Go no terminal contra um bot Monte Carlo Tree Search (MCTS). Suporta
tabuleiros 5×5, 7×7 e 9×9, capturas, superko posicional, passes e pontuação
por área com komi. Requer Python 3, sem dependências externas.

```bash
python3 main.py
```

`src/go/rules.py` contém as regras e a pontuação; `src/go/state.py` mantém a
partida e simula jogadas; `src/mcts/` contém a árvore e a busca; `main.py`
contém a interface de terminal.

## Experimentos: 100, 500, 1.000 e 10.000 simulações

```bash
python3 -m src.evaluation.experimento
```

Compara todos os pares: 100 × 500, 500 × 1.000, 100 × 1.000,
1.000 × 10.000, 500 × 10.000 e 100 × 10.000, no tabuleiro 5×5.
São 20 partidas por confronto (10 com cada agente de preto), todas com peso de
exploração 1,4. Mostra vitórias totais e por cor e salva um CSV por confronto
em `experiments/resultados_torneio_V*.csv` após cada confronto.
Os confrontos com 10.000 simulações podem levar dezenas de minutos; o
experimento completo pode levar bastante tempo.
Para mudar a amostra, ajuste
`total_jogos` em `src/evaluation/experimento.py` para outro número par.
Mais simulações **podem** melhorar a taxa de vitórias, mas não garantem vitória:
como as partidas usam aleatoriedade, os resultados podem variar.
