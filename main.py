from src.evaluation.arena import bot_deve_passar
from src.go.rules import BRANCO, KOMI, PRETO
from src.go.state import Estado
from src.mcts.agent import mcts
from src.utils.interface import (COLUNAS, SIMBOLO_POR_COR, desenhar, ler_jogada,
                                 mostrar_resultado, nome_ponto, perguntar, menu_inicial)

TEMPO_POR_NIVEL = {"1": 0.5, "2": 2.0, "3": 6.0}


def main():
    menu_inicial()
    tamanho = int(perguntar("Tamanho do tabuleiro (5, 7 ou 9)", {"5", "7", "9"}, "5"))
    simbolo_humano = perguntar("Sua cor (X joga primeiro, O joga depois)", {"X", "O"}, "X")
    nivel = perguntar("Nível do bot (1 fácil, 2 médio, 3 difícil)", {"1", "2", "3"}, "2")
    cor_humana = PRETO if simbolo_humano == "X" else BRANCO
    segundos_por_jogada = TEMPO_POR_NIVEL[nivel]

    estado = Estado(tamanho, KOMI[tamanho])
    ultima_jogada = "—"

    while not estado.terminal():
        desenhar(estado)
        placar = estado.placar()
        pontos_pretos = placar[0]
        pontos_brancos = placar[1]
        print(f"\nÚltima jogada: {ultima_jogada}")
        print(f"Placar atual (área + komi): X {pontos_pretos:g} × O {pontos_brancos:g}")

        if estado.vez == cor_humana:
            entrada = input(f"Sua vez ({SIMBOLO_POR_COR[cor_humana]}) - jogada (ex: C3), PASSO ou SAIR: ").strip().upper()
            if entrada == "SAIR":
                print("Até a próxima!")
                return
            if entrada == "PASSO":
                estado.jogar(None)
                ultima_jogada = "você passou"
                continue
            ponto = ler_jogada(entrada, tamanho)
            if ponto is None:
                print(f"Jogada inválida! Use coluna {COLUNAS[0]}-{COLUNAS[tamanho - 1]} e linha 1-{tamanho}, como C3.")
                continue
            motivo = estado.jogar(ponto)
            if motivo:
                print(f"Jogada ilegal: {motivo}.")
                continue
            ultima_jogada = f"você jogou {nome_ponto(ponto, tamanho)}"
        else:
            if bot_deve_passar(estado):
                estado.jogar(None)
                ultima_jogada = "o bot passou"
                continue
            print("\nBot pensando...")
            resultado = mcts(estado, segundos_por_jogada)
            jogada = resultado[0]
            chance_vitoria = resultado[1]
            simulacoes = resultado[2]
            estado.jogar(jogada)
            ultima_jogada = "o bot passou" if jogada is None else f"o bot jogou {nome_ponto(jogada, tamanho)}"
            print(f"({simulacoes} simulações, chance de vitória estimada do bot: {chance_vitoria:.0%})")

    mostrar_resultado(estado, cor_humana)


if __name__ == "__main__":
    main()
