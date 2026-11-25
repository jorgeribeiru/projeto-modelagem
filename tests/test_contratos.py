"""Testes unitários para as estruturas de dados em `src.contratos`."""

import unittest

from src.contratos import ProblemaPVI, ResultadoMetodo


class TestContratos(unittest.TestCase):
    def test_pvi_campos_obrigatorios_e_default_opcional(self) -> None:
        pvi = ProblemaPVI(
            f=lambda x, y: x - 2.0 * y,
            x0=0.0,
            y0=3.0,
            x_fim=5.0,
            h=0.1,
        )

        self.assertEqual(pvi.x0, 0.0)
        self.assertEqual(pvi.y0, 3.0)
        self.assertEqual(pvi.x_fim, 5.0)
        self.assertEqual(pvi.h, 0.1)
        self.assertIsNone(pvi.solucao_exata)
        self.assertEqual(pvi.f(1.0, 3.0), -5.0)

    def test_pvi_com_solucao_exata(self) -> None:
        pvi = ProblemaPVI(
            f=lambda x, y: y,
            x0=0.0,
            y0=1.0,
            x_fim=1.0,
            h=0.5,
            solucao_exata=lambda x: 2.0 * x + 1.0,
        )

        self.assertIsNotNone(pvi.solucao_exata)
        assert pvi.solucao_exata is not None
        self.assertEqual(pvi.solucao_exata(0.5), 2.0)

    def test_resultado_metodo_armazena_listas_e_compara_por_valor(self) -> None:
        r1 = ResultadoMetodo(
            nome="Método de Euler",
            x=[0.0, 0.1, 0.2],
            y=[3.0, 2.5, 2.09],
        )
        r2 = ResultadoMetodo(
            nome="Método de Euler",
            x=[0.0, 0.1, 0.2],
            y=[3.0, 2.5, 2.09],
        )

        self.assertEqual(r1.nome, "Método de Euler")
        self.assertEqual(len(r1.x), len(r1.y))
        self.assertEqual(r1, r2)


if __name__ == "__main__":
    unittest.main()
