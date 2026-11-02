import random

from src.mcts.agent import mcts


class Competidor:
    def __init__(self, qtd_simulacoes=100, peso_exploracao=1.4):
        self.qtd_simulacoes = qtd_simulacoes
        self.peso_exploracao = peso_exploracao
        self.nome = (f"MCTS_{qtd_simulacoes}simu_{peso_exploracao}peso"
                     if qtd_simulacoes is not None else "Aleatorio")

    def escolher_jogada(self, estado):
        if self.qtd_simulacoes is None:
            return random.choice(estado.jogadas_legais()), 0.0, 0
        return mcts(estado, limite_simulacoes=self.qtd_simulacoes,
                    peso_exploracao=self.peso_exploracao)
