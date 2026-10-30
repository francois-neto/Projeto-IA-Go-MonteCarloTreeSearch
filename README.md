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
