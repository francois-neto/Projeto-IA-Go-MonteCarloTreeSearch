from src.go.rules import BRANCO, KOMI, PRETO, VAZIO
from src.go.state import Estado
from src.mcts.agent import mcts

SIMBOLO_POR_COR = {VAZIO: "+", PRETO: "X", BRANCO: "O"}
COLUNAS = "ABCDEFGHJ"
TEMPO_POR_NIVEL = {"1": 0.5, "2": 2.0, "3": 6.0}


def nome_ponto(ponto, tamanho):
    """Converte o índice de uma interseção para uma coordenada como C3.

    @param ponto: Índice da interseção no tabuleiro.
    @param tamanho: Número de interseções por lado.
    @return: Coordenada usada na interface.
    """
    coordenadas = divmod(ponto, tamanho)
    linha = coordenadas[0]
    coluna = coordenadas[1]
    return f"{COLUNAS[coluna]}{tamanho - linha}"


def ler_jogada(texto, tamanho):
    """Converte uma coordenada como C3 em índice.

    @param texto: Coordenada digitada pelo jogador.
    @param tamanho: Número de interseções por lado.
    @return: Índice do ponto ou None se a entrada for inválida.
    """
    texto = texto.strip().upper()
    if len(texto) < 2 or texto[0] not in COLUNAS[:tamanho] or not texto[1:].isdigit():
        return None
    linha = int(texto[1:])
    if not 1 <= linha <= tamanho:
        return None
    return (tamanho - linha) * tamanho + COLUNAS.index(texto[0])


def desenhar(estado):
    """Mostra as pedras nas interseções do tabuleiro.

    @param estado: Estado da partida a exibir.
    """
    tamanho = estado.tamanho
    cabecalho = "    " + "   ".join(COLUNAS[:tamanho])
    print("\n" + cabecalho)
    for linha in range(tamanho):
        simbolos = [SIMBOLO_POR_COR[estado.tabuleiro[linha * tamanho + coluna]]
                    for coluna in range(tamanho)]
        print(f"{tamanho - linha:2}  " + "---".join(simbolos) + f"  {tamanho - linha}")
        if linha < tamanho - 1:
            print("    " + "   ".join("|" * tamanho))
    print(cabecalho)


def perguntar(texto, opcoes_validas, padrao):
    """Repete a pergunta até receber uma opção válida.

    @param texto: Pergunta exibida no terminal.
    @param opcoes_validas: Respostas aceitas.
    @param padrao: Resposta adotada quando a entrada está vazia.
    @return: Opção escolhida.
    """
    while True:
        resposta = input(f"{texto} [{padrao}]: ").strip().upper() or padrao
        if resposta in opcoes_validas:
            return resposta
        print("Opção inválida.")


def mostrar_resultado(estado, cor_humana):
    """Exibe o placar por área e o vencedor da partida.

    @param estado: Estado final da partida.
    @param cor_humana: Cor escolhida pelo jogador humano.
    """
    desenhar(estado)
    contagens = estado.pontuar()
    pedras = contagens[0]
    territorio = contagens[1]
    placar = estado.placar()
    pontos_pretos = placar[0]
    pontos_brancos = placar[1]
    print("\n=== Fim de jogo ===")
    print(f"X (preto):  {pedras[PRETO]} pedras + {territorio[PRETO]} de território = {pontos_pretos:g}")
    print(f"O (branco): {pedras[BRANCO]} pedras + {territorio[BRANCO]} de território"
          f" + {estado.komi:g} de komi = {pontos_brancos:g}")
    vencedor = estado.vencedor()
    print(f"Vitória de {SIMBOLO_POR_COR[vencedor]}! "
          + ("Parabéns!" if vencedor == cor_humana else "O bot levou essa."))


def bot_deve_passar(estado):
    """Encerra a partida se o humano passou e o bot já está ganhando.

    @param estado: Estado da partida, com o bot na vez de jogar.
    @return: True se passar encerra a partida com vitória do bot.
    """
    if estado.passes != 1:
        return False
    placar = estado.placar()
    pontos_pretos = placar[0]
    pontos_brancos = placar[1]
    return (pontos_pretos > pontos_brancos) == (estado.vez == PRETO)


def main():
    print("=== GO NO TERMINAL ===")
    print("X = preto (joga primeiro)   O = branco   + = ponto vazio")
    print("Contagem por área (pedras + território + komi para o branco).")
    print("Pedras mortas precisam ser capturadas antes de passar.\n")

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
