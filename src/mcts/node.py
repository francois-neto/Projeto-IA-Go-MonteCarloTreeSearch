"""Nó da árvore de busca Monte Carlo."""

from src.go.rules import oponente


class No:
    """Posição da busca e estatísticas da jogada que levou até ela.

    `jogador_da_jogada` é quem acabou de jogar; é para ele que as vitórias
    deste nó são contadas. Na raiz, é o adversário de quem vai começar.
    """

    __slots__ = ("estado", "pai", "jogada", "filhos", "nao_tentadas",
                 "visitas", "vitorias", "jogador_da_jogada")

    def __init__(self, estado, pai=None, jogada=None):
        """Cria um nó; estados finais não têm jogadas para expandir."""
        self.estado = estado
        self.pai = pai
        self.jogada = jogada
        self.filhos = []
        self.nao_tentadas = [] if estado.terminal() else estado.jogadas_legais()
        self.visitas = 0
        self.vitorias = 0
        self.jogador_da_jogada = oponente(estado.vez)

    def numero_de_visitas(self):
        """Devolve quantas vezes este nó foi visitado na busca."""
        return self.visitas
