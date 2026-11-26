"""Testes unitários para a modelagem do problema e malha em `src.problema`."""

import math
import unittest

from src.contratos import ProblemaPVI
from src.problema import criar_pvi_trabalho, f, gerar_malha, solucao_exata


class TestProblema(unittest.TestCase):
    def test_valores_no_ponto_inicial(self) -> None:
        self.assertEqual(solucao_exata(0.0), 3.0)
        self.assertEqual(f(0.0, 3.0), -5.0)

    def test_solucao_exata_satisfaz_a_edo(self) -> None:
        # Derivada analítica de exp(-x) + 2*exp(-2x) é -exp(-x) - 4*exp(-2x)
        for x in [0.0, 0.5, 1.0, 2.5, 5.0]:
            y_exato = solucao_exata(x)
            derivada_esperada = -math.exp(-x) - 4.0 * math.exp(-2.0 * x)
            self.assertAlmostEqual(f(x, y_exato), derivada_esperada, places=12)

    def test_gerar_malha_51_pontos_sem_erro_flutuante(self) -> None:
        malha = gerar_malha(0.0, 5.0, 0.1)

        self.assertEqual(len(malha), 51)
        self.assertEqual(malha[0], 0.0)
        self.assertEqual(malha[3], 0.3)
        self.assertEqual(malha[-1], 5.0)

    def test_criar_pvi_trabalho_retorna_contrato_completo(self) -> None:
        pvi = criar_pvi_trabalho()

        self.assertIsInstance(pvi, ProblemaPVI)
        self.assertEqual(pvi.x0, 0.0)
        self.assertEqual(pvi.y0, 3.0)
        self.assertEqual(pvi.x_fim, 5.0)
        self.assertEqual(pvi.h, 0.1)
        self.assertIsNotNone(pvi.solucao_exata)
        assert pvi.solucao_exata is not None
        self.assertAlmostEqual(pvi.solucao_exata(0.0), pvi.y0)


if __name__ == "__main__":
    unittest.main()
