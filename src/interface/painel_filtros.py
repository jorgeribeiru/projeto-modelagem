"""Barra lateral com os filtros: curvas visíveis, intervalo de x, escalas, tipo de erro e passo h."""
from collections.abc import Callable

import customtkinter as ctk

from src.contratos import CenarioComparacao
from src.interface import tema
from src.interface.estado import PASSOS_DISPONIVEIS, EstadoFiltros
from src.visualizacao import (
    ERRO_ABSOLUTO,
    ERRO_RELATIVO,
    ESCALA_LINEAR,
    ESCALA_LOG,
    NOME_EULER,
    NOME_EXATA,
    NOME_RK4,
    ROTULOS_ERRO,
    nomes_das_curvas,
)

DESCRICOES_CURVA = {
    NOME_EXATA: "curva analítica φ(x)",
    NOME_EULER: "1ª ordem · erro global ~ h",
    NOME_RK4: "4ª ordem · erro global ~ h⁴",
}
ROTULOS_ESCALA = {ESCALA_LINEAR: "Linear", ESCALA_LOG: "Log"}
ROTULOS_TIPO_ERRO = {ERRO_ABSOLUTO: "Absoluto", ERRO_RELATIVO: "Relativo"}


def _inverter(mapa: dict[str, str]) -> dict[str, str]:
    return {v: k for k, v in mapa.items()}


def _formatar_passo(h: float) -> str:
    return f"{h:g}"


class PainelFiltros(ctk.CTkScrollableFrame):
    """Cada seção é um cartão com borda própria, para que o guia possa destacá-la."""

    def __init__(
        self,
        master,
        cenario: CenarioComparacao,
        estado: EstadoFiltros,
        fontes: tema.Fontes,
        ao_mudar: Callable[[], None],
        ao_mudar_passo: Callable[[float], None],
        ao_restaurar: Callable[[], None],
    ) -> None:
        super().__init__(master, width=300, fg_color="transparent", corner_radius=0,
                         scrollbar_button_color=tema.BORDA, scrollbar_button_hover_color=tema.SEGMENTO_HOVER)
        self.cenario = cenario
        self.estado = estado
        self.fontes = fontes
        self.ao_mudar = ao_mudar
        self.ao_mudar_passo = ao_mudar_passo
        self.ao_restaurar = ao_restaurar
        self.limites = (cenario.pvi.x0, cenario.pvi.x_fim)
        self.secoes: dict[str, ctk.CTkFrame] = {}
        self._previas: dict[str, ctk.CTkCanvas] = {}
        self._switches: dict[str, ctk.CTkSwitch] = {}

        self._criar_secao_curvas()
        self._criar_secao_intervalo()
        self._criar_secao_exibicao()
        self._criar_secao_passo()

        ctk.CTkButton(
            self, text="Restaurar padrão", command=self.ao_restaurar, height=36, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=tema.BORDA, text_color=tema.TEXTO,
            hover_color=tema.SEGMENTO_HOVER, font=fontes.corpo_forte,
        ).pack(fill="x", padx=(2, 8), pady=(4, 12))

        self.sincronizar()

    # ---------- construção ----------

    def _secao(self, chave: str, titulo: str, subtitulo: str) -> ctk.CTkFrame:
        cartao = ctk.CTkFrame(self, fg_color=tema.CARTAO, corner_radius=14, border_width=2,
                              border_color=tema.BORDA)
        cartao.pack(fill="x", padx=(2, 8), pady=(0, 10))
        ctk.CTkLabel(cartao, text=titulo.upper(), font=self.fontes.rotulo, text_color=tema.DESTAQUE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(cartao, text=subtitulo, font=self.fontes.pequena, text_color=tema.TEXTO_SUAVE,
                     anchor="w", justify="left", wraplength=250).pack(fill="x", padx=16, pady=(0, 8))
        corpo = ctk.CTkFrame(cartao, fg_color="transparent")
        corpo.pack(fill="x", padx=16, pady=(0, 12))
        self.secoes[chave] = cartao
        return corpo

    def _segmentado(self, master, valores: list[str], comando: Callable[[str], None]) -> ctk.CTkSegmentedButton:
        return ctk.CTkSegmentedButton(
            master, values=valores, command=comando, height=32, corner_radius=9,
            font=self.fontes.corpo, fg_color=tema.SEGMENTO_FUNDO,
            selected_color=tema.PRIMARIO, selected_hover_color=tema.PRIMARIO_HOVER,
            unselected_color=tema.SEGMENTO_FUNDO, unselected_hover_color=tema.SEGMENTO_HOVER,
            text_color=(tema.TEXTO[0], tema.TEXTO[1]),
        )

    def _criar_secao_curvas(self) -> None:
        corpo = self._secao("curvas", "Curvas", "Escolha quais soluções aparecem nos gráficos.")
        for nome in nomes_das_curvas(self.cenario):
            linha = ctk.CTkFrame(corpo, fg_color="transparent")
            linha.pack(fill="x", pady=3)

            previa = ctk.CTkCanvas(linha, width=46, height=22, highlightthickness=0, bd=0)
            previa.pack(side="left", padx=(0, 10))
            self._previas[nome] = previa

            textos = ctk.CTkFrame(linha, fg_color="transparent")
            textos.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(textos, text=nome, font=self.fontes.corpo_forte, text_color=tema.TEXTO,
                         anchor="w", height=18).pack(fill="x")
            ctk.CTkLabel(textos, text=DESCRICOES_CURVA.get(nome, ""), font=self.fontes.pequena,
                         text_color=tema.TEXTO_SUAVE, anchor="w", height=16).pack(fill="x")

            switch = ctk.CTkSwitch(
                linha, text="", width=44, switch_width=40, switch_height=22, border_width=3,
                progress_color=tema.cor_curva(nome), button_color=("#FFFFFF", "#E7EAF3"),
                button_hover_color=("#F4F4F5", "#FFFFFF"), fg_color=tema.SEGMENTO_FUNDO,
                command=lambda n=nome: self._alternar_curva(n),
            )
            switch.pack(side="right")
            self._switches[nome] = switch

    def _criar_secao_intervalo(self) -> None:
        corpo = self._secao("intervalo", "Intervalo de x", "Aproxime uma região do domínio para examiná-la.")
        x0, x_fim = self.limites

        campos = ctk.CTkFrame(corpo, fg_color="transparent")
        campos.pack(fill="x")
        self._sliders: dict[str, ctk.CTkSlider] = {}
        self._entradas: dict[str, ctk.CTkEntry] = {}
        for chave, rotulo in (("min", "de"), ("max", "até")):
            ctk.CTkLabel(campos, text=rotulo, font=self.fontes.corpo, text_color=tema.TEXTO_SUAVE).pack(
                side="left", padx=(0 if chave == "min" else 12, 6))
            entrada = ctk.CTkEntry(campos, width=76, height=28, corner_radius=8, justify="center",
                                   font=self.fontes.numero, border_color=tema.BORDA, fg_color=tema.CARTAO_ELEVADO,
                                   text_color=tema.TEXTO)
            entrada.pack(side="left")
            entrada.bind("<Return>", lambda _e: self._aplicar_entradas())
            entrada.bind("<FocusOut>", lambda _e: self._aplicar_entradas())
            self._entradas[chave] = entrada

        for chave in ("min", "max"):
            slider = ctk.CTkSlider(corpo, from_=x0, to=x_fim, height=16,
                                   progress_color=tema.PRIMARIO if chave == "max" else tema.SEGMENTO_FUNDO,
                                   button_color=tema.PRIMARIO, button_hover_color=tema.PRIMARIO_HOVER,
                                   fg_color=tema.SEGMENTO_FUNDO if chave == "max" else tema.PRIMARIO,
                                   command=lambda _v: self._aplicar_sliders())
            slider.pack(fill="x", pady=(10, 0))
            self._sliders[chave] = slider

        atalhos = ctk.CTkFrame(corpo, fg_color="transparent")
        atalhos.pack(fill="x", pady=(12, 0))
        largura = x_fim - x0
        faixas = [
            ("Tudo", x0, x_fim),
            (f"{x0:g}–{x0 + 0.2 * largura:g}", x0, x0 + 0.2 * largura),
            (f"{x0 + 0.2 * largura:g}–{x0 + 0.6 * largura:g}", x0 + 0.2 * largura, x0 + 0.6 * largura),
            (f"{x0 + 0.6 * largura:g}–{x_fim:g}", x0 + 0.6 * largura, x_fim),
        ]
        for coluna, (texto, a, b) in enumerate(faixas):
            atalhos.grid_columnconfigure(coluna, weight=1)
            ctk.CTkButton(
                atalhos, text=texto, height=26, width=10, corner_radius=8, font=self.fontes.pequena,
                fg_color=tema.SEGMENTO_FUNDO, hover_color=tema.SEGMENTO_HOVER, text_color=tema.TEXTO,
                command=lambda a=a, b=b: self._definir_intervalo(a, b),
            ).grid(row=0, column=coluna, sticky="ew", padx=2)

    def _criar_secao_exibicao(self) -> None:
        corpo = self._secao("exibicao", "Exibição",
                            "Escala Log compara erros de ordens de grandeza diferentes.")
        self._seg_escala: dict[str, ctk.CTkSegmentedButton] = {}
        for chave, rotulo in (("escala_y", "Soluções y(x)"), ("escala_erro", "Erro")):
            linha = ctk.CTkFrame(corpo, fg_color="transparent")
            linha.pack(fill="x", pady=(0, 8))
            ctk.CTkLabel(linha, text=rotulo, font=self.fontes.corpo, text_color=tema.TEXTO,
                         anchor="w").pack(side="left")
            segmentado = self._segmentado(
                linha, list(ROTULOS_ESCALA.values()),
                lambda valor, c=chave: self._definir(c, _inverter(ROTULOS_ESCALA)[valor]),
            )
            segmentado.pack(side="right")
            self._seg_escala[chave] = segmentado

        linha = ctk.CTkFrame(corpo, fg_color="transparent")
        linha.pack(fill="x")
        ctk.CTkLabel(linha, text="Tipo de erro", font=self.fontes.corpo, text_color=tema.TEXTO,
                     anchor="w").pack(side="left")
        self._seg_tipo_erro = self._segmentado(
            linha, list(ROTULOS_TIPO_ERRO.values()),
            lambda valor: self._definir("tipo_erro", _inverter(ROTULOS_TIPO_ERRO)[valor]),
        )
        self._seg_tipo_erro.pack(side="right")
        self._formula_erro = ctk.CTkLabel(corpo, text="", font=self.fontes.numero, text_color=tema.TEXTO,
                                          fg_color=tema.CARTAO_ELEVADO, corner_radius=8, height=30)
        self._formula_erro.pack(fill="x", pady=(10, 0))

    def _criar_secao_passo(self) -> None:
        corpo = self._secao("passo", "Passo h", "Recalcula Euler e RK4 com outro espaçamento da malha.")
        self._seg_passo = self._segmentado(
            corpo, [_formatar_passo(h) for h in PASSOS_DISPONIVEIS],
            lambda valor: self.ao_mudar_passo(float(valor)),
        )
        self._seg_passo.pack(fill="x")
        self._info_passo = ctk.CTkLabel(corpo, text="", font=self.fontes.pequena, text_color=tema.TEXTO_SUAVE,
                                        anchor="w", justify="left", wraplength=250)
        self._info_passo.pack(fill="x", pady=(8, 0))

    # ---------- eventos ----------

    def _alternar_curva(self, nome: str) -> None:
        if self._switches[nome].get():
            self.estado.visiveis.add(nome)
        else:
            self.estado.visiveis.discard(nome)
        self._colorir_borda_switch(nome)
        self.ao_mudar()

    def _colorir_borda_switch(self, nome: str) -> None:
        """Sem a borda colorida, o botão branco do switch some contra o cartão branco do tema claro."""
        ligado = nome in self.estado.visiveis
        self._switches[nome].configure(border_color=tema.cor_curva(nome) if ligado else tema.SEGMENTO_FUNDO)

    def _definir(self, atributo: str, valor: str) -> None:
        setattr(self.estado, atributo, valor)
        self.sincronizar()
        self.ao_mudar()

    def _definir_intervalo(self, x_min: float, x_max: float) -> None:
        self.estado.definir_intervalo(x_min, x_max, self.limites)
        self.sincronizar()
        self.ao_mudar()

    def _aplicar_sliders(self) -> None:
        x_min, x_max = self._sliders["min"].get(), self._sliders["max"].get()
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        self._definir_intervalo(x_min, x_max)

    def _aplicar_entradas(self) -> None:
        try:
            x_min = float(self._entradas["min"].get().replace(",", "."))
            x_max = float(self._entradas["max"].get().replace(",", "."))
        except ValueError:
            self.sincronizar()
            return
        if (x_min, x_max) != (self.estado.x_min, self.estado.x_max):
            self._definir_intervalo(min(x_min, x_max), max(x_min, x_max))

    # ---------- sincronização ----------

    def sincronizar(self) -> None:
        """Reflete o `estado` atual em todos os widgets (após restaurar, trocar h ou o tema)."""
        for nome, switch in self._switches.items():
            switch.select() if nome in self.estado.visiveis else switch.deselect()
            self._colorir_borda_switch(nome)

        x0, x_fim = self.limites
        passos = max(1, round((x_fim - x0) / self.estado.h))
        for chave, valor in (("min", self.estado.x_min), ("max", self.estado.x_max)):
            self._sliders[chave].configure(number_of_steps=passos)
            self._sliders[chave].set(valor)
            entrada = self._entradas[chave]
            if self.focus_get() is not getattr(entrada, "_entry", None):
                entrada.delete(0, "end")
                entrada.insert(0, f"{valor:g}")

        self._seg_escala["escala_y"].set(ROTULOS_ESCALA[self.estado.escala_y])
        self._seg_escala["escala_erro"].set(ROTULOS_ESCALA[self.estado.escala_erro])
        self._seg_tipo_erro.set(ROTULOS_TIPO_ERRO[self.estado.tipo_erro])
        self._formula_erro.configure(text=ROTULOS_ERRO[self.estado.tipo_erro])

        rotulo_passo = _formatar_passo(self.estado.h)
        valores = [_formatar_passo(h) for h in PASSOS_DISPONIVEIS]
        if rotulo_passo not in valores:
            self._seg_passo.configure(values=[*valores, rotulo_passo])
        self._seg_passo.set(rotulo_passo)
        self._info_passo.configure(
            text=f"{passos + 1} nós na malha. Ao dividir h por 2, o erro do Euler cai ~2× e o do RK4 ~16×."
        )
        self.desenhar_previas()

    def desenhar_previas(self) -> None:
        """Miniatura do estilo de cada curva (cor, traço e marcador), igual ao do gráfico."""
        modo = self.estado.modo
        fundo = tema.resolver_cor(tema.CARTAO, modo)
        for nome, canvas in self._previas.items():
            cor = tema.resolver_cor(tema.cor_curva(nome), modo)
            canvas.configure(bg=fundo)
            canvas.delete("all")
            meio = 11
            if nome == NOME_EXATA:
                canvas.create_line(4, meio, 42, meio, fill=cor, width=4, capstyle="round")
            elif nome == NOME_EULER:
                canvas.create_line(4, meio, 42, meio, fill=cor, width=2, dash=(5, 3))
                for x in (8, 23, 38):
                    canvas.create_oval(x - 3, meio - 3, x + 3, meio + 3, fill=cor, outline=cor)
            elif nome == NOME_RK4:
                canvas.create_line(4, meio, 42, meio, fill=cor, width=2, dash=(3, 2))
                for x in (10, 23, 36):
                    canvas.create_oval(x - 5, meio - 5, x + 5, meio + 5, outline=cor, width=2)
            else:
                canvas.create_line(4, meio, 42, meio, fill=cor, width=2, dash=(2, 2))
