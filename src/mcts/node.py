from src.go.rules import oponente


class No:
    """Nó da busca: guarda estado, pai, jogada, filhos e estatísticas.

    Inicia com as jogadas legais por tentar (nenhuma se o estado for final).
    Conta vitórias para quem fez a jogada; na raiz, para o adversário da vez.
    """

    def __init__(self, estado, pai=None, jogada=None):
        """Inicializa o nó da busca.

        @param estado: Estado do jogo representado pelo nó.
        @param pai: Nó anterior na árvore; None na raiz.
        @param jogada: Jogada que levou ao nó; None na raiz ou após um passe.
        """
        self.estado = estado
        self.pai = pai
        self.jogada = jogada
        self.filhos = []
        self.nao_tentadas = self._jogadas_nao_tentadas()
        self.visitas = 0
        self.vitorias = 0
        self.jogador_da_jogada = self._determinar_jogador_da_jogada()

    def _determinar_jogador_da_jogada(self):
        """Identifica quem fez a jogada anterior à posição deste nó.

        @return: Adversário do jogador da vez no estado do nó.
        """
        return oponente(self.estado.vez)

    def _jogadas_nao_tentadas(self):
        """Lista as jogadas ainda disponíveis para expansão.

        @return: Jogadas legais, ou lista vazia se o estado for terminal.
        """
        if self.estado.terminal():
            return []
        return self.estado.jogadas_legais()

    def numero_de_visitas(self):
        """Devolve o total de visitas ao nó.

        @return: Número de visitas recebidas na busca.
        """
        return self.visitas
