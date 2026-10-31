"""Estado de uma partida de Go e aplicação das jogadas."""

import random

from src.go.rules import (BRANCO, PRETO, VAZIO, grupo_e_liberdades,
                          oponente, pontuar, vizinhos_do_tabuleiro)


class Estado:
    """Guarda o tabuleiro, a vez e o histórico necessário para validar ko."""

    def __init__(self, n, komi):
        """Inicia um tabuleiro n × n; o preto começa e o komi favorece o branco."""
        self.n = n
        self.komi = komi
        self.viz = vizinhos_do_tabuleiro(n)
        self.tab = [VAZIO] * (n * n)
        self.vez = PRETO
        self.passes = 0
        self.hist = {bytes(self.tab)}  # superko posicional

    def copia(self):
        """Copia tabuleiro e histórico para simular sem alterar a partida original."""
        copia = Estado.__new__(Estado)
        copia.n, copia.komi, copia.viz = self.n, self.komi, self.viz
        copia.tab = self.tab[:]
        copia.vez, copia.passes = self.vez, self.passes
        copia.hist = set(self.hist)
        return copia

    def terminal(self):
        """A partida termina após dois passes consecutivos."""
        return self.passes >= 2

    def _tentar(self, ponto):
        """Testa uma jogada sem alterar o estado.

        Captura grupos adversários sem liberdades antes de verificar suicídio
        e repetição de posição (superko). Devolve (novo tabuleiro, None) se
        legal ou (None, motivo) se ilegal.
        """
        if self.tab[ponto] != VAZIO:
            return None, "posição ocupada"
        adversario = oponente(self.vez)
        novo_tabuleiro = self.tab[:]
        novo_tabuleiro[ponto] = self.vez
        for vizinho in self.viz[ponto]:
            if novo_tabuleiro[vizinho] == adversario:
                grupo, liberdades = grupo_e_liberdades(novo_tabuleiro, vizinho, self.viz)
                if not liberdades:
                    for pedra in grupo:
                        novo_tabuleiro[pedra] = VAZIO
        _, liberdades = grupo_e_liberdades(novo_tabuleiro, ponto, self.viz)
        if not liberdades:
            return None, "suicídio (o grupo ficaria sem liberdades)"
        if bytes(novo_tabuleiro) in self.hist:
            return None, "ko (repetiria uma posição anterior)"
        return novo_tabuleiro, None

    def _aplicar(self, novo_tabuleiro):
        """Confirma uma jogada legal, registra a posição e passa a vez."""
        self.tab = novo_tabuleiro
        self.hist.add(bytes(novo_tabuleiro))
        self.passes = 0
        self.vez = oponente(self.vez)

    def jogar(self, p):
        """Joga no ponto `p` (ou passa com None); devolve motivo se ilegal."""
        if p is None:
            self.passes += 1
            self.vez = oponente(self.vez)
            return None
        novo_tabuleiro, motivo = self._tentar(p)
        if motivo:
            return motivo
        self._aplicar(novo_tabuleiro)
        return None

    def jogadas_legais(self):
        """Lista as jogadas permitidas, incluindo passar (None)."""
        jogadas = [None]
        for ponto in range(len(self.tab)):
            if self.tab[ponto] == VAZIO and self._tentar(ponto)[1] is None:
                jogadas.append(ponto)
        return jogadas

    def _olho_proprio(self, ponto, cor):
        """Evita preencher pontos cercados por pedras da própria cor na simulação."""
        return all(self.tab[vizinho] == cor for vizinho in self.viz[ponto])

    def simular(self):
        """Joga em pontos vazios aleatórios até dois passes ou o limite de turnos.

        Ignora olhos próprios para evitar jogadas inúteis; ao terminar,
        devolve o vencedor pela pontuação atual.
        """
        turnos_restantes = self.n * self.n * 2
        while self.passes < 2 and turnos_restantes > 0:
            turnos_restantes -= 1
            pontos_vazios = [ponto for ponto in range(len(self.tab)) if self.tab[ponto] == VAZIO]
            random.shuffle(pontos_vazios)
            jogou = False
            for ponto in pontos_vazios:
                if self._olho_proprio(ponto, self.vez):
                    continue
                novo_tabuleiro, motivo = self._tentar(ponto)
                if motivo is None:
                    self._aplicar(novo_tabuleiro)
                    jogou = True
                    break
            if not jogou:
                self.jogar(None)
        return self.vencedor()

    def pontuar(self):
        """Devolve as contagens de pedras e de território por cor."""
        return pontuar(self.tab, self.viz)

    def placar(self):
        """Soma pedras e território; adiciona o komi ao branco."""
        pedras, territorio = self.pontuar()
        pretos = pedras[PRETO] + territorio[PRETO]
        brancos = pedras[BRANCO] + territorio[BRANCO] + self.komi
        return pretos, brancos

    def vencedor(self):
        """Devolve a cor com mais pontos; em empate, vence o branco."""
        pretos, brancos = self.placar()
        return PRETO if pretos > brancos else BRANCO
