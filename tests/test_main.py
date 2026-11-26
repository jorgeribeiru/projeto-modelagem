"""Teste de fumaça (smoke test) para o orquestrador `main.py`."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from main import main, montar_cenario


class TestMain(unittest.TestCase):
    def test_main_executa_euler_e_rk4_e_salva_o_grafico(self) -> None:
        with tempfile.TemporaryDirectory() as pasta:
            saida = io.StringIO()
            with contextlib.redirect_stdout(saida):
                main(["--saida", pasta])

            texto = saida.getvalue()
            self.assertIn("Método de Euler: 51 pontos", texto)
            self.assertIn("Runge-Kutta (RK4): 51 pontos", texto)
            self.assertIn("Resumo de Erros Absolutos", texto)
            self.assertTrue((Path(pasta) / "comparacao_pvi.png").is_file())
            self.assertTrue((Path(pasta) / "comparacao_pvi.pdf").is_file())

    def test_montar_cenario_com_outro_passo(self) -> None:
        cenario = montar_cenario(0.05)

        self.assertEqual(cenario.pvi.h, 0.05)
        for res in cenario.resultados:
            self.assertEqual(len(res.x), 101)
            self.assertEqual(len(cenario.erros_absolutos[res.nome]), 101)
            self.assertEqual(len(cenario.erros_relativos[res.nome]), 101)

    def test_montar_cenario_padrao_usa_h_do_enunciado(self) -> None:
        cenario = montar_cenario()

        self.assertEqual(cenario.pvi.h, 0.1)
        self.assertEqual([r.nome for r in cenario.resultados], ["Método de Euler", "Runge-Kutta (RK4)"])


if __name__ == "__main__":
    unittest.main()
