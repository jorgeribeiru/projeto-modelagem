"""Testes da lógica de filtros e inspeção da interface (`src.interface.estado`), sem display."""

import unittest

from main import montar_cenario
from src.interface.estado import (
    EstadoFiltros,
    faixa_de_indices,
    formatar_numero,
    formatar_percentual,
    formatar_razao,
    mover_indice,
    no_mais_proximo,
    resumo_ponto,
)
from src.visualizacao import ERRO_ABSOLUTO, ESCALA_LINEAR, ESCALA_LOG, NOME_EULER, NOME_EXATA, NOME_RK4


class TestEstadoFiltros(unittest.TestCase):
    def setUp(self) -> None:
        self.cenario = montar_cenario()
        self.malha = self.cenario.resultados[0].x

    def test_padrao_exibe_tudo_no_dominio_inteiro(self) -> None:
        estado = EstadoFiltros.padrao(self.cenario)

        self.assertEqual(estado.visiveis, {NOME_EXATA, NOME_EULER, NOME_RK4})
        self.assertEqual((estado.x_min, estado.x_max), (0.0, 5.0))
        self.assertEqual(estado.escala_y, ESCALA_LINEAR)
        self.assertEqual(estado.escala_erro, ESCALA_LOG)
        self.assertEqual(estado.tipo_erro, ERRO_ABSOLUTO)
        self.assertEqual(estado.h, 0.1)

    def test_opcoes_grafico_refletem_o_estado(self) -> None:
        estado = EstadoFiltros.padrao(self.cenario)
        estado.visiveis.discard(NOME_EULER)
        estado.definir_intervalo(1.0, 2.0, (0.0, 5.0))

        opcoes = estado.opcoes_grafico()

        self.assertNotIn(NOME_EULER, opcoes.visiveis)
        self.assertEqual(opcoes.intervalo_x, (1.0, 2.0))

    def test_definir_intervalo_respeita_limites_e_largura_minima(self) -> None:
        estado = EstadoFiltros.padrao(self.cenario)

        estado.definir_intervalo(-3.0, 9.0, (0.0, 5.0))
        self.assertEqual((estado.x_min, estado.x_max), (0.0, 5.0))

        estado.definir_intervalo(2.0, 2.0, (0.0, 5.0))
        self.assertEqual((estado.x_min, estado.x_max), (2.0, 2.1))

        estado.definir_intervalo(5.0, 5.0, (0.0, 5.0))
        self.assertEqual((estado.x_min, estado.x_max), (4.9, 5.0))


class TestInspecaoDePontos(unittest.TestCase):
    def setUp(self) -> None:
        self.cenario = montar_cenario()
        self.malha = self.cenario.resultados[0].x

    def test_no_mais_proximo(self) -> None:
        self.assertEqual(no_mais_proximo(self.malha, -1.0), 0)
        self.assertEqual(no_mais_proximo(self.malha, 0.04), 0)
        self.assertEqual(no_mais_proximo(self.malha, 0.06), 1)
        self.assertEqual(no_mais_proximo(self.malha, 1.23), 12)
        self.assertEqual(no_mais_proximo(self.malha, 99.0), 50)

    def test_faixa_de_indices(self) -> None:
        self.assertEqual(faixa_de_indices(self.malha, 0.0, 5.0), (0, 50))
        self.assertEqual(faixa_de_indices(self.malha, 1.0, 2.0), (10, 20))
        self.assertEqual(faixa_de_indices(self.malha, 1.05, 1.95), (11, 19))

    def test_mover_indice_para_nas_bordas(self) -> None:
        self.assertEqual(mover_indice(10, 1, 10, 20), 11)
        self.assertEqual(mover_indice(10, -1, 10, 20), 10)
        self.assertEqual(mover_indice(20, 1, 10, 20), 20)

    def test_resumo_no_ponto_inicial_tem_erro_zero(self) -> None:
        resumo = resumo_ponto(self.cenario, 0)

        self.assertEqual(resumo.x, 0.0)
        self.assertAlmostEqual(resumo.exato, 3.0)
        self.assertTrue(all(m.erro_absoluto == 0.0 for m in resumo.metodos))
        self.assertIsNone(resumo.razao)

    def test_resumo_compara_euler_e_rk4(self) -> None:
        resumo = resumo_ponto(self.cenario, 10)

        self.assertAlmostEqual(resumo.x, 1.0)
        self.assertEqual(resumo.pior, NOME_EULER)
        self.assertEqual(resumo.melhor, NOME_RK4)
        self.assertGreater(resumo.razao, 1000)

    def test_formatar_numero(self) -> None:
        self.assertEqual(formatar_numero(0.0), "0")
        self.assertEqual(formatar_numero(2.5), "2.500000")
        self.assertEqual(formatar_numero(1.234e-5), "1.234 × 10⁻⁵")
        self.assertEqual(formatar_numero(float("nan")), "—")

    def test_formatar_percentual_e_razao(self) -> None:
        self.assertEqual(formatar_percentual(0.0695), "6.95 %")
        self.assertEqual(formatar_percentual(5.83e-7), "5.830 × 10⁻⁵ %")
        self.assertEqual(formatar_razao(6871.4), "6\u202f871")
        self.assertEqual(formatar_razao(2.04), "2.0")


if __name__ == "__main__":
    unittest.main()
