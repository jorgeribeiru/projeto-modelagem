"""Regressão: segurar as setas não pode empilhar redesenhos (requer display; pulado sem ele)."""

import os
import tkinter
import unittest

from main import montar_cenario


def _tk_disponivel() -> bool:
    if os.name != "nt" and not os.environ.get("DISPLAY"):
        return False
    try:
        tkinter.Tk().destroy()
    except tkinter.TclError:
        return False
    return True


@unittest.skipUnless(_tk_disponivel(), "requer um display para abrir a janela")
class TestNavegacaoPorTeclado(unittest.TestCase):
    def setUp(self) -> None:
        from src.interface.app import AplicativoAnalise

        self.app = AplicativoAnalise(montar_cenario(), montar_cenario, mostrar_guia=False)
        # Mapeada (eventos de tecla não chegam a janelas ocultas), mas transparente para não piscar na tela.
        self.app.attributes("-alpha", 0.0)
        self.app.update()
        self.desenhos_completos = 0
        desenhar = self.app.canvas.draw

        def contar_desenho() -> None:
            self.desenhos_completos += 1
            desenhar()

        self.app.canvas.draw = contar_desenho

    def tearDown(self) -> None:
        for pendente in self.app.tk.call("after", "info"):
            self.app.after_cancel(pendente)
        self.app.destroy()

    def test_rajada_de_setas_agrupa_a_atualizacao_visual(self) -> None:
        self.app._selecionar(0)
        self.app.update()
        self.desenhos_completos = 0
        atualizacoes = []
        atualizar_original = self.app.inspetor.atualizar
        self.app.inspetor.atualizar = lambda resumo: (atualizacoes.append(resumo), atualizar_original(resumo))

        for _ in range(40):
            self.app.event_generate("<Right>", when="tail")
        self.app.event_generate("<Left>", when="tail")
        self.app.update()

        self.assertEqual(self.app.estado.indice_inspecionado, 39)
        self.assertEqual(self.desenhos_completos, 0)
        self.assertEqual(len(atualizacoes), 1)
        self.assertEqual(atualizacoes[-1].indice, 39)

    def test_navegacao_para_nas_bordas_do_intervalo(self) -> None:
        self.app._selecionar(49)
        for _ in range(5):
            self.app.event_generate("<Right>", when="tail")
        self.app.update()

        self.assertEqual(self.app.estado.indice_inspecionado, 50)


if __name__ == "__main__":
    unittest.main()
