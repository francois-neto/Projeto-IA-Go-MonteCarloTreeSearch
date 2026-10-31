"""Busca Monte Carlo com seleção UCT."""

import math
import random
import time

from src.mcts.node import No


def selecionar(raiz, c):
    """Desce pela árvore usando UCT até achar jogadas não tentadas ou uma folha.

    UCT equilibra a taxa de vitórias com a exploração de filhos pouco visitados;
    quanto maior `c`, maior o peso da exploração.
    """
    no = raiz
    while not no.nao_tentadas and no.filhos:
        log_visitas = math.log(no.visitas)
        no = max(
            no.filhos,
            key=lambda filho: filho.vitorias / filho.visitas
            + c * math.sqrt(log_visitas / filho.visitas),
        )
    return no


def expandir(no):
    """Experimenta uma jogada ainda não tentada e devolve o novo filho."""
    jogada = no.nao_tentadas.pop(random.randrange(len(no.nao_tentadas)))
    proximo_estado = no.estado.copia()
    proximo_estado.jogar(jogada)
    filho = No(proximo_estado, no, jogada)
    no.filhos.append(filho)
    return filho


def retropropagar(no, vencedor):
    """Atualiza os nós até a raiz com o resultado da simulação.

    Cada nó conta vitórias para quem fez a jogada que levou até ele.
    """
    while no is not None:
        no.visitas += 1
        if vencedor == no.jogador_da_jogada:
            no.vitorias += 1
        no = no.pai


def mcts(estado, segundos, c=1.4):
    """Busca uma jogada por seleção, expansão, simulação e retropropagação.

    Executa ao menos uma simulação, mesmo com tempo zero. Devolve a jogada
    mais visitada, sua taxa de vitórias para o jogador da vez e o total de
    simulações. `c` controla o peso da exploração na seleção UCT.
    """
    raiz = No(estado.copia())
    prazo = time.monotonic() + segundos
    simulacoes = 0
    while simulacoes < 1 or time.monotonic() < prazo:
        no = selecionar(raiz, c)
        if no.nao_tentadas:
            no = expandir(no)
        vencedor = no.estado.copia().simular()
        retropropagar(no, vencedor)
        simulacoes += 1
    melhor = max(raiz.filhos, key=lambda filho: filho.visitas)
    return melhor.jogada, melhor.vitorias / melhor.visitas, simulacoes
