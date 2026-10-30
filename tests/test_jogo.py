"""Verificações básicas das regras e da integração com o MCTS."""

import unittest

from src.go.rules import BRANCO, PRETO, VAZIO
from src.go.state import Estado
from src.mcts.agent import mcts


class JogoTest(unittest.TestCase):
    def test_captura_e_ko(self):
        est = Estado(5, 0.5)
        for p in (1, 5, 11):
            est.tab[p] = PRETO
        for p in (2, 6, 8, 12):
            est.tab[p] = BRANCO
        est.hist = {bytes(est.tab)}

        self.assertIsNone(est.jogar(7))
        self.assertEqual(est.tab[6], VAZIO)
        self.assertIn("ko", est.jogar(6))
        self.assertEqual(est.tab[7], PRETO)

    def test_suicidio_e_placar(self):
        est = Estado(5, 0.5)
        for p in (1, 5, 7, 11):
            est.tab[p] = BRANCO
        self.assertIn("suicídio", est.jogar(6))
        self.assertEqual(est.tab[6], VAZIO)
        self.assertEqual(est.placar(), (0, 25.5))

    def test_passes_e_mcts(self):
        est = Estado(5, 0.5)
        jogada, chance, sims = mcts(est, 0)
        self.assertIn(jogada, est.jogadas_legais())
        self.assertTrue(0 <= chance <= 1)
        self.assertGreaterEqual(sims, 1)
        self.assertIsNone(est.jogar(None))
        self.assertIsNone(est.jogar(None))
        self.assertTrue(est.terminal())


if __name__ == "__main__":
    unittest.main()
