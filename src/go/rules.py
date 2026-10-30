"""Regras e pontuação por área do Go."""

from functools import lru_cache

VAZIO, PRETO, BRANCO = 0, 1, 2
KOMI = {5: 0.5, 7: 4.5, 9: 6.5}


def oponente(cor):
    return BRANCO if cor == PRETO else PRETO


@lru_cache(maxsize=None)
def vizinhos_do_tabuleiro(n):
    """Vizinhos de cada ponto (índice = linha * n + coluna)."""
    viz = []
    for i in range(n):
        for j in range(n):
            v = []
            for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if 0 <= i + di < n and 0 <= j + dj < n:
                    v.append((i + di) * n + (j + dj))
            viz.append(v)
    return viz


def grupo_e_liberdades(tab, p, viz):
    """Flood fill: devolve (pedras do grupo, pontos de liberdade)."""
    cor = tab[p]
    grupo, libs, pilha = set(), set(), [p]
    while pilha:
        q = pilha.pop()
        if q in grupo:
            continue
        grupo.add(q)
        for r in viz[q]:
            if tab[r] == VAZIO:
                libs.add(r)
            elif tab[r] == cor:
                pilha.append(r)
    return grupo, libs


def pontuar(tab, viz):
    """Devolve pedras e território por cor (regiões vazias cercadas por uma cor)."""
    pedras = {PRETO: 0, BRANCO: 0}
    terr = {PRETO: 0, BRANCO: 0}
    visto = set()
    for p in range(len(tab)):
        if tab[p] != VAZIO:
            pedras[tab[p]] += 1
        elif p not in visto:
            regiao, borda, pilha = set(), set(), [p]
            while pilha:
                q = pilha.pop()
                if q in regiao:
                    continue
                regiao.add(q)
                for r in viz[q]:
                    if tab[r] == VAZIO:
                        pilha.append(r)
                    else:
                        borda.add(tab[r])
            visto |= regiao
            if len(borda) == 1:
                terr[next(iter(borda))] += len(regiao)
    return pedras, terr
