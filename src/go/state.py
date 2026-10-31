import random

from src.go.rules import (BRANCO, PRETO, VAZIO, grupo_e_liberdades,
                          oponente, pontuar, vizinhos_do_tabuleiro)


class Estado:
    """Mantém o tabuleiro, a vez, os passes e as posições anteriores."""

    def __init__(self, tamanho, komi):
        """Inicializa uma partida com o tamanho e o komi escolhidos.

        @param tamanho: Número de interseções por lado do tabuleiro.
        @param komi: Pontos extras concedidos às brancas.
        """
        self.tamanho = tamanho
        self.komi = komi
        self._iniciar_partida()

    def _iniciar_partida(self):
        """Regra: as pretas começam e a posição inicial é vazia.

        Implementação: cria o tabuleiro e registra a posição para o superko.
        """
        self.vizinhos = vizinhos_do_tabuleiro(self.tamanho)
        self.tabuleiro = [VAZIO] * (self.tamanho * self.tamanho)
        self.vez = PRETO
        self.passes = 0
        self.historico = {bytes(self.tabuleiro)}

    def copia(self):
        """Copia tabuleiro e histórico para simular sem alterar a partida.

        @return: Novo Estado independente da partida original.
        """
        novo_estado = Estado.__new__(Estado)
        novo_estado.tamanho = self.tamanho
        novo_estado.komi = self.komi
        novo_estado.vizinhos = self.vizinhos
        novo_estado.tabuleiro = self.tabuleiro[:]
        novo_estado.vez = self.vez
        novo_estado.passes = self.passes
        novo_estado.historico = set(self.historico)
        return novo_estado

    def terminal(self):
        """Regra: dois passes consecutivos encerram a partida.

        Implementação: verifica a contagem de passes desde a última pedra.

        @return: True se a partida terminou; caso contrário, False.
        """
        return self.passes >= 2

    def _preparar_jogada(self, ponto):
        """Regra: não se joga sobre pedras, em suicídio nem repetindo posição.

        Implementação: simula a pedra em uma cópia, captura grupos sem
        liberdades e verifica suicídio e superko. Devolve (tabuleiro, None)
        se legal, ou (None, motivo) se ilegal.

        @param ponto: Índice da interseção onde se quer jogar.
        @return: (novo tabuleiro, None) se legal; (None, motivo) se ilegal.
        """
        if self.tabuleiro[ponto] != VAZIO:
            return None, "posição ocupada"
        adversario = oponente(self.vez)
        novo_tabuleiro = self.tabuleiro[:]
        novo_tabuleiro[ponto] = self.vez
        for vizinho in self.vizinhos[ponto]:
            if novo_tabuleiro[vizinho] == adversario:
                resultado_grupo = grupo_e_liberdades(novo_tabuleiro, vizinho, self.vizinhos)
                grupo = resultado_grupo[0]
                liberdades = resultado_grupo[1]
                if not liberdades:
                    for pedra in grupo:
                        novo_tabuleiro[pedra] = VAZIO
        liberdades = grupo_e_liberdades(novo_tabuleiro, ponto, self.vizinhos)[1]
        if not liberdades:
            return None, "suicídio (o grupo ficaria sem liberdades)"
        if bytes(novo_tabuleiro) in self.historico:
            return None, "ko (repetiria uma posição anterior)"
        return novo_tabuleiro, None

    def _confirmar_jogada(self, novo_tabuleiro):
        """Regra: após jogar uma pedra, a vez muda e os passes são zerados.

        Implementação: guarda o tabuleiro legal e sua posição para o superko.

        @param novo_tabuleiro: Tabuleiro resultante de uma jogada legal.
        """
        self.tabuleiro = novo_tabuleiro
        self.historico.add(bytes(novo_tabuleiro))
        self.passes = 0
        self.vez = oponente(self.vez)

    def jogar(self, ponto):
        """Regra: a cada turno, o jogador coloca uma pedra legal ou passa.

        Implementação: registra o passe ou confirma a jogada preparada;
        devolve o motivo quando a jogada é ilegal.

        @param ponto: Índice da interseção, ou None para passar.
        @return: Motivo da ilegalidade, ou None se a jogada foi aceita.
        """
        if ponto is None:
            self.passes += 1
            self.vez = oponente(self.vez)
            return None
        resultado = self._preparar_jogada(ponto)
        novo_tabuleiro = resultado[0]
        motivo = resultado[1]
        if motivo:
            return motivo
        self._confirmar_jogada(novo_tabuleiro)
        return None

    def jogadas_legais(self):
        """Regra: pode-se passar ou colocar uma pedra em uma posição legal.

        Implementação: testa cada interseção vazia sem alterar a partida.

        @return: Lista de pontos legais, incluindo None para passar.
        """
        jogadas = [None]
        for ponto in range(len(self.tabuleiro)):
            if self.tabuleiro[ponto] == VAZIO and self._preparar_jogada(ponto)[1] is None:
                jogadas.append(ponto)
        return jogadas

    def _cercado_pela_propria_cor(self, ponto):
        """Estratégia da simulação: evita pontos cercados pela própria cor.

        Implementação: verifica os vizinhos ortogonais do ponto.

        @param ponto: Índice da interseção examinada.
        @return: True se todos os vizinhos têm a cor do jogador da vez.
        """
        return all(self.tabuleiro[vizinho] == self.vez for vizinho in self.vizinhos[ponto])

    def simular(self):
        """Estratégia do MCTS: completa a partida com jogadas aleatórias.

        Implementação: evita pontos cercados pela própria cor, passa se não
        puder jogar e termina após dois passes ou um limite de turnos.

        @return: Cor vencedora ao fim da simulação.
        """
        turnos_restantes = self.tamanho * self.tamanho * 2
        while self.passes < 2 and turnos_restantes > 0:
            turnos_restantes -= 1
            pontos_vazios = [ponto for ponto in range(len(self.tabuleiro))
                             if self.tabuleiro[ponto] == VAZIO]
            random.shuffle(pontos_vazios)
            encontrou_jogada = False
            for ponto in pontos_vazios:
                if self._cercado_pela_propria_cor(ponto):
                    continue
                resultado = self._preparar_jogada(ponto)
                novo_tabuleiro = resultado[0]
                motivo = resultado[1]
                if motivo is None:
                    self._confirmar_jogada(novo_tabuleiro)
                    encontrou_jogada = True
                    break
            if not encontrou_jogada:
                self.jogar(None)
        return self.vencedor()

    def pontuar(self):
        """Regra: a pontuação por área conta pedras e território.

        Implementação: delega a contagem ao módulo de regras.

        @return: Contagens de pedras e de território por cor.
        """
        return pontuar(self.tabuleiro, self.vizinhos)

    def placar(self):
        """Regra: pedras e território pontuam; as brancas recebem komi.

        Implementação: soma os valores de cada cor e acrescenta o komi.

        @return: Pontos das pretas e das brancas, nessa ordem.
        """
        contagens = self.pontuar()
        pedras = contagens[0]
        territorio = contagens[1]
        pontos_pretos = pedras[PRETO] + territorio[PRETO]
        pontos_brancos = pedras[BRANCO] + territorio[BRANCO] + self.komi
        return pontos_pretos, pontos_brancos

    def vencedor(self):
        """Regra: vence a cor com mais pontos; empate favorece as brancas.

        Implementação: compara os dois valores do placar.

        @return: PRETO ou BRANCO, conforme o resultado.
        """
        placar = self.placar()
        pontos_pretos = placar[0]
        pontos_brancos = placar[1]
        return PRETO if pontos_pretos > pontos_brancos else BRANCO
