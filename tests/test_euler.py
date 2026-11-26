"""Testes de sanidade e convergência para o Método de Euler (`src.metodos.euler`)."""

import math
import unittest

from src.contratos import ProblemaPVI, ResultadoMetodo
from src.metodos.euler import resolver_euler
from src.problema import criar_pvi_trabalho, solucao_exata


class TestMetodoEuler(unittest.TestCase):
    def test_condicao_inicial_e_tamanho_da_malha(self) -> None:
        pvi = criar_pvi_trabalho()
        resultado = resolver_euler(pvi)

        self.assertIsInstance(resultado, ResultadoMetodo)
        self.assertEqual(len(resultado.x), 51)
        self.assertEqual(len(resultado.y), 51)
        self.assertEqual(resultado.x[0], 0.0)
        self.assertEqual(resultado.x[-1], 5.0)
        self.assertEqual(resultado.y[0], 3.0)

    def test_primeiros_passos_manuais(self) -> None:
        pvi = criar_pvi_trabalho()
        resultado = resolver_euler(pvi)

        # Passo 1: y_1 = 3.0 + 0.1 * (exp(0) - 2*3.0) = 2.5
        self.assertAlmostEqual(resultado.y[1], 2.5, places=12)

        # Passo 2: y_2 = 2.5 + 0.1 * (exp(-0.1) - 2*2.5)
        y2_esperado = 2.5 + 0.1 * (math.exp(-0.1) - 5.0)
        self.assertAlmostEqual(resultado.y[2], y2_esperado, places=12)

    def test_desacoplamento_com_outro_pvi_generico(self) -> None:
        pvi_outro = ProblemaPVI(
            f=lambda x, y: 2.0 * x,
            x0=0.0,
            y0=1.0,
            x_fim=1.0,
            h=0.5,
        )
        resultado = resolver_euler(pvi_outro)

        self.assertEqual(resultado.x, [0.0, 0.5, 1.0])
        self.assertAlmostEqual(resultado.y[0], 1.0)
        self.assertAlmostEqual(resultado.y[1], 1.0)
        self.assertAlmostEqual(resultado.y[2], 1.5)

    def test_erro_global_cai_pela_metade_ao_reduzir_passo(self) -> None:
        pvi_h01 = criar_pvi_trabalho()
        pvi_h005 = ProblemaPVI(
            f=pvi_h01.f,
            x0=pvi_h01.x0,
            y0=pvi_h01.y0,
            x_fim=pvi_h01.x_fim,
            h=0.05,
            solucao_exata=solucao_exata,
        )

        res_01 = resolver_euler(pvi_h01)
        res_005 = resolver_euler(pvi_h005)

        erro_max_01 = max(abs(solucao_exata(x) - y) for x, y in zip(res_01.x, res_01.y))
        erro_max_005 = max(abs(solucao_exata(x) - y) for x, y in zip(res_005.x, res_005.y))

        razao = erro_max_01 / erro_max_005
        self.assertGreater(razao, 1.9)
        self.assertLess(razao, 2.3)


if __name__ == "__main__":
    unittest.main()
