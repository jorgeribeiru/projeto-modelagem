"""Janela principal: cabeçalho, filtros, gráfico interativo, inspeção de pontos e guia."""
import tkinter
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.transforms import blended_transform_factory

from src.contratos import CenarioComparacao, FuncaoRecalculo
from src.interface import tema
from src.interface.estado import (
    EstadoFiltros,
    ResumoPonto,
    faixa_de_indices,
    formatar_numero,
    mover_indice,
    no_mais_proximo,
    resumo_ponto,
)
from src.interface.guia import ALVO_GRAFICO, ALVO_INSPETOR, SOBRE_GRAFICO, SOBRE_PAINEL_LATERAL, Guia, montar_passos
from src.interface.inspetor import CartaoInspecao, rotulo_no
from src.interface.painel_filtros import PainelFiltros
from src.visualizacao import (
    ERRO_RELATIVO,
    ESCALA_LOG,
    MODO_CLARO,
    MODO_ESCURO,
    NOME_EULER,
    NOME_EXATA,
    TEMAS,
    cor_da_curva,
    montar_figura_comparacao,
    plotar_comparacao,
)

ATRASO_REDESENHO_MS = 30
ROTULOS_MODO = {MODO_CLARO: "Claro", MODO_ESCURO: "Escuro"}


class AplicativoAnalise(ctk.CTk):
    def __init__(
        self,
        cenario: CenarioComparacao,
        recalcular: FuncaoRecalculo,
        mostrar_guia: bool = True,
        pasta_exportacao: Path | None = None,
    ) -> None:
        ctk.set_appearance_mode(tema.MODOS_CTK[MODO_CLARO])
        super().__init__(fg_color=tema.FUNDO)
        self.title("Análise do PVI · Exata × Euler × Runge-Kutta")
        self.geometry("1480x940")
        self.minsize(1180, 760)

        self.cenario = cenario
        self.recalcular = recalcular
        self._h_inicial = cenario.pvi.h
        self.pasta_exportacao = pasta_exportacao or Path.cwd()
        self.estado = EstadoFiltros.padrao(cenario)
        self.fontes = tema.criar_fontes()
        self.guia: Guia | None = None
        self._redesenho_agendado: str | None = None
        self._artistas_inspecao: list = []
        self._inspecao_agendada: str | None = None
        self._fundo_grafico = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._criar_cabecalho()
        self.coluna_lateral = ctk.CTkFrame(self, fg_color="transparent")
        self.coluna_lateral.grid(row=1, column=0, sticky="nsw", padx=(20, 4), pady=(0, 8))
        self.painel = PainelFiltros(
            self.coluna_lateral, cenario, self.estado, self.fontes,
            ao_mudar=self._agendar_redesenho,
            ao_mudar_passo=self._mudar_passo,
            ao_restaurar=self._restaurar,
        )
        self.painel.pack(fill="both", expand=True)
        self._criar_area_grafico()
        self._criar_barra_status()
        self._ligar_teclado()

        self._redesenhar()
        if mostrar_guia:
            self.after(350, self.abrir_guia)

    # ---------- construção ----------

    def _criar_cabecalho(self) -> None:
        f = self.fontes
        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, columnspan=2, sticky="ew", padx=22, pady=(18, 14))

        ctk.CTkLabel(cabecalho, text="y′", width=44, height=44, corner_radius=12, fg_color=tema.PRIMARIO,
                     text_color=tema.SOBRE_DESTAQUE, font=f.titulo).pack(side="left")
        textos = ctk.CTkFrame(cabecalho, fg_color="transparent")
        textos.pack(side="left", padx=14)
        ctk.CTkLabel(textos, text="Análise do PVI  ·  Euler × Runge-Kutta", font=f.titulo,
                     text_color=tema.TEXTO, anchor="w", height=24).pack(fill="x")
        chips = ctk.CTkFrame(textos, fg_color="transparent")
        chips.pack(fill="x", pady=(4, 0))
        for texto in (self.cenario.equacao, self.cenario.solucao_exata_texto,
                      f"x ∈ [{self.cenario.pvi.x0:g}, {self.cenario.pvi.x_fim:g}]"):
            if texto:
                ctk.CTkLabel(chips, text=texto, font=f.pequena, text_color=tema.TEXTO_SUAVE, height=24,
                             fg_color=tema.CARTAO, corner_radius=8).pack(side="left", padx=(0, 6), ipadx=8)

        ctk.CTkButton(cabecalho, text="Exportar figura", height=38, corner_radius=10, font=f.corpo_forte,
                      fg_color=tema.PRIMARIO, hover_color=tema.PRIMARIO_HOVER, text_color=tema.SOBRE_DESTAQUE,
                      command=self._exportar).pack(side="right")
        ctk.CTkButton(cabecalho, text="?  Guia", width=90, height=38, corner_radius=10, font=f.corpo_forte,
                      fg_color=tema.CARTAO, hover_color=tema.SEGMENTO_HOVER, text_color=tema.TEXTO,
                      border_width=1, border_color=tema.BORDA,
                      command=self.abrir_guia).pack(side="right", padx=10)
        self._seg_modo = ctk.CTkSegmentedButton(
            cabecalho, values=list(ROTULOS_MODO.values()), command=self._mudar_modo, height=38,
            corner_radius=10, font=f.corpo, fg_color=tema.SEGMENTO_FUNDO, selected_color=tema.CARTAO,
            selected_hover_color=tema.CARTAO, unselected_color=tema.SEGMENTO_FUNDO,
            unselected_hover_color=tema.SEGMENTO_HOVER, text_color=tema.TEXTO,
        )
        self._seg_modo.set(ROTULOS_MODO[self.estado.modo])
        self._seg_modo.pack(side="right")

    def _criar_area_grafico(self) -> None:
        f = self.fontes
        area = ctk.CTkFrame(self, fg_color="transparent")
        area.grid(row=1, column=1, sticky="nsew", padx=(8, 20), pady=(0, 8))
        area.grid_columnconfigure(0, weight=1)
        area.grid_rowconfigure(0, weight=1)

        self.cartao_grafico = ctk.CTkFrame(area, fg_color=tema.CARTAO, corner_radius=16, border_width=2,
                                           border_color=tema.BORDA)
        self.cartao_grafico.grid(row=0, column=0, sticky="nsew")

        topo = ctk.CTkFrame(self.cartao_grafico, fg_color="transparent")
        topo.pack(fill="x", padx=20, pady=(14, 0))
        ctk.CTkLabel(topo, text="Gráfico comparativo", font=f.corpo_forte, text_color=tema.TEXTO).pack(side="left")
        ctk.CTkLabel(topo, text="Clique para inspecionar um nó  ·  ← → navegam  ·  Esc limpa",
                     font=f.pequena, text_color=tema.TEXTO_SUAVE).pack(side="right")

        self.figura = Figure(figsize=(9, 6), dpi=100, layout="constrained")
        self.canvas = FigureCanvasTkAgg(self.figura, master=self.cartao_grafico)
        widget = self.canvas.get_tk_widget()
        widget.configure(highlightthickness=0, bd=0, cursor="crosshair")
        widget.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        self.canvas.mpl_connect("button_press_event", self._ao_clicar)
        self.canvas.mpl_connect("motion_notify_event", self._ao_mover_cursor)
        self.canvas.mpl_connect("figure_leave_event", lambda _e: self._mostrar_cursor(""))
        self.canvas.mpl_connect("draw_event", self._ao_desenhar_figura)

        self.inspetor = CartaoInspecao(area, self.cenario, f, ao_navegar=self._navegar)
        self.inspetor.grid(row=1, column=0, sticky="ew", pady=(12, 0))

    def _criar_barra_status(self) -> None:
        barra = ctk.CTkFrame(self, fg_color="transparent", height=28)
        barra.grid(row=2, column=0, columnspan=2, sticky="ew", padx=24, pady=(0, 10))
        self._status_mensagem = ctk.CTkLabel(barra, text="", font=self.fontes.pequena,
                                             text_color=tema.TEXTO_SUAVE, anchor="w")
        self._status_mensagem.pack(side="left")
        self._status_resumo = ctk.CTkLabel(barra, text="", font=self.fontes.pequena,
                                           text_color=tema.TEXTO_SUAVE, anchor="e")
        self._status_resumo.pack(side="right")
        self._status_cursor = ctk.CTkLabel(barra, text="", font=self.fontes.numero,
                                           text_color=tema.TEXTO, anchor="e")
        self._status_cursor.pack(side="right", padx=20)

    def _ligar_teclado(self) -> None:
        self.bind_all("<Left>", lambda e: self._tecla_navegacao(e, -1))
        self.bind_all("<Right>", lambda e: self._tecla_navegacao(e, 1))
        self.bind_all("<Home>", lambda e: self._tecla_navegacao(e, -10**6))
        self.bind_all("<End>", lambda e: self._tecla_navegacao(e, 10**6))
        self.bind("<Escape>", self._limpar_selecao, add="+")

    # ---------- desenho ----------

    @property
    def malha(self) -> list[float]:
        return self.cenario.resultados[0].x

    def _agendar_redesenho(self) -> None:
        """Agrupa eventos rápidos (ex.: arrastar o slider) em um único redesenho."""
        if self._redesenho_agendado is not None:
            self.after_cancel(self._redesenho_agendado)
        self._redesenho_agendado = self.after(ATRASO_REDESENHO_MS, self._redesenhar)

    def _redesenhar(self) -> None:
        self._redesenho_agendado = None
        self.canvas.get_tk_widget().configure(bg=TEMAS[self.estado.modo].painel)
        _, self.ax_solucoes, self.ax_erro = montar_figura_comparacao(
            self.cenario, self.estado.opcoes_grafico(), fig=self.figura)
        self._artistas_inspecao = []
        self._fundo_grafico = None
        self._manter_selecao_no_intervalo()
        self._atualizar_inspecao()
        self.canvas.draw_idle()

    def _agendar_inspecao(self) -> None:
        """Teclas e cliques só mudam o índice; a parte visual roda uma vez quando a fila de eventos
        esvazia. Assim a repetição automática do teclado não empilha redesenhos atrasados."""
        if self._inspecao_agendada is None:
            self._inspecao_agendada = self.after_idle(self._aplicar_inspecao_agendada)

    def _aplicar_inspecao_agendada(self) -> None:
        self._inspecao_agendada = None
        self._atualizar_inspecao()
        self._blit_inspecao()

    def _atualizar_inspecao(self) -> None:
        indice = self.estado.indice_inspecionado
        resumo = resumo_ponto(self.cenario, indice) if indice is not None else None
        self.inspetor.atualizar(resumo)
        self._atualizar_status()
        self._recriar_artistas_inspecao(resumo)

    def _blit_inspecao(self) -> None:
        """Repinta só a seleção sobre o fundo em cache, sem redesenhar a figura inteira."""
        if self._fundo_grafico is None:
            self.canvas.draw_idle()
            return
        self.canvas.restore_region(self._fundo_grafico)
        self._desenhar_artistas_inspecao()
        self.canvas.blit(self.figura.bbox)

    def _ao_desenhar_figura(self, _evento) -> None:
        """Após cada desenho completo (filtros, tema, redimensionamento), guarda o fundo sem a seleção."""
        self._fundo_grafico = self.canvas.copy_from_bbox(self.figura.bbox)
        self._desenhar_artistas_inspecao()

    def _desenhar_artistas_inspecao(self) -> None:
        for artista in sorted(self._artistas_inspecao, key=lambda a: a.get_zorder()):
            self.figura.draw_artist(artista)

    def _manter_selecao_no_intervalo(self) -> None:
        indice = self.estado.indice_inspecionado
        if indice is None:
            return
        inicio, fim = faixa_de_indices(self.malha, self.estado.x_min, self.estado.x_max)
        self.estado.indice_inspecionado = min(max(indice, inicio), fim)

    def _recriar_artistas_inspecao(self, resumo: ResumoPonto | None) -> None:
        """Os artistas da seleção são `animated`: ficam fora do desenho completo e são pintados por blit."""
        for artista in self._artistas_inspecao:
            artista.remove()
        self._artistas_inspecao = []
        if resumo is None:
            return

        modo = self.estado.modo
        destaque = TEMAS[modo].destaque
        fundo = TEMAS[modo].painel
        visiveis = self.estado.visiveis
        x = resumo.x
        novos = self._artistas_inspecao

        for ax in (self.ax_solucoes, self.ax_erro):
            novos.append(ax.axvline(x, color=destaque, linewidth=1.3, linestyle=(0, (4, 3)), alpha=0.9, zorder=1))

        transformacao = blended_transform_factory(self.ax_erro.transData, self.ax_erro.transAxes)
        novos.append(self.ax_erro.annotate(
            f"{rotulo_no(resumo.indice)} = {x:g}", xy=(x, 0), xycoords=transformacao, xytext=(0, -5),
            textcoords="offset points", ha="center", va="top", fontsize=9.5, fontweight="bold",
            color="white", zorder=10, annotation_clip=False,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": destaque, "edgecolor": "none"},
        ))

        if NOME_EXATA in visiveis:
            novos.extend(self.ax_solucoes.plot(
                x, resumo.exato, marker="o", markersize=11, markerfacecolor=fundo,
                markeredgecolor=cor_da_curva(NOME_EXATA, modo), markeredgewidth=2.5, zorder=8))

        erros_ativos = (self.cenario.erros_relativos if self.estado.tipo_erro == ERRO_RELATIVO
                        else self.cenario.erros_absolutos)
        for metodo in resumo.metodos:
            if metodo.nome not in visiveis:
                continue
            cor = cor_da_curva(metodo.nome, modo)
            novos.extend(self.ax_solucoes.plot(
                x, metodo.y, marker="o", markersize=8, color=cor, markeredgecolor=fundo,
                markeredgewidth=1.8, zorder=9))
            # Barra vertical entre a solução exata e o método: o erro visto como distância.
            if metodo.erro_absoluto > 0:
                novos.append(self.ax_solucoes.annotate(
                    "", xy=(x, metodo.y), xytext=(x, resumo.exato), zorder=7,
                    arrowprops={"arrowstyle": "-", "color": cor, "linewidth": 3, "alpha": 0.55}))

            erro = erros_ativos[metodo.nome][resumo.indice]
            if erro > 0 or self.estado.escala_erro != ESCALA_LOG:
                novos.extend(self.ax_erro.plot(
                    x, erro, marker="o", markersize=8, color=cor, markeredgecolor=fundo,
                    markeredgewidth=1.8, zorder=9))
                novos.append(self.ax_erro.annotate(
                    formatar_numero(erro), xy=(x, erro), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=cor, fontweight="bold", zorder=10,
                    bbox={"boxstyle": "round,pad=0.25", "facecolor": fundo, "edgecolor": "none", "alpha": 0.85}))

        for artista in novos:
            artista.set_animated(True)

    # ---------- interação ----------

    def _ao_clicar(self, evento) -> None:
        self.canvas.get_tk_widget().focus_set()
        if evento.button != 1 or evento.inaxes not in (self.ax_solucoes, self.ax_erro) or evento.xdata is None:
            return
        self._selecionar(no_mais_proximo(self.malha, evento.xdata))

    def _selecionar(self, indice: int) -> None:
        self.estado.indice_inspecionado = indice
        self._manter_selecao_no_intervalo()
        self._agendar_inspecao()

    def _navegar(self, delta: int) -> None:
        inicio, fim = faixa_de_indices(self.malha, self.estado.x_min, self.estado.x_max)
        atual = self.estado.indice_inspecionado
        if atual is None:
            atual = inicio if delta > 0 else fim
            delta = 0
        self._selecionar(mover_indice(atual, delta, inicio, fim))

    def _tecla_navegacao(self, evento, delta: int) -> None:
        # Setas dentro de um campo de texto movem o cursor, não a seleção.
        if isinstance(evento.widget, tkinter.Entry):
            return
        self._navegar(delta)

    def _limpar_selecao(self, _evento=None) -> None:
        if self.guia is not None:
            return
        self.estado.indice_inspecionado = None
        self._agendar_inspecao()

    def _ao_mover_cursor(self, evento) -> None:
        if evento.inaxes is self.ax_solucoes and evento.ydata is not None:
            self._mostrar_cursor(f"x = {evento.xdata:.3f}   y(x) = {formatar_numero(evento.ydata)}")
        elif evento.inaxes is self.ax_erro and evento.ydata is not None:
            self._mostrar_cursor(f"x = {evento.xdata:.3f}   erro = {formatar_numero(evento.ydata)}")
        else:
            self._mostrar_cursor("")

    def _mostrar_cursor(self, texto: str) -> None:
        self._status_cursor.configure(text=texto)

    def _mudar_passo(self, h: float) -> None:
        if abs(h - self.estado.h) < 1e-12:
            return
        x_selecionado = (self.malha[self.estado.indice_inspecionado]
                         if self.estado.indice_inspecionado is not None else None)
        self.cenario = self.recalcular(h)
        self.painel.cenario = self.cenario
        self.estado.h = h
        self.estado.definir_intervalo(self.estado.x_min, self.estado.x_max, self.painel.limites)
        if x_selecionado is not None:
            self.estado.indice_inspecionado = no_mais_proximo(self.malha, x_selecionado)
        self.painel.sincronizar()
        self._redesenhar()
        self._avisar(f"Métodos recalculados com h = {h:g} ({len(self.malha)} nós).")

    def _restaurar(self) -> None:
        if abs(self.cenario.pvi.h - self._h_inicial) > 1e-12:
            self.cenario = self.recalcular(self._h_inicial)
            self.painel.cenario = self.cenario
        novo = EstadoFiltros.padrao(self.cenario, self.estado.modo)
        for campo, valor in vars(novo).items():
            setattr(self.estado, campo, valor)
        self.painel.sincronizar()
        self._redesenhar()
        self._avisar("Filtros restaurados.")

    def _mudar_modo(self, rotulo: str) -> None:
        modo = {v: k for k, v in ROTULOS_MODO.items()}[rotulo]
        self.estado.modo = modo
        ctk.set_appearance_mode(tema.MODOS_CTK[modo])
        self.painel.desenhar_previas()
        self._redesenhar()

    def _exportar(self) -> None:
        caminho = filedialog.asksaveasfilename(
            parent=self, title="Exportar figura", initialdir=self.pasta_exportacao,
            initialfile="comparacao_pvi.png", defaultextension=".png",
            filetypes=[("Imagem PNG", "*.png"), ("Documento PDF", "*.pdf"), ("Vetorial SVG", "*.svg")],
        )
        if not caminho:
            return
        destino = Path(caminho)
        opcoes = self.estado.opcoes_grafico()
        opcoes.modo = MODO_CLARO
        opcoes.destacar_eixos = False
        formato = destino.suffix.lstrip(".").lower() or "png"
        plotar_comparacao(self.cenario, destino, opcoes, formatos=(formato,))
        self._avisar(f"Figura exportada em {destino}")

    # ---------- guia ----------

    def abrir_guia(self) -> None:
        if self.guia is not None:
            return
        passos = montar_passos(self.cenario, self._destacar_eixos, self._selecionar_ponto_demonstracao)
        alvos = {ALVO_GRAFICO: self.cartao_grafico, ALVO_INSPETOR: self.inspetor, **self.painel.secoes}
        ancoras = {SOBRE_PAINEL_LATERAL: self.coluna_lateral, SOBRE_GRAFICO: self.cartao_grafico}
        self.guia = Guia(self, passos, alvos, ancoras, self.fontes, ao_fechar=self._ao_fechar_guia)

    def _ao_fechar_guia(self) -> None:
        self.guia = None
        self.canvas.get_tk_widget().focus_set()

    def _destacar_eixos(self, ativo: bool) -> None:
        self.estado.destacar_eixos = ativo
        self._redesenhar()

    def _selecionar_ponto_demonstracao(self) -> None:
        if self.estado.indice_inspecionado is not None:
            return
        erros = self.cenario.erros_absolutos.get(NOME_EULER)
        if not erros:
            return
        inicio, fim = faixa_de_indices(self.malha, self.estado.x_min, self.estado.x_max)
        self._selecionar(max(range(inicio, fim + 1), key=lambda i: erros[i]))

    # ---------- status ----------

    def _atualizar_status(self) -> None:
        self._status_resumo.configure(
            text=f"h = {self.estado.h:g}  ·  {len(self.malha)} nós  ·  "
                 f"intervalo [{self.estado.x_min:g}, {self.estado.x_max:g}]"
        )

    def _avisar(self, mensagem: str) -> None:
        self._status_mensagem.configure(text=mensagem)
