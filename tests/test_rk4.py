"""Testes de sanidade e convergência para Runge-Kutta (`src.metodos.runge_kutta`)."""

import unittest
from dataclasses import replace

from src.contratos import ProblemaPVI, ResultadoMetodo
from src.metodos.runge_kutta import resolver_runge_kutta
from src.problema import criar_pvi_trabalho, solucao_exata


class TestMetodoRungeKutta(unittest.TestCase):
    def test_condicao_inicial_e_tamanho_da_malha(self) -> None:
        pvi = criar_pvi_trabalho()
        resultado = resolver_runge_kutta(pvi)

        self.assertIsInstance(resultado, ResultadoMetodo)
        self.assertEqual(len(resultado.x), 51)
        self.assertEqual(len(resultado.y), 51)
        self.assertEqual(resultado.x[0], 0.0)
        self.assertEqual(resultado.x[-1], 5.0)
        self.assertEqual(resultado.y[0], 3.0)

    def test_primeiros_passos(self) -> None:
        pvi = criar_pvi_trabalho()
        resultado = resolver_runge_kutta(pvi)

        # Valores da recorrência RK4 calculados com precisão decimal.
        self.assertAlmostEqual(resultado.y[1], 2.542304798912142, places=12)
        self.assertAlmostEqual(resultado.y[2], 2.159380526290836, places=12)

    def test_desacoplamento_com_outro_pvi_generico(self) -> None:
        pvi_outro = ProblemaPVI(
            f=lambda x, y: 2.0 * x,
            x0=1.0,
            y0=1.0,
            x_fim=2.0,
            h=0.5,
        )
        resultado = resolver_runge_kutta(pvi_outro)

        self.assertEqual(resultado.x, [1.0, 1.5, 2.0])
        self.assertAlmostEqual(resultado.y[0], 1.0)
        self.assertAlmostEqual(resultado.y[1], 2.25)
        self.assertAlmostEqual(resultado.y[2], 4.0)

    def test_erro_global_converge_com_quarta_ordem(self) -> None:
        pvi_h01 = criar_pvi_trabalho()
        pvi_h005 = replace(pvi_h01, h=0.05)

        res_01 = resolver_runge_kutta(pvi_h01)
        res_005 = resolver_runge_kutta(pvi_h005)

        erro_max_01 = max(abs(solucao_exata(x) - y) for x, y in zip(res_01.x, res_01.y))
        erro_max_005 = max(abs(solucao_exata(x) - y) for x, y in zip(res_005.x, res_005.y))

        self.assertLess(erro_max_01, 2e-5)
        razao = erro_max_01 / erro_max_005
        self.assertGreater(razao, 15.0)
        self.assertLess(razao, 18.0)


if __name__ == "__main__":
    unittest.main()
