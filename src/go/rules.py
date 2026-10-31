from functools import lru_cache

VAZIO = 0
PRETO = 1
BRANCO = 2
KOMI = {
    5: 0.5,
    7: 4.5,
    9: 6.5,
}


def oponente(cor):
    """Regra: os jogadores alternam turnos.

    @param cor: Cor do jogador atual (PRETO ou BRANCO).
    @return: Cor do adversário.
    """
    return BRANCO if cor == PRETO else PRETO


@lru_cache(maxsize=None)
def vizinhos_do_tabuleiro(tamanho):
    """Regra: só interseções ortogonais são adjacentes; diagonais não contam.

    Implementação: percorre a grade e guarda índices válidos acima, abaixo,
    à esquerda e à direita de cada ponto (índice = linha * tamanho + coluna).

    @param tamanho: Número de interseções por lado do tabuleiro.
    @return: Lista de vizinhos para cada ponto do tabuleiro.
    """
    vizinhos_por_ponto = []
    for linha in range(tamanho):
        for coluna in range(tamanho):
            vizinhos_do_ponto = []
            for deslocamento in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                deslocamento_linha = deslocamento[0]
                deslocamento_coluna = deslocamento[1]
                nova_linha = linha + deslocamento_linha
                nova_coluna = coluna + deslocamento_coluna
                if 0 <= nova_linha < tamanho and 0 <= nova_coluna < tamanho:
                    vizinhos_do_ponto.append(nova_linha * tamanho + nova_coluna)
            vizinhos_por_ponto.append(vizinhos_do_ponto)
    return vizinhos_por_ponto


def grupo_e_liberdades(tabuleiro, ponto_inicial, vizinhos):
    """Regra: pedras conectadas da mesma cor formam um grupo com liberdades comuns.

    Implementação: usa uma pilha a partir de `ponto_inicial` e conjuntos
    para reunir pedras e vizinhos vazios sem contar repetições.

    @param tabuleiro: Lista de pedras em cada interseção.
    @param ponto_inicial: Índice de uma pedra do grupo.
    @param vizinhos: Lista de vizinhos por interseção.
    @return: Conjuntos de pedras do grupo e de suas liberdades.
    """
    cor = tabuleiro[ponto_inicial]
    grupo = set()
    liberdades = set()
    pilha = [ponto_inicial]
    while pilha:
        ponto = pilha.pop()
        if ponto in grupo:
            continue
        grupo.add(ponto)
        for vizinho in vizinhos[ponto]:
            if tabuleiro[vizinho] == VAZIO:
                liberdades.add(vizinho)
            elif tabuleiro[vizinho] == cor:
                pilha.append(vizinho)
    return grupo, liberdades


def pontuar(tabuleiro, vizinhos):
    """Regra: contam as pedras no tabuleiro e o território cercado por uma cor.

    Implementação: conta as pedras e percorre cada região vazia; só atribui
    seus pontos se a borda tocar pedras de uma única cor.

    @param tabuleiro: Lista de pedras em cada interseção.
    @param vizinhos: Lista de vizinhos por interseção.
    @return: Contagens de pedras e de território por cor.
    """
    pedras = {PRETO: 0, BRANCO: 0}
    territorio = {PRETO: 0, BRANCO: 0}
    visitados = set()
    for ponto in range(len(tabuleiro)):
        if tabuleiro[ponto] != VAZIO:
            pedras[tabuleiro[ponto]] += 1
        elif ponto not in visitados:
            regiao = set()
            cores_da_borda = set()
            pilha = [ponto]
            while pilha:
                ponto_atual = pilha.pop()
                if ponto_atual in regiao:
                    continue
                regiao.add(ponto_atual)
                for vizinho in vizinhos[ponto_atual]:
                    if tabuleiro[vizinho] == VAZIO:
                        pilha.append(vizinho)
                    else:
                        cores_da_borda.add(tabuleiro[vizinho])
            visitados.update(regiao)
            if len(cores_da_borda) == 1:
                territorio[next(iter(cores_da_borda))] += len(regiao)
    return pedras, territorio
