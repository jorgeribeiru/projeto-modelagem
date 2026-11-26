"""Testes do gráfico comparativo da letra (c) (`src.visualizacao`), sem display."""

import math
import tempfile
import unittest
from pathlib import Path

from main import montar_cenario
from src.visualizacao import (
    ERRO_RELATIVO,
    ESCALA_LOG,
    GID_SETA_EIXO,
    NOME_EULER,
    NOME_EXATA,
    NOME_RK4,
    PONTOS_CURVA_EXATA,
    ROTULO_X,
    ROTULO_Y,
    ROTULOS_ERRO,
    OpcoesGrafico,
    amostrar_exata,
    estilo_da_curva,
    montar_figura_comparacao,
    plotar_comparacao,
)


def _curvas(ax):
    """Linhas de dados (ignora as pontas de seta dos eixos)."""
    return {linha.get_label(): linha for linha in ax.get_lines() if linha.get_gid() != GID_SETA_EIXO}


class TestVisualizacao(unittest.TestCase):
    def setUp(self) -> None:
        self.cenario = montar_cenario()

    def test_amostrar_exata_cobre_o_intervalo(self) -> None:
        xs, ys = amostrar_exata(math.exp, 0.0, 1.0, n=11)

        self.assertEqual(len(xs), 11)
        self.assertEqual((xs[0], xs[-1]), (0.0, 1.0))
        self.assertAlmostEqual(ys[-1], math.e)

    def test_tres_curvas_no_mesmo_frame(self) -> None:
        _, ax_solucoes, _ = montar_figura_comparacao(self.cenario, OpcoesGrafico())
        curvas = _curvas(ax_solucoes)

        self.assertEqual(set(curvas), {NOME_EXATA, NOME_EULER, NOME_RK4})
        self.assertEqual(len(curvas[NOME_EXATA].get_xdata()), PONTOS_CURVA_EXATA)
        self.assertEqual(len(curvas[NOME_EULER].get_xdata()), 51)

    def test_estilos_distintos_para_curvas_sobrepostas(self) -> None:
        _, ax_solucoes, _ = montar_figura_comparacao(self.cenario, OpcoesGrafico())
        curvas = _curvas(ax_solucoes)

        self.assertEqual(curvas[NOME_RK4].get_linestyle(), "--")
        self.assertEqual(curvas[NOME_RK4].get_markerfacecolor(), "none")
        self.assertNotEqual(curvas[NOME_EULER].get_linestyle(), curvas[NOME_EXATA].get_linestyle())
        self.assertNotEqual(estilo_da_curva(NOME_EULER)["linestyle"], estilo_da_curva(NOME_RK4)["linestyle"])

    def test_eixos_rotulados(self) -> None:
        _, ax_solucoes, ax_erro = montar_figura_comparacao(self.cenario, OpcoesGrafico())

        self.assertEqual(ax_solucoes.get_ylabel(), ROTULO_Y)
        self.assertEqual(ax_erro.get_xlabel(), ROTULO_X)
        self.assertEqual(ax_erro.get_ylabel(), ROTULOS_ERRO["absoluto"])

    def test_filtros_de_curva_intervalo_e_erro(self) -> None:
        opcoes = OpcoesGrafico(visiveis={NOME_EULER}, intervalo_x=(1.0, 2.0), tipo_erro=ERRO_RELATIVO)
        _, ax_solucoes, ax_erro = montar_figura_comparacao(self.cenario, opcoes)

        self.assertEqual(set(_curvas(ax_solucoes)), {NOME_EULER})
        self.assertEqual(ax_solucoes.get_xlim(), (1.0, 2.0))
        xs = _curvas(ax_solucoes)[NOME_EULER].get_xdata()
        self.assertEqual((min(xs), max(xs)), (1.0, 2.0))
        self.assertEqual(ax_erro.get_ylabel(), ROTULOS_ERRO[ERRO_RELATIVO])

    def test_erro_em_escala_log_descarta_o_zero_da_condicao_inicial(self) -> None:
        opcoes = OpcoesGrafico(escala_erro=ESCALA_LOG)
        _, _, ax_erro = montar_figura_comparacao(self.cenario, opcoes)

        self.assertEqual(ax_erro.get_yscale(), "log")
        self.assertTrue(all(e > 0 for e in _curvas(ax_erro)[NOME_EULER].get_ydata()))

    def test_plotar_comparacao_salva_png_e_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as pasta:
            salvos = plotar_comparacao(self.cenario, Path(pasta) / "figura.png")

            self.assertEqual([p.suffix for p in salvos], [".png", ".pdf"])
            self.assertTrue(all(p.stat().st_size > 0 for p in salvos))


if __name__ == "__main__":
    unittest.main()
