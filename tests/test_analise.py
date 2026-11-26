"""Testes unitários para o módulo de análise de erros (`src.analise`)."""

import contextlib
import io
import math
import unittest

from src.analise import (
    calcular_erros_absolutos,
    calcular_erros_relativos,
    exibir_analise_erros,
    resumir_erro,
)
from src.contratos import ResultadoMetodo
from src.metodos.euler import resolver_euler
from src.problema import criar_pvi_trabalho


class TestAnalise(unittest.TestCase):
    def test_calcular_erros_absolutos_ponto_a_ponto(self) -> None:
        exata = lambda x: 2.0 * x
        resultado = ResultadoMetodo(
            nome="Teste",
            x=[0.0, 1.0, 2.0],
            y=[0.0, 1.5, 4.2],
        )

        erros = calcular_erros_absolutos(exata, resultado)

        self.assertEqual(len(erros), 3)
        self.assertAlmostEqual(erros[0], 0.0)
        self.assertAlmostEqual(erros[1], 0.5)
        self.assertAlmostEqual(erros[2], 0.2)

    def test_calcular_erros_relativos_divide_pelo_valor_exato(self) -> None:
        exata = lambda x: 2.0 * x
        resultado = ResultadoMetodo(nome="Teste", x=[1.0, 2.0], y=[1.5, 4.2])

        relativos = calcular_erros_relativos(exata, resultado)

        self.assertAlmostEqual(relativos[0], 0.25)
        self.assertAlmostEqual(relativos[1], 0.05)

    def test_calcular_erros_relativos_retorna_nan_onde_exata_zera(self) -> None:
        exata = lambda x: 2.0 * x
        resultado = ResultadoMetodo(nome="Teste", x=[0.0, 1.0], y=[0.1, 2.0])

        relativos = calcular_erros_relativos(exata, resultado)

        self.assertTrue(math.isnan(relativos[0]))
        self.assertAlmostEqual(relativos[1], 0.0)

    def test_resumir_erro_extrai_maximo_posicao_media_e_final(self) -> None:
        exata = lambda x: 2.0 * x
        resultado = ResultadoMetodo(
            nome="Teste",
            x=[0.0, 1.0, 2.0],
            y=[0.0, 1.4, 3.7],  # erros: 0.0, 0.6, 0.3
        )

        resumo = resumir_erro(exata, resultado)

        self.assertEqual(resumo.nome, "Teste")
        self.assertAlmostEqual(resumo.erro_maximo, 0.6)
        self.assertEqual(resumo.x_erro_maximo, 1.0)
        self.assertAlmostEqual(resumo.erro_medio, 0.3)
        self.assertAlmostEqual(resumo.erro_final, 0.3)

    def test_exibir_analise_erros_imprime_resumo_e_tabela(self) -> None:
        pvi = criar_pvi_trabalho()
        res_euler = resolver_euler(pvi)

        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            exibir_analise_erros(pvi.solucao_exata, [res_euler])

        texto = saida.getvalue()
        self.assertIn("Método de Euler", texto)
        self.assertIn("Exata", texto)
        self.assertIn("5.0", texto)

    def test_exibir_analise_sem_solucao_exata_nao_quebra(self) -> None:
        res = ResultadoMetodo(nome="Teste", x=[0.0], y=[3.0])
        exibir_analise_erros(None, [res])


if __name__ == "__main__":
    unittest.main()
