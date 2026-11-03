import csv
import os

from src.evaluation.arena import Arena
from src.evaluation.competidor import Competidor


class ControladorExperimento:
    def __init__(self, competidor_a, competidor_b, tamanho=5):
        """Prepara os competidores e a arena para o tabuleiro escolhido.

        @param competidor_a: Primeiro competidor do torneio.
        @param competidor_b: Segundo competidor do torneio.
        @param tamanho: Lado do tabuleiro (5, 7 ou 9).
        """
        self.competidor_a = competidor_a
        self.competidor_b = competidor_b
        self.arena = Arena(tamanho)
        if competidor_a.nome != competidor_b.nome:
            self.nome_a, self.nome_b = competidor_a.nome, competidor_b.nome
        else:
            self.nome_a = f"{competidor_a.nome}_a"
            self.nome_b = f"{competidor_b.nome}_b"

    def executar_torneio(self, num_partidas=20, caminho_csv=None):
        """Joga as partidas com cores alternadas e contabiliza as vitórias.

        @param num_partidas: Quantidade de partidas a disputar.
        @param caminho_csv: Caminho opcional para salvar os resultados.
        @return: Vitórias totais e por cor de cada competidor.
        """
        estatisticas = {
            rotulo: {"vitorias": 0, "vitorias_preto": 0, "vitorias_branco": 0}
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

            partida = self.arena.disputar_partida(preto, branco, nome_preto, nome_branco)
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
            with open(caminho_csv, mode="w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=list(historico[0].keys()))
                escritor.writeheader()
                escritor.writerows(historico)

        return estatisticas


def gerar_caminho_csv():
    os.makedirs("experiments", exist_ok=True)
    versao = 1
    while os.path.exists(f"experiments/resultados_torneio_V{versao}.csv"):
        versao += 1
    return f"experiments/resultados_torneio_V{versao}.csv"


if __name__ == "__main__":
    total_jogos = 20
    for simulacoes_a, simulacoes_b in (
        (100, 500), (500, 1000), (100, 1000),
        (1000, 10000), (500, 10000), (100, 10000),
    ):
        controlador = ControladorExperimento(
            Competidor(qtd_simulacoes=simulacoes_a),
            Competidor(qtd_simulacoes=simulacoes_b),
            tamanho=5,
        )
        caminho_csv = gerar_caminho_csv()
        print(f"\n== {simulacoes_a} vs. {simulacoes_b} simulações ==")
        estatisticas = controlador.executar_torneio(
            num_partidas=total_jogos,
            caminho_csv=caminho_csv,
        )
        for nome, dados in estatisticas.items():
            print(f"{nome}: {dados['vitorias']}/{total_jogos} vitórias "
                  f"({dados['vitorias'] / total_jogos:.1%}); "
                  f"preto: {dados['vitorias_preto']}, branco: {dados['vitorias_branco']}")
        print(f"Resultados por partida: {caminho_csv}")
