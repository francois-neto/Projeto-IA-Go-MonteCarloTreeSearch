"""Nó da árvore de busca Monte Carlo."""

from src.go.rules import oponente


class No:
    __slots__ = ("estado", "pai", "jogada", "filhos", "nao_tentadas",
                 "visitas", "vitorias", "quem")

    def __init__(self, estado, pai=None, jogada=None):
        self.estado = estado
        self.pai = pai
        self.jogada = jogada
        self.filhos = []
        self.nao_tentadas = [] if estado.terminal() else estado.jogadas_legais()
        self.visitas = 0
        self.vitorias = 0
        self.quem = oponente(estado.vez)
