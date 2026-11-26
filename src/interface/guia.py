"""Guia de boas-vindas (onboarding) em passos, com destaque pulsante no componente explicado."""
from collections.abc import Callable
from dataclasses import dataclass

import tkinter

import customtkinter as ctk

from src.contratos import CenarioComparacao
from src.interface import tema

ALVO_GRAFICO = "grafico"
ALVO_INSPETOR = "inspetor"
ALVOS_FILTROS = ("intervalo", "exibicao", "passo")

# Onde o cartão do guia fica para não cobrir o componente destacado.
SOBRE_PAINEL_LATERAL = "painel"
SOBRE_GRAFICO = "grafico"
CENTRO = "centro"

LARGURA_CARTAO = 400
INTERVALO_PULSO_MS = 550


@dataclass
class Passo:
    titulo: str
    texto: str
    dica: str = ""
    alvos: tuple[str, ...] = ()
    posicao: str = CENTRO
    ao_entrar: Callable[[], None] | None = None
    ao_sair: Callable[[], None] | None = None


def montar_passos(
    cenario: CenarioComparacao,
    destacar_eixos: Callable[[bool], None],
    selecionar_ponto_demonstracao: Callable[[], None],
) -> list[Passo]:
    pvi = cenario.pvi
    return [
        Passo(
            titulo="Bem-vindo à análise do PVI",
            texto=(
                f"Vamos comparar três soluções de  {cenario.equacao}  no intervalo "
                f"[{pvi.x0:g}, {pvi.x_fim:g}]:\n\n"
                f"•  Solução exata  {cenario.solucao_exata_texto}\n"
                "•  Método de Euler (1ª ordem)\n"
                "•  Runge-Kutta clássico, RK4 (4ª ordem)"
            ),
            dica="Leva menos de um minuto. Você pode reabrir este guia pelo botão “Guia” no topo.",
        ),
        Passo(
            titulo="Como ler os eixos",
            texto=(
                "O eixo horizontal é x, a variável independente, compartilhado pelos dois painéis.\n\n"
                "No painel de cima, o eixo vertical é y(x): o valor de cada solução.\n\n"
                "No painel de baixo, o eixo vertical é o erro de cada método em relação à solução exata, "
                "medido em cada nó xₙ da malha."
            ),
            dica="Os eixos ficam destacados em roxo enquanto este passo estiver aberto.",
            alvos=(ALVO_GRAFICO,),
            posicao=SOBRE_PAINEL_LATERAL,
            ao_entrar=lambda: destacar_eixos(True),
            ao_sair=lambda: destacar_eixos(False),
        ),
        Passo(
            titulo="Escolha as curvas",
            texto=(
                "Ligue e desligue cada curva. A Exata é uma linha contínua; o Euler é tracejado com pontos "
                "cheios; o RK4 tem tracejado curto com círculos vazados, praticamente em cima da Exata."
            ),
            dica="Desligue a Exata e veja o RK4 desenhar sozinho a mesma curva.",
            alvos=("curvas",),
            posicao=SOBRE_GRAFICO,
        ),
        Passo(
            titulo="Filtre o que importa",
            texto=(
                "•  Intervalo de x: aproxime uma região (o Euler erra mais perto de x = 0,5).\n"
                "•  Escala Log: necessária para ver o erro do RK4 (~10⁻⁵) ao lado do Euler (~10⁻¹).\n"
                "•  Erro absoluto ou relativo ao valor exato.\n"
                "•  Passo h: recalcula os dois métodos com outra malha."
            ),
            dica="Ao trocar h de 0.1 para 0.05, o erro do Euler cai ~2× e o do RK4 ~16×: são as ordens 1 e 4.",
            alvos=ALVOS_FILTROS,
            posicao=SOBRE_GRAFICO,
        ),
        Passo(
            titulo="Inspecione um ponto",
            texto=(
                "Clique em qualquer lugar do gráfico: a seleção salta para o nó mais próximo da malha. "
                "Use ← e → para andar nó a nó.\n\n"
                "O cartão abaixo do gráfico mostra φ(xₙ), o valor de cada método, os erros e quantas vezes "
                "um método erra mais que o outro."
            ),
            dica="Já selecionamos o nó onde o Euler tem o maior erro. Esc limpa a seleção.",
            alvos=(ALVO_GRAFICO, ALVO_INSPETOR),
            posicao=SOBRE_PAINEL_LATERAL,
            ao_entrar=selecionar_ponto_demonstracao,
        ),
        Passo(
            titulo="Tudo pronto!",
            texto=(
                "Explore à vontade. Quando quiser registrar uma visão no relatório, use “Exportar figura”: "
                "o gráfico é salvo em alta resolução com os filtros atuais."
            ),
        ),
    ]


class Guia(ctk.CTkFrame):
    """Cartão sobreposto à janela (via `place`), não um Toplevel: evita problemas de foco e de
    janela sem borda em gerenciadores de janela do Linux."""

    def __init__(
        self,
        janela: ctk.CTk,
        passos: list[Passo],
        alvos: dict[str, ctk.CTkFrame],
        ancoras: dict[str, ctk.CTkBaseClass],
        fontes: tema.Fontes,
        ao_fechar: Callable[[], None],
    ) -> None:
        super().__init__(janela, width=LARGURA_CARTAO, fg_color=tema.CARTAO, corner_radius=18,
                         border_width=2, border_color=tema.DESTAQUE_PULSO)
        self.janela = janela
        self.passos = passos
        self.alvos = alvos
        self.ancoras = ancoras
        self.fontes = fontes
        self.ao_fechar = ao_fechar
        self.indice = 0
        self._pulso_id: str | None = None
        self._pulso_aceso = False
        self._bordas_originais = {chave: alvo.cget("border_color") for chave, alvo in alvos.items()}

        self._montar_layout()
        self._teclas = [
            (sequencia, janela.bind(sequencia, funcao, add="+"))
            for sequencia, funcao in (("<Return>", lambda _e: self.avancar()),
                                      ("<Escape>", lambda _e: self.fechar()))
        ]
        self._mostrar_passo()

    def _montar_layout(self) -> None:
        f = self.fontes
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=22, pady=(18, 0))
        ctk.CTkLabel(topo, text="GUIA RÁPIDO", font=f.rotulo, text_color=tema.DESTAQUE).pack(side="left")
        ctk.CTkButton(topo, text="✕", width=28, height=28, corner_radius=8, font=f.corpo,
                      fg_color="transparent", hover_color=tema.SEGMENTO_HOVER, text_color=tema.TEXTO_SUAVE,
                      command=self.fechar).pack(side="right")
        self._contador = ctk.CTkLabel(topo, text="", font=f.pequena, text_color=tema.TEXTO_SUAVE)
        self._contador.pack(side="right", padx=8)

        self._progresso = ctk.CTkFrame(self, fg_color="transparent")
        self._progresso.pack(fill="x", padx=22, pady=(8, 0))
        self._segmentos = []
        for i in range(len(self.passos)):
            self._progresso.grid_columnconfigure(i, weight=1)
            segmento = ctk.CTkFrame(self._progresso, width=12, height=5, corner_radius=3, fg_color=tema.BORDA)
            segmento.grid(row=0, column=i, sticky="ew", padx=2)
            self._segmentos.append(segmento)

        self._titulo = ctk.CTkLabel(self, text="", font=f.guia_titulo, text_color=tema.TEXTO, anchor="w",
                                    justify="left", wraplength=LARGURA_CARTAO - 44)
        self._titulo.pack(fill="x", padx=22, pady=(16, 6))
        self._texto = ctk.CTkLabel(self, text="", font=f.corpo, text_color=tema.TEXTO, anchor="w",
                                   justify="left", wraplength=LARGURA_CARTAO - 44)
        self._texto.pack(fill="x", padx=22)

        self._caixa_dica = ctk.CTkFrame(self, fg_color=tema.DESTAQUE_SUAVE, corner_radius=12)
        self._dica = ctk.CTkLabel(self._caixa_dica, text="", font=f.pequena, text_color=tema.TEXTO,
                                  anchor="w", justify="left", wraplength=LARGURA_CARTAO - 76)
        self._dica.pack(fill="x", padx=14, pady=10)

        self._rodape = ctk.CTkFrame(self, fg_color="transparent")
        self._rodape.pack(fill="x", padx=22, pady=(16, 18), side="bottom")
        self._pular = ctk.CTkButton(self._rodape, text="Pular guia", width=10, height=34, font=f.corpo,
                                    fg_color="transparent", hover_color=tema.SEGMENTO_HOVER,
                                    text_color=tema.TEXTO_SUAVE, command=self.fechar)
        self._pular.pack(side="left")
        self._proximo = ctk.CTkButton(self._rodape, text="Próximo", width=110, height=34, corner_radius=10,
                                      font=f.corpo_forte, fg_color=tema.PRIMARIO, hover_color=tema.PRIMARIO_HOVER,
                                      text_color=tema.SOBRE_DESTAQUE, command=self.avancar)
        self._proximo.pack(side="right")
        self._voltar = ctk.CTkButton(self._rodape, text="Voltar", width=80, height=34, corner_radius=10,
                                     font=f.corpo, fg_color=tema.SEGMENTO_FUNDO, hover_color=tema.SEGMENTO_HOVER,
                                     text_color=tema.TEXTO, command=self.voltar)
        self._voltar.pack(side="right", padx=8)

    # ---------- navegação ----------

    def avancar(self) -> None:
        if self.indice == len(self.passos) - 1:
            self.fechar()
            return
        self._sair_do_passo()
        self.indice += 1
        self._mostrar_passo()

    def voltar(self) -> None:
        if self.indice == 0:
            return
        self._sair_do_passo()
        self.indice -= 1
        self._mostrar_passo()

    def fechar(self) -> None:
        self._sair_do_passo()
        for sequencia, identificador in self._teclas:
            self.janela.unbind(sequencia, identificador)
        self.place_forget()
        self.destroy()
        self.ao_fechar()

    def _sair_do_passo(self) -> None:
        passo = self.passos[self.indice]
        self._parar_pulso()
        if passo.ao_sair:
            passo.ao_sair()

    def _mostrar_passo(self) -> None:
        passo = self.passos[self.indice]
        ultimo = self.indice == len(self.passos) - 1

        self._contador.configure(text=f"Passo {self.indice + 1} de {len(self.passos)}")
        for i, segmento in enumerate(self._segmentos):
            segmento.configure(fg_color=tema.DESTAQUE if i <= self.indice else tema.BORDA)
        self._titulo.configure(text=passo.titulo)
        self._texto.configure(text=passo.texto)
        if passo.dica:
            self._dica.configure(text=f"Dica: {passo.dica}")
            self._caixa_dica.pack(fill="x", padx=22, pady=(14, 0), before=self._rodape)
        else:
            self._caixa_dica.pack_forget()
        self._voltar.configure(state="normal" if self.indice > 0 else "disabled")
        self._proximo.configure(text="Começar a analisar" if ultimo else "Próximo",
                                width=160 if ultimo else 110)
        self._pular.configure(text="" if ultimo else "Pular guia", state="disabled" if ultimo else "normal")

        if passo.ao_entrar:
            passo.ao_entrar()
        self._posicionar(passo.posicao)
        self._iniciar_pulso(passo.alvos)

    def _posicionar(self, posicao: str) -> None:
        """A largura vai no `place` do Tk (o CTk a proíbe): os filhos empacotados fariam o frame
        crescer até o conteúdo."""
        self.place_forget()
        place = lambda **opcoes: tkinter.Frame.place(self, **opcoes)
        if posicao == SOBRE_PAINEL_LATERAL:
            painel = self.ancoras[SOBRE_PAINEL_LATERAL]
            painel.update_idletasks()
            largura = max(painel.winfo_width(), 300)
            self._ajustar_quebra(largura)
            place(in_=painel, x=0, y=0, anchor="nw", width=largura)
        elif posicao == SOBRE_GRAFICO:
            self._ajustar_quebra(LARGURA_CARTAO)
            place(in_=self.ancoras[SOBRE_GRAFICO], relx=0.5, rely=0.42, anchor="center",
                       width=LARGURA_CARTAO)
        else:
            self._ajustar_quebra(LARGURA_CARTAO)
            place(relx=0.5, rely=0.48, anchor="center", width=LARGURA_CARTAO)
        self.lift()

    def _ajustar_quebra(self, largura: int) -> None:
        for rotulo in (self._titulo, self._texto):
            rotulo.configure(wraplength=largura - 48)
        self._dica.configure(wraplength=largura - 80)

    # ---------- destaque pulsante ----------

    def _iniciar_pulso(self, alvos: tuple[str, ...]) -> None:
        self._alvos_ativos = [self.alvos[a] for a in alvos if a in self.alvos]
        self._pulso_aceso = True
        self._pulsar()

    def _pulsar(self) -> None:
        cor = tema.DESTAQUE if self._pulso_aceso else tema.DESTAQUE_PULSO
        for alvo in self._alvos_ativos:
            alvo.configure(border_color=cor)
        self._pulso_aceso = not self._pulso_aceso
        if self._alvos_ativos:
            self._pulso_id = self.after(INTERVALO_PULSO_MS, self._pulsar)

    def _parar_pulso(self) -> None:
        if self._pulso_id is not None:
            self.after_cancel(self._pulso_id)
            self._pulso_id = None
        for chave, alvo in self.alvos.items():
            alvo.configure(border_color=self._bordas_originais[chave])
        self._alvos_ativos = []
