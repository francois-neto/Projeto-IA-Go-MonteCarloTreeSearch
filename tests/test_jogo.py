"""Verificações básicas das regras e da integração com o MCTS."""

import unittest

from main import bot_deve_passar, ler_jogada, nome_ponto
from src.go.rules import BRANCO, KOMI, PRETO, VAZIO
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

    def test_tamanhos_komi_e_vizinhos(self):
        for tamanho, komi in ((5, 0.5), (7, 4.5), (9, 6.5)):
            est = Estado(tamanho, komi)
            self.assertEqual(len(est.tabuleiro), tamanho * tamanho)
            self.assertTrue(all(ponto == VAZIO for ponto in est.tabuleiro))
            self.assertEqual(est.vez, PRETO)
            self.assertEqual(est.komi, komi)
            self.assertEqual(len(est.jogadas_legais()), tamanho * tamanho + 1)
            self.assertEqual(len(est.vizinhos[0]), 2)
            self.assertEqual(len(est.vizinhos[(tamanho // 2) * tamanho + tamanho // 2]), 4)

    def test_turnos_e_passos(self):
        est = Estado(5, 0.5)
        est.jogar(0)
        self.assertEqual(est.vez, BRANCO)
        historico_com_pedra = set(est.historico)
        est.jogar(None)
        self.assertEqual(est.vez, PRETO)
        self.assertEqual(est.passes, 1)
        self.assertFalse(est.terminal())
        self.assertEqual(est.historico, historico_com_pedra)
        est.jogar(1)
        self.assertEqual(est.passes, 0)
        historico_com_duas_pedras = set(est.historico)
        est.jogar(None)
        est.jogar(None)
        self.assertTrue(est.terminal())
        self.assertEqual(est.passes, 2)
        self.assertEqual(est.historico, historico_com_duas_pedras)

    def test_captura_multiplos_grupos(self):
        est = Estado(5, 0.5)
        for ponto in (0, 2, 10, 12, 16):
            est.tabuleiro[ponto] = PRETO
        for ponto in (1, 11):
            est.tabuleiro[ponto] = BRANCO
        est.historico = {bytes(est.tabuleiro)}
        self.assertIsNone(est.jogar(6))
        self.assertEqual(est.tabuleiro[1], VAZIO)
        self.assertEqual(est.tabuleiro[11], VAZIO)

    def test_captura_em_7x7_e_9x9(self):
        for tamanho in (7, 9):
            est = Estado(tamanho, KOMI[tamanho])
            est.tabuleiro[2] = BRANCO
            est.tabuleiro[1] = PRETO
            est.tabuleiro[3] = PRETO
            est.historico = {bytes(est.tabuleiro)}
            self.assertIsNone(est.jogar(tamanho + 2))
            self.assertEqual(est.tabuleiro[2], VAZIO)

    def test_suicidio_que_captura_e_legal(self):
        est = Estado(5, 0.5)
        for ponto in range(25):
            if ponto != 6:
                est.tabuleiro[ponto] = BRANCO
        est.historico = {bytes(est.tabuleiro)}
        self.assertIsNone(est.jogar(6))
        self.assertFalse(any(ponto == BRANCO for ponto in est.tabuleiro))
        self.assertEqual(est.tabuleiro[6], PRETO)

    def test_superko_posicional(self):
        est = Estado(5, 0.5)
        est.tabuleiro[0] = PRETO
        est.tabuleiro[2] = PRETO
        est.tabuleiro[1] = BRANCO
        posicao_anterior = [VAZIO] * 25
        posicao_anterior[0] = PRETO
        posicao_anterior[2] = PRETO
        posicao_anterior[6] = PRETO
        est.historico = {bytes(posicao_anterior)}
        self.assertIn("ko", est.jogar(6))

    def test_pontuacao_area_neutra_e_komi(self):
        est = Estado(5, 0.5)
        self.assertEqual(est.placar(), (0, 0.5))

        est = Estado(5, 0.5)
        est.tabuleiro[0] = PRETO
        self.assertEqual(est.placar(), (25, 0.5))

        est = Estado(5, 0.5)
        est.tabuleiro[0] = PRETO
        est.tabuleiro[4] = BRANCO
        self.assertEqual(est.pontuar()[1], {PRETO: 0, BRANCO: 0})
        self.assertEqual(est.placar(), (1, 1.5))

        for tamanho in (7, 9):
            est = Estado(tamanho, KOMI[tamanho])
            self.assertEqual(est.placar(), (0, KOMI[tamanho]))

        est = Estado(5, 0.0)
        est.tabuleiro[0] = PRETO
        est.tabuleiro[4] = BRANCO
        self.assertEqual(est.placar(), (1, 1))
        self.assertEqual(est.vencedor(), BRANCO)


if __name__ == "__main__":
    unittest.main()
