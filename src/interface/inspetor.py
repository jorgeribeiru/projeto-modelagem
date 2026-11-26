"""Cartão de inspeção: valores e erros de cada método no nó da malha selecionado."""
from collections.abc import Callable

import customtkinter as ctk

from src.contratos import CenarioComparacao
from src.interface import tema
from src.interface.estado import ResumoPonto, formatar_numero, formatar_percentual, formatar_razao
from src.visualizacao import NOME_EXATA

SUBSCRITOS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def rotulo_no(indice: int) -> str:
    return "x" + str(indice).translate(SUBSCRITOS)


class CartaoInspecao(ctk.CTkFrame):
    def __init__(
        self,
        master,
        cenario: CenarioComparacao,
        fontes: tema.Fontes,
        ao_navegar: Callable[[int], None],
    ) -> None:
        super().__init__(master, fg_color=tema.CARTAO, corner_radius=16, border_width=2, border_color=tema.BORDA)
        self.fontes = fontes
        self.grid_columnconfigure(1, weight=1)

        navegacao = ctk.CTkFrame(self, fg_color="transparent")
        navegacao.grid(row=0, column=0, sticky="nsw", padx=(18, 10), pady=14)
        ctk.CTkLabel(navegacao, text="PONTO INSPECIONADO", font=fontes.rotulo, text_color=tema.DESTAQUE,
                     anchor="w").pack(fill="x")
        self._rotulo_x = ctk.CTkLabel(navegacao, text="—", font=fontes.numero_grande, text_color=tema.TEXTO,
                                      anchor="w")
        self._rotulo_x.pack(fill="x", pady=(2, 4))
        botoes = ctk.CTkFrame(navegacao, fg_color="transparent")
        botoes.pack(fill="x")
        for texto, delta in (("◀", -1), ("▶", 1)):
            ctk.CTkButton(
                botoes, text=texto, width=36, height=30, corner_radius=9, font=fontes.corpo_forte,
                fg_color=tema.SEGMENTO_FUNDO, hover_color=tema.SEGMENTO_HOVER, text_color=tema.TEXTO,
                command=lambda d=delta: ao_navegar(d),
            ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(botoes, text="ou ← →", font=fontes.pequena, text_color=tema.TEXTO_SUAVE).pack(side="left")

        self._colunas = ctk.CTkFrame(self, fg_color="transparent")
        self._colunas.grid(row=0, column=1, sticky="nsew", pady=12)

        self._vazio = ctk.CTkLabel(
            self._colunas,
            text="Clique em qualquer ponto do gráfico para ver aqui o valor de cada método e o erro em relação "
                 "à solução exata naquele nó da malha.",
            font=fontes.corpo, text_color=tema.TEXTO_SUAVE, justify="left", anchor="w", wraplength=620,
        )

        self._cartoes: dict[str, dict[str, ctk.CTkLabel]] = {}
        self._cartao_exata = self._mini_cartao(NOME_EXATA, ("φ(xₙ)",))
        for res in cenario.resultados:
            self._cartoes[res.nome] = self._mini_cartao(res.nome, ("yₙ", "erro abs.", "erro rel."))

        self._veredito = ctk.CTkFrame(self, fg_color=tema.DESTAQUE_SUAVE, corner_radius=12, width=210)
        self._veredito.grid(row=0, column=2, sticky="nse", padx=(6, 14), pady=14)
        self._veredito.grid_propagate(False)
        ctk.CTkLabel(self._veredito, text="COMPARAÇÃO", font=fontes.rotulo, text_color=tema.DESTAQUE,
                     anchor="w").pack(fill="x", padx=14, pady=(12, 0))
        self._texto_veredito = ctk.CTkLabel(self._veredito, text="", font=fontes.corpo, text_color=tema.TEXTO,
                                            anchor="nw", justify="left", wraplength=184)
        self._texto_veredito.pack(fill="both", expand=True, padx=14, pady=(4, 12))

        self._exibindo_vazio: bool | None = None
        self.atualizar(None)

    def _mini_cartao(self, nome: str, campos: tuple[str, ...]) -> dict[str, ctk.CTkLabel]:
        cartao = ctk.CTkFrame(self._colunas, fg_color=tema.CARTAO_ELEVADO, corner_radius=12)
        topo = ctk.CTkFrame(cartao, fg_color="transparent")
        topo.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkFrame(topo, width=10, height=10, corner_radius=5, fg_color=tema.cor_curva(nome)).pack(
            side="left", padx=(0, 7))
        ctk.CTkLabel(topo, text=nome, font=self.fontes.corpo_forte, text_color=tema.TEXTO,
                     anchor="w", height=18).pack(side="left")

        valores: dict[str, ctk.CTkLabel] = {}
        for campo in campos:
            linha = ctk.CTkFrame(cartao, fg_color="transparent")
            linha.pack(fill="x", padx=12, pady=1)
            ctk.CTkLabel(linha, text=campo, font=self.fontes.pequena, text_color=tema.TEXTO_SUAVE,
                         height=18).pack(side="left")
            valor = ctk.CTkLabel(linha, text="—", font=self.fontes.numero, text_color=tema.TEXTO, height=18)
            valor.pack(side="right")
            valores[campo] = valor
        ctk.CTkFrame(cartao, fg_color="transparent", height=6).pack()
        valores["_cartao"] = cartao
        return valores

    def atualizar(self, resumo: ResumoPonto | None) -> None:
        self._alternar_vazio(resumo is None)
        if resumo is None:
            self._rotulo_x.configure(text="—")
            self._texto_veredito.configure(text="Nenhum ponto selecionado.")
            return

        self._rotulo_x.configure(text=f"{rotulo_no(resumo.indice)} = {resumo.x:g}")
        self._cartao_exata["φ(xₙ)"].configure(text=formatar_numero(resumo.exato))
        for metodo in resumo.metodos:
            campos = self._cartoes[metodo.nome]
            campos["yₙ"].configure(text=formatar_numero(metodo.y))
            campos["erro abs."].configure(text=formatar_numero(metodo.erro_absoluto))
            campos["erro rel."].configure(text=formatar_percentual(metodo.erro_relativo))

        if resumo.razao is None:
            texto = "Na condição inicial todos os métodos coincidem com a solução exata (erro zero)."
        else:
            texto = f"{resumo.pior} erra {formatar_razao(resumo.razao)}× mais que {resumo.melhor} neste ponto."
        self._texto_veredito.configure(text=texto)

    def _alternar_vazio(self, vazio: bool) -> None:
        """Refaz o `pack` só na troca de estado; refazê-lo a cada nó deixava a navegação lenta."""
        if vazio == self._exibindo_vazio:
            return
        self._exibindo_vazio = vazio
        todos = [self._cartao_exata, *self._cartoes.values()]
        if vazio:
            for cartao in todos:
                cartao["_cartao"].pack_forget()
            self._vazio.pack(fill="both", expand=True, padx=8)
        else:
            self._vazio.pack_forget()
            for cartao in todos:
                cartao["_cartao"].pack(side="left", fill="both", expand=True, padx=5)
