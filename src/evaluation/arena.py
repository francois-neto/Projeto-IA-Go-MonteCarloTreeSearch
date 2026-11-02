import time

from src.go.rules import KOMI, PRETO
from src.go.state import Estado


def bot_deve_passar(estado):
    """Encerra a partida se o adversário passou e o bot já está ganhando.

    @param estado: Estado da partida, com o bot na vez de jogar.
    @return: True se passar encerra a partida com vitória do bot.
    """
    if estado.passes != 1:
        return False
    pontos_pretos, pontos_brancos = estado.placar()
    return (pontos_pretos > pontos_brancos) == (estado.vez == PRETO)


class Arena:
    def __init__(self, tamanho=5):
        self.tamanho = tamanho
        self.komi = KOMI[tamanho]

    def disputar_partida(self, jogador_preto, jogador_branco, rotulo_preto, rotulo_branco):
        estado = Estado(self.tamanho, self.komi)
        limite_turnos = self.tamanho * self.tamanho * 3
        turnos = 0
        inicio = time.monotonic()

        while not estado.terminal() and turnos < limite_turnos:
            cor_atual = estado.vez
            if bot_deve_passar(estado):
                estado.jogar(None)
                turnos += 1
                continue

            agente = jogador_preto if cor_atual == PRETO else jogador_branco
            resultado = agente.escolher_jogada(estado)
            jogada = resultado[0]

            estado.jogar(jogada)
            turnos += 1

        duracao = time.monotonic() - inicio
        placar = estado.placar()
        pontos_pretos = placar[0]
        pontos_brancos = placar[1]
        cor_vencedora = estado.vencedor()
        vencedor = rotulo_preto if cor_vencedora == PRETO else rotulo_branco

        return {
            "preto": rotulo_preto,
            "branco": rotulo_branco,
            "vencedor": vencedor,
            "pontos_pretos": pontos_pretos,
            "pontos_brancos": pontos_brancos,
            "turnos": turnos,
            "duracao_s": round(duracao, 3),
        }
