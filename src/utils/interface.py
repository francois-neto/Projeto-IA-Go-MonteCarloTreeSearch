from src.go.rules import BRANCO, PRETO, VAZIO


SIMBOLO_POR_COR = {VAZIO: "+", PRETO: "X", BRANCO: "O"}
COLUNAS = "ABCDEFGHJ"


def menu_inicial():
    print("=== GO NO TERMINAL ===")
    print("X = preto (joga primeiro)   O = branco   + = ponto vazio")
    print("Contagem por área (pedras + território + komi para o branco).")
    print("Pedras mortas precisam ser capturadas antes de passar.\n")


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
