#!/usr/bin/env python3
"""Go no terminal: você contra um bot Monte Carlo Tree Search (MCTS).

Rode com: python3 main.py
"""

from src.go.rules import BRANCO, KOMI, PRETO, VAZIO
from src.go.state import Estado
from src.mcts.agent import mcts

SIMBOLO = {VAZIO: "+", PRETO: "X", BRANCO: "O"}
COLUNAS = "ABCDEFGHJ"  # no Go não se usa a letra I
TEMPO_POR_NIVEL = {"1": 0.5, "2": 2.0, "3": 6.0}


def nome_ponto(p, n):
    i, j = divmod(p, n)
    return f"{COLUNAS[j]}{n - i}"


def ler_jogada(texto, n):
    """Converte 'C3' em índice; devolve None se inválida."""
    texto = texto.strip().upper()
    if len(texto) < 2 or texto[0] not in COLUNAS[:n] or not texto[1:].isdigit():
        return None
    linha = int(texto[1:])
    if not 1 <= linha <= n:
        return None
    return (n - linha) * n + COLUNAS.index(texto[0])


def desenhar(est):
    n = est.n
    cab = "    " + "   ".join(COLUNAS[:n])
    print("\n" + cab)
    for i in range(n):
        celulas = [SIMBOLO[est.tab[i * n + j]] for j in range(n)]
        print(f"{n - i:2}  " + "---".join(celulas) + f"  {n - i}")
        if i < n - 1:
            print("    " + "   ".join("|" * n))
    print(cab)


def perguntar(texto, validos, padrao):
    while True:
        r = input(f"{texto} [{padrao}]: ").strip().upper() or padrao
        if r in validos:
            return r
        print("Opção inválida.")


def mostrar_resultado(est, humano):
    desenhar(est)
    pedras, terr = est.pontuar()
    pretos, brancos = est.placar()
    print("\n=== Fim de jogo ===")
    print(f"X (preto):  {pedras[PRETO]} pedras + {terr[PRETO]} de território = {pretos:g}")
    print(f"O (branco): {pedras[BRANCO]} pedras + {terr[BRANCO]} de território"
          f" + {est.komi:g} de komi = {brancos:g}")
    venc = est.vencedor()
    print(f"Vitória de {SIMBOLO[venc]}! " + ("Parabéns!" if venc == humano else "O bot levou essa."))


def main():
    print("=== GO NO TERMINAL ===")
    print("X = preto (joga primeiro)   O = branco   + = ponto vazio")
    print("Contagem por área (pedras + território + komi para o branco).")
    print("Pedras mortas precisam ser capturadas antes de passar.\n")

    n = int(perguntar("Tamanho do tabuleiro (5, 7 ou 9)", {"5", "7", "9"}, "5"))
    cor = perguntar("Sua cor (X joga primeiro, O joga depois)", {"X", "O"}, "X")
    nivel = perguntar("Nível do bot (1 fácil, 2 médio, 3 difícil)", {"1", "2", "3"}, "2")
    humano = PRETO if cor == "X" else BRANCO
    tempo = TEMPO_POR_NIVEL[nivel]

    est = Estado(n, KOMI[n])
    ultima = "—"

    while not est.terminal():
        desenhar(est)
        pretos, brancos = est.placar()
        print(f"\nÚltima jogada: {ultima}")
        print(f"Placar atual (área + komi): X {pretos:g} × O {brancos:g}")

        if est.vez == humano:
            entrada = input(f"Sua vez ({SIMBOLO[humano]}) - jogada (ex: C3), PASSO ou SAIR: ").strip().upper()
            if entrada == "SAIR":
                print("Até a próxima!")
                return
            if entrada == "PASSO":
                est.jogar(None)
                ultima = "você passou"
                continue
            p = ler_jogada(entrada, n)
            if p is None:
                print(f"Jogada inválida! Use coluna {COLUNAS[0]}-{COLUNAS[n - 1]} e linha 1-{n}, como C3.")
                continue
            motivo = est.jogar(p)
            if motivo:
                print(f"Jogada ilegal: {motivo}.")
                continue
            ultima = f"você jogou {nome_ponto(p, n)}"
        else:
            # Se o humano passou e o bot já está ganhando, passa e encerra.
            if est.passes == 1:
                pretos, brancos = est.placar()
                bot_ganha = (pretos > brancos) == (est.vez == PRETO)
                if bot_ganha:
                    est.jogar(None)
                    ultima = "o bot passou"
                    continue
            print("\nBot pensando...")
            jogada, chance, sims = mcts(est, tempo)
            est.jogar(jogada)
            ultima = "o bot passou" if jogada is None else f"o bot jogou {nome_ponto(jogada, n)}"
            print(f"({sims} simulações, chance de vitória estimada do bot: {chance:.0%})")

    mostrar_resultado(est, humano)


if __name__ == "__main__":
    main()
