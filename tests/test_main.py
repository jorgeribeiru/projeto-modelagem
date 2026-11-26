"""Teste de fumaça (smoke test) para o orquestrador `main.py`."""

import contextlib
import io
import unittest

from main import main


class TestMain(unittest.TestCase):
    def test_main_executa_fluxo_euler_sem_erros(self) -> None:
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            main()

        texto = saida.getvalue()
        self.assertIn("Método de Euler", texto)
        self.assertIn("51", texto)


if __name__ == "__main__":
    unittest.main()
