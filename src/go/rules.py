"""Regras e pontuação por área do Go."""

from functools import lru_cache

VAZIO, PRETO, BRANCO = 0, 1, 2
KOMI = {5: 0.5, 7: 4.5, 9: 6.5}


def oponente(cor):
    """Devolve a outra cor jogável."""
    return BRANCO if cor == PRETO else PRETO


@lru_cache(maxsize=None)
def vizinhos_do_tabuleiro(n):
    """Lista os vizinhos ortogonais de cada ponto, indexado por linha * n + coluna."""
    vizinhos = []
    for linha in range(n):
        for coluna in range(n):
            adjacentes = []
            for deslocamento_linha, deslocamento_coluna in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nova_linha = linha + deslocamento_linha
                nova_coluna = coluna + deslocamento_coluna
                if 0 <= nova_linha < n and 0 <= nova_coluna < n:
                    adjacentes.append(nova_linha * n + nova_coluna)
            vizinhos.append(adjacentes)
    return vizinhos


def grupo_e_liberdades(tab, p, viz):
    """Percorre pedras conectadas à de `p` e reúne seus vizinhos vazios.

    Devolve (pedras do grupo, liberdades); cada liberdade conta uma vez só.
    """
    cor = tab[p]
    grupo, liberdades, pilha = set(), set(), [p]
    while pilha:
        ponto = pilha.pop()
        if ponto in grupo:
            continue
        grupo.add(ponto)
        for vizinho in viz[ponto]:
            if tab[vizinho] == VAZIO:
                liberdades.add(vizinho)
            elif tab[vizinho] == cor:
                pilha.append(vizinho)
    return grupo, liberdades


def pontuar(tab, viz):
    """Conta pedras e território de cada cor pela regra de área.

    Uma região vazia só é território se tocar pedras de uma única cor;
    regiões que tocam as duas cores não pontuam.
    """
    pedras = {PRETO: 0, BRANCO: 0}
    territorio = {PRETO: 0, BRANCO: 0}
    visitados = set()
    for ponto in range(len(tab)):
        if tab[ponto] != VAZIO:
            pedras[tab[ponto]] += 1
        elif ponto not in visitados:
            regiao, cores_da_borda, pilha = set(), set(), [ponto]
            while pilha:
                atual = pilha.pop()
                if atual in regiao:
                    continue
                regiao.add(atual)
                for vizinho in viz[atual]:
                    if tab[vizinho] == VAZIO:
                        pilha.append(vizinho)
                    else:
                        cores_da_borda.add(tab[vizinho])
            visitados.update(regiao)
            if len(cores_da_borda) == 1:
                territorio[next(iter(cores_da_borda))] += len(regiao)
    return pedras, territorio
