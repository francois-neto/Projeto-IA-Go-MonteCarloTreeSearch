import csv
import tempfile
import unittest
from pathlib import Path

from src.evaluation.experimento import ControladorExperimento


class SemprePassa:
    def __init__(self, nome):
        self.nome = nome

    def escolher_jogada(self, estado):
        return None, 0.0, 0


class AvaliacaoTest(unittest.TestCase):
    def test_torneio_original_com_cores_alternadas_e_csv(self):
        controlador = ControladorExperimento(SemprePassa("A"), SemprePassa("B"))
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "partidas.csv"
            resumo = controlador.executar_torneio(3, caminho)
            with caminho.open(newline="", encoding="utf-8") as arquivo:
                partidas = list(csv.DictReader(arquivo))

        self.assertEqual([(p["preto"], p["branco"]) for p in partidas],
                         [("A", "B"), ("B", "A"), ("A", "B")])
        self.assertEqual([p["partida"] for p in partidas], ["1", "2", "3"])
        self.assertEqual(resumo["A"]["vitorias_branco"], 1)
        self.assertEqual(resumo["B"]["vitorias_branco"], 2)
        self.assertEqual(len(resumo), 2)

    def test_nomes_iguais_recebem_sufixos(self):
        controlador = ControladorExperimento(SemprePassa("A"), SemprePassa("A"))
        self.assertEqual((controlador.nome_a, controlador.nome_b), ("A_a", "A_b"))


if __name__ == "__main__":
    unittest.main()
