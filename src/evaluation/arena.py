import csv
import random
import time
import os

from src.go.rules import BRANCO, KOMI, PRETO
from src.go.state import Estado
from src.mcts.agent import mcts

class Competidor:
    def __init__(self, qtd_simulacoes=100, peso_exploracao=1.4):
        self.qtd_simulacoes = qtd_simulacoes
        self.peso_exploracao = peso_exploracao #Peso do UCT (Se vai ter mais liberdade ou ser mais conservador na decisão de explorar os nós)
        self.nome = self._gerar_nome()

    def _gerar_nome(self):
        if self.qtd_simulacoes is not None:
            return f"MCTS_{self.qtd_simulacoes}simu_{self.peso_exploracao}peso"
        return "Aleatorio"

    def escolher_jogada(self, estado):
        if self.qtd_simulacoes is None:
            jogada = random.choice(estado.jogadas_legais())
            return jogada, 0.0, 0
        return mcts(
            estado,
            limite_simulacoes=self.qtd_simulacoes, #ALTERAR CLASSE AGENTE PARA RECEBER ESSE PARAMETRO
            peso_exploracao=self.peso_exploracao,
        )

def bot_deve_passar(estado):
    """Encerra a partida se o adversário passou e o jogador da vez já vence.

    @param estado: Estado atual da partida.
    @return: True se passar garante a vitória imediata.
    """
    if estado.passes != 1:
        return False
    placar = estado.placar()
    pontos_pretos = placar[0]
    pontos_brancos = placar[1]
    return (pontos_pretos > pontos_brancos) == (estado.vez == PRETO)

class Arena:
    def __init__(self, competidor_a, competidor_b, tamanho=5):
        self.competidor_a = competidor_a
        self.competidor_b = competidor_b
        nomes = self._definir_nomes_distintos(competidor_a, competidor_b)
        self.nome_a = nomes[0]
        self.nome_b = nomes[1]
        self.tamanho = tamanho
        self.komi = KOMI[tamanho]

    def _definir_nomes_distintos(self, competidor_a, competidor_b):
        if competidor_a.nome != competidor_b.nome:
            return (competidor_a.nome, competidor_b.nome)
        return (f"{competidor_a.nome}_a", f"{competidor_b.nome}_b")

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

    def executar_torneio(self, num_partidas=20, caminho_csv=None):
        estatisticas = {
            rotulo: {
                "vitorias": 0,
                "vitorias_preto": 0,
                "vitorias_branco": 0,
            }
            for rotulo in (self.nome_a, self.nome_b)
        }
        historico = []

        for indice in range(num_partidas):
            if indice % 2 == 0:
                preto, nome_preto = self.competidor_a, self.nome_a
                branco, nome_branco = self.competidor_b, self.nome_b
            else:
                preto, nome_preto = self.competidor_b, self.nome_b
                branco, nome_branco = self.competidor_a, self.nome_a

            partida = self.disputar_partida(preto, branco, nome_preto, nome_branco)
            partida["partida"] = indice + 1
            historico.append(partida)

            nome_vencedor = partida["vencedor"]
            estatisticas[nome_vencedor]["vitorias"] += 1
            if nome_vencedor == partida["preto"]:
                estatisticas[nome_vencedor]["vitorias_preto"] += 1
            else:
                estatisticas[nome_vencedor]["vitorias_branco"] += 1

            print(
                f"[{indice + 1}/{num_partidas}] "
                f"Preto: {nome_preto} ({partida['pontos_pretos']:g}) x "
                f"Branco: {nome_branco} ({partida['pontos_brancos']:g}) -> "
                f"Vitória: {nome_vencedor} em {partida['turnos']} turnos"
            )

        if caminho_csv and historico:
            self._salvar_csv(historico, caminho_csv)

        return estatisticas

    def _salvar_csv(self, historico, caminho_csv):
        campos = list(historico[0].keys())
        with open(caminho_csv, mode="w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(historico)

def gerar_caminho_csv():
    os.makedirs("experiments", exist_ok=True)

    versao = 1
    while os.path.exists(f"experiments/resultados_torneio_V{versao}.csv"):
        versao += 1

    return f"experiments/resultados_torneio_V{versao}.csv"

if __name__ == "__main__":
    agente_a = Competidor(qtd_simulacoes=1000)
    agente_b = Competidor(qtd_simulacoes=1000)

    arena = Arena(agente_a, agente_b, tamanho=5)
    total_jogos = 5
    caminho_csv = gerar_caminho_csv()
    estatisticas = arena.executar_torneio(
        num_partidas=total_jogos,
        caminho_csv=caminho_csv,
    )
    print("==TORNEIO FINALIZADO==")