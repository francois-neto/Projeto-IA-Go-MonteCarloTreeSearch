"""Estado de uma partida de Go e aplicação das jogadas."""

import random

from src.go.rules import (BRANCO, PRETO, VAZIO, grupo_e_liberdades,
                          oponente, pontuar, vizinhos_do_tabuleiro)


class Estado:
    def __init__(self, n, komi):
        self.n = n
        self.komi = komi
        self.viz = vizinhos_do_tabuleiro(n)
        self.tab = [VAZIO] * (n * n)
        self.vez = PRETO
        self.passes = 0
        self.hist = {bytes(self.tab)}  # superko posicional

    def copia(self):
        e = Estado.__new__(Estado)
        e.n, e.komi, e.viz = self.n, self.komi, self.viz
        e.tab = self.tab[:]
        e.vez, e.passes = self.vez, self.passes
        e.hist = set(self.hist)
        return e

    def terminal(self):
        return self.passes >= 2

    def _tentar(self, p):
        """Testa uma jogada sem alterar o estado: (tabuleiro, motivo)."""
        if self.tab[p] != VAZIO:
            return None, "posição ocupada"
        cor, adv = self.vez, oponente(self.vez)
        novo = self.tab[:]
        novo[p] = cor
        for q in self.viz[p]:
            if novo[q] == adv:
                grupo, libs = grupo_e_liberdades(novo, q, self.viz)
                if not libs:
                    for g in grupo:
                        novo[g] = VAZIO
        _, libs = grupo_e_liberdades(novo, p, self.viz)
        if not libs:
            return None, "suicídio (o grupo ficaria sem liberdades)"
        if bytes(novo) in self.hist:
            return None, "ko (repetiria uma posição anterior)"
        return novo, None

    def _aplicar(self, novo):
        self.tab = novo
        self.hist.add(bytes(novo))
        self.passes = 0
        self.vez = oponente(self.vez)

    def jogar(self, p):
        """p = índice do ponto ou None para passar; devolve motivo se ilegal."""
        if p is None:
            self.passes += 1
            self.vez = oponente(self.vez)
            return None
        novo, motivo = self._tentar(p)
        if motivo:
            return motivo
        self._aplicar(novo)
        return None

    def jogadas_legais(self):
        res = [None]  # passar é sempre legal
        for p in range(len(self.tab)):
            if self.tab[p] == VAZIO and self._tentar(p)[1] is None:
                res.append(p)
        return res

    def _olho_proprio(self, p, cor):
        return all(self.tab[q] == cor for q in self.viz[p])

    def simular(self):
        """Joga aleatoriamente até o fim e devolve o vencedor."""
        limite = self.n * self.n * 2
        while self.passes < 2 and limite > 0:
            limite -= 1
            vazios = [p for p in range(len(self.tab)) if self.tab[p] == VAZIO]
            random.shuffle(vazios)
            jogou = False
            for p in vazios:
                if self._olho_proprio(p, self.vez):
                    continue
                novo, motivo = self._tentar(p)
                if motivo is None:
                    self._aplicar(novo)
                    jogou = True
                    break
            if not jogou:
                self.jogar(None)
        return self.vencedor()

    def pontuar(self):
        return pontuar(self.tab, self.viz)

    def placar(self):
        pedras, terr = self.pontuar()
        pretos = pedras[PRETO] + terr[PRETO]
        brancos = pedras[BRANCO] + terr[BRANCO] + self.komi
        return pretos, brancos

    def vencedor(self):
        pretos, brancos = self.placar()
        return PRETO if pretos > brancos else BRANCO
