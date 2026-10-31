"""Verificações básicas das regras e da integração com o MCTS."""

import unittest

from main import bot_deve_passar, ler_jogada, nome_ponto
from src.go.rules import BRANCO, PRETO, VAZIO
from src.go.state import Estado
from src.mcts.agent import mcts
from src.mcts.node import No


class JogoTest(unittest.TestCase):
    def test_interface_e_passe_do_bot(self):
        self.assertEqual(ler_jogada(nome_ponto(12, 5), 5), 12)
        estado = Estado(5, 0.5)
        self.assertFalse(bot_deve_passar(estado))
        estado.jogar(None)
        self.assertTrue(bot_deve_passar(estado))

    def test_jogadas_nao_tentadas(self):
        est = Estado(5, 0.5)
        self.assertEqual(No(est).nao_tentadas, est.jogadas_legais())
        est.jogar(None)
        est.jogar(None)
        self.assertEqual(No(est).nao_tentadas, [])

    def test_captura_e_ko(self):
        est = Estado(5, 0.5)
        for p in (1, 5, 11):
            est.tabuleiro[p] = PRETO
        for p in (2, 6, 8, 12):
            est.tabuleiro[p] = BRANCO
        est.historico = {bytes(est.tabuleiro)}

        self.assertIsNone(est.jogar(7))
        self.assertEqual(est.tabuleiro[6], VAZIO)
        self.assertIn("ko", est.jogar(6))
        self.assertEqual(est.tabuleiro[7], PRETO)

    def test_suicidio_e_placar(self):
        est = Estado(5, 0.5)
        for p in (1, 5, 7, 11):
            est.tabuleiro[p] = BRANCO
        self.assertIn("suicídio", est.jogar(6))
        self.assertEqual(est.tabuleiro[6], VAZIO)
        self.assertEqual(est.placar(), (0, 25.5))

    def test_passes_e_mcts(self):
        est = Estado(5, 0.5)
        resultado = mcts(est, 0)
        jogada = resultado[0]
        chance = resultado[1]
        sims = resultado[2]
        self.assertIn(jogada, est.jogadas_legais())
        self.assertTrue(0 <= chance <= 1)
        self.assertGreaterEqual(sims, 1)
        self.assertIsNone(est.jogar(None))
        self.assertIsNone(est.jogar(None))
        self.assertTrue(est.terminal())


if __name__ == "__main__":
    unittest.main()
