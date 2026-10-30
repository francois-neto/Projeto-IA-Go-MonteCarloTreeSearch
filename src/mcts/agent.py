"""Busca Monte Carlo com seleção UCT."""

import math
import random
import time

from src.mcts.node import No


def mcts(estado, segundos, c=1.4):
    """Devolve (jogada, chance de vitória, número de simulações)."""
    raiz = No(estado.copia())
    fim = time.monotonic() + segundos
    sims = 0
    while sims < 1 or time.monotonic() < fim:
        no = raiz
        while not no.nao_tentadas and no.filhos:
            ln = math.log(no.visitas)
            no = max(no.filhos,
                     key=lambda f: f.vitorias / f.visitas + c * math.sqrt(ln / f.visitas))
        if no.nao_tentadas:
            j = no.nao_tentadas.pop(random.randrange(len(no.nao_tentadas)))
            e = no.estado.copia()
            e.jogar(j)
            filho = No(e, no, j)
            no.filhos.append(filho)
            no = filho
        vencedor = no.estado.copia().simular()
        while no is not None:
            no.visitas += 1
            if vencedor == no.quem:
                no.vitorias += 1
            no = no.pai
        sims += 1
    melhor = max(raiz.filhos, key=lambda f: f.visitas)
    return melhor.jogada, melhor.vitorias / melhor.visitas, sims
