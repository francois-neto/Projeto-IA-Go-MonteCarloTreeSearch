"""MCTS: repete seleção, expansão, simulação e retropropagação."""

import math
import random
import time

from src.mcts.node import No


def selecionar(raiz, c):
    """Parte da raiz e desce até um nó que possa ser expandido ou seja folha.

    Enquanto todas as jogadas do nó já foram tentadas, escolhe o filho com
    maior pontuação UCT. A pontuação soma taxa de vitórias e um bônus para
    filhos pouco visitados; `c` controla o peso desse bônus.
    """
    def pontuacao_uct(filho):
        """Calcula a pontuação do filho usando as visitas do nó atual."""
        aproveitamento = filho.vitorias / filho.visitas
        exploracao = c * math.sqrt(log_visitas / filho.visitas)
        return aproveitamento + exploracao

    no = raiz
    while not no.nao_tentadas and no.filhos:
        log_visitas = math.log(no.visitas)
        no = max(no.filhos, key=pontuacao_uct)
    return no


def expandir(no):
    """Escolhe uma jogada não tentada, aplica-a numa cópia e cria um filho.

    Remove a jogada das opções por tentar e devolve o novo nó da árvore.
    """
    jogada = no.nao_tentadas.pop(random.randrange(len(no.nao_tentadas)))
    proximo_estado = no.estado.copia()
    proximo_estado.jogar(jogada)
    filho = No(proximo_estado, no, jogada)
    no.filhos.append(filho)
    return filho


def retropropagar(no, vencedor):
    """Volta do nó simulado até a raiz e atualiza as estatísticas.

    Cada nó recebe uma visita; a vitória é contada apenas quando o vencedor
    é o jogador que fez a jogada que levou àquele nó.
    """
    while no is not None:
        no.visitas += 1
        if vencedor == no.jogador_da_jogada:
            no.vitorias += 1
        no = no.pai


def mcts(estado, segundos, c=1.4):
    """Busca uma jogada repetindo as quatro etapas do MCTS até acabar o tempo.

    1. Seleção: percorre a árvore com UCT até um nó expansível ou uma folha.
    2. Expansão: se houver jogadas não tentadas, acrescenta um filho.
    3. Simulação: joga aleatoriamente a partir de uma cópia desse nó.
    4. Retropropagação: registra o resultado do nó até a raiz.

    Executa ao menos uma simulação, mesmo com tempo zero. Ao final, devolve
    a jogada da raiz mais visitada, sua taxa de vitórias e o total de
    simulações. `c` controla a exploração na etapa de seleção.
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
    melhor = max(raiz.filhos, key=No.numero_de_visitas)
    return melhor.jogada, melhor.vitorias / melhor.visitas, simulacoes
