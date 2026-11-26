"""
Letra (c) — Gráfico comparativo das 3 soluções em um único frame (`matplotlib`).

Responsabilidades:
- Paleta, tipografia e estilos das curvas (compartilhados com `src.interface`).
- Desenho das soluções (Exata, Euler, RK4) e do erro de cada método, com eixos rotulados.
- Geração da figura estática do relatório (`plotar_comparacao`), salva em PNG/PDF.

Regras:
- Recebe um `CenarioComparacao` pronto (montado pelo `main.py`): não importa solvers nem `analise`.
- Usa `matplotlib.figure.Figure` diretamente (sem `pyplot`), funcionando sem display.
"""
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

import matplotlib
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from src.contratos import CenarioComparacao

NOME_EXATA = "Solução Exata"
NOME_EULER = "Método de Euler"
NOME_RK4 = "Runge-Kutta (RK4)"

ESCALA_LINEAR = "linear"
ESCALA_LOG = "log"
ERRO_ABSOLUTO = "absoluto"
ERRO_RELATIVO = "relativo"
MODO_CLARO = "claro"
MODO_ESCURO = "escuro"

GID_SETA_EIXO = "seta-eixo"
PONTOS_CURVA_EXATA = 500

FONTES_PREFERIDAS = ("Inter", "Fira Sans", "Ubuntu", "Roboto", "Segoe UI", "Helvetica Neue")
FONTE_RESERVA = "DejaVu Sans"


@dataclass(frozen=True)
class Tema:
    fundo: str
    painel: str
    texto: str
    texto_suave: str
    grade: str
    eixo: str
    destaque: str
    curvas: dict[str, str]


TEMAS: dict[str, Tema] = {
    MODO_CLARO: Tema(
        fundo="#F6F7FB",
        painel="#FFFFFF",
        texto="#1B2230",
        texto_suave="#5E677A",
        grade="#E4E7EF",
        eixo="#9AA3B5",
        destaque="#7C3AED",
        curvas={NOME_EXATA: "#0F6FC6", NOME_EULER: "#E8590C", NOME_RK4: "#0E9F6E"},
    ),
    MODO_ESCURO: Tema(
        fundo="#0E131F",
        painel="#151C2C",
        texto="#E7EAF3",
        texto_suave="#8E97AD",
        grade="#232C40",
        eixo="#4A5571",
        destaque="#A78BFA",
        curvas={NOME_EXATA: "#5AB8FF", NOME_EULER: "#FF9F43", NOME_RK4: "#34D399"},
    ),
}

CORES_RESERVA = ("#D946EF", "#F43F5E", "#EAB308", "#14B8A6")

# Com h = 0.1 o RK4 fica sobreposto à Exata; marcadores vazados e um tracejado curto (mais curto que o do
# Euler, e menor que o vão entre círculos, senão o traço parece contínuo) mantêm as 3 curvas distinguíveis.
ESTILOS_CURVA: dict[str, dict] = {
    NOME_EXATA: {"linestyle": "-", "linewidth": 3.2, "alpha": 0.55, "zorder": 2, "solid_capstyle": "round"},
    NOME_EULER: {
        "linestyle": (0, (5, 3)),
        "linewidth": 1.7,
        "marker": "o",
        "markersize": 4.2,
        "zorder": 3,
    },
    NOME_RK4: {
        "linestyle": (0, (2.5, 2)),
        "linewidth": 2.0,
        "marker": "o",
        "markersize": 7.5,
        "markerfacecolor": "none",
        "markeredgewidth": 1.7,
        "zorder": 4,
    },
}
ESTILO_METODO_GENERICO = {"linestyle": ":", "linewidth": 1.6, "marker": "s", "markersize": 4, "zorder": 3}

ROTULO_X = "x  —  variável independente"
ROTULO_Y = "y(x)  —  solução do PVI"
ROTULOS_ERRO = {
    ERRO_ABSOLUTO: "|φ(xₙ) − yₙ|",
    ERRO_RELATIVO: "|φ(xₙ) − yₙ| / |φ(xₙ)|",
}
TITULOS_ERRO = {
    ERRO_ABSOLUTO: "ERRO ABSOLUTO",
    ERRO_RELATIVO: "ERRO RELATIVO",
}


@dataclass
class OpcoesGrafico:
    """Filtros e aparência aplicados ao desenho das curvas."""

    visiveis: set[str] = field(default_factory=lambda: {NOME_EXATA, NOME_EULER, NOME_RK4})
    intervalo_x: tuple[float, float] | None = None
    escala_y: str = ESCALA_LINEAR
    escala_erro: str = ESCALA_LOG
    tipo_erro: str = ERRO_ABSOLUTO
    modo: str = MODO_CLARO
    destacar_eixos: bool = False


@cache
def familia_fonte() -> str:
    """Primeira fonte preferida instalada no sistema (ou a reserva do matplotlib)."""
    instaladas = {fonte.name for fonte in font_manager.fontManager.ttflist}
    return next((nome for nome in FONTES_PREFERIDAS if nome in instaladas), FONTE_RESERVA)


def configurar_fontes() -> None:
    """A fonte de reserva cobre glifos ausentes na preferida (ex.: ′, ₙ, ⁻ˣ)."""
    matplotlib.rcParams["font.family"] = [familia_fonte(), FONTE_RESERVA]


def cor_da_curva(nome: str, modo: str = MODO_CLARO) -> str:
    tema = TEMAS[modo]
    if nome in tema.curvas:
        return tema.curvas[nome]
    return CORES_RESERVA[hash(nome) % len(CORES_RESERVA)]


def estilo_da_curva(nome: str) -> dict:
    return ESTILOS_CURVA.get(nome, ESTILO_METODO_GENERICO)


def nomes_das_curvas(cenario: CenarioComparacao) -> list[str]:
    """Ordem de exibição: Exata primeiro (se houver), depois os métodos."""
    nomes = [res.nome for res in cenario.resultados]
    if cenario.pvi.solucao_exata is not None:
        nomes.insert(0, NOME_EXATA)
    return nomes


def amostrar_exata(
    funcao: Callable[[float], float],
    x0: float,
    x_fim: float,
    n: int = PONTOS_CURVA_EXATA,
) -> tuple[list[float], list[float]]:
    """Avalia phi(x) numa malha densa para desenhar a curva analítica suave."""
    passo = (x_fim - x0) / (n - 1)
    xs = [x0 + i * passo for i in range(n)]
    xs[-1] = x_fim
    return xs, [funcao(x) for x in xs]


def intervalo_efetivo(cenario: CenarioComparacao, opcoes: OpcoesGrafico) -> tuple[float, float]:
    if opcoes.intervalo_x is None:
        return cenario.pvi.x0, cenario.pvi.x_fim
    x_min, x_max = opcoes.intervalo_x
    return max(x_min, cenario.pvi.x0), min(x_max, cenario.pvi.x_fim)


def _recortar(
    xs: Sequence[float], ys: Sequence[float], x_min: float, x_max: float
) -> tuple[list[float], list[float]]:
    tolerancia = 1e-9
    pares = [(x, y) for x, y in zip(xs, ys) if x_min - tolerancia <= x <= x_max + tolerancia]
    return [x for x, _ in pares], [y for _, y in pares]


def _marcar_a_cada(total_pontos: int) -> int:
    """Evita poluição visual de marcadores quando h é pequeno."""
    return max(1, round(total_pontos / 60))


def aplicar_tema(fig: Figure, eixos: Sequence[Axes], modo: str) -> None:
    tema = TEMAS[modo]
    fig.set_facecolor(tema.painel)
    for ax in eixos:
        ax.set_facecolor(tema.painel)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        for lado in ("left", "bottom"):
            ax.spines[lado].set_color(tema.eixo)
            ax.spines[lado].set_linewidth(1.1)
        ax.tick_params(colors=tema.texto_suave, labelsize=9, length=4, width=0.9)
        ax.grid(True, which="major", color=tema.grade, linewidth=0.8)
        ax.grid(True, which="minor", color=tema.grade, linewidth=0.4, alpha=0.6)
        ax.set_axisbelow(True)


def _desenhar_setas_dos_eixos(ax: Axes, cor: str) -> None:
    """Pontas de seta no fim de cada eixo, reforçando a orientação de x e y."""
    ax.plot(1, 0, marker=">", color=cor, markersize=7, transform=ax.transAxes,
            clip_on=False, gid=GID_SETA_EIXO)
    ax.plot(0, 1, marker="^", color=cor, markersize=7, transform=ax.transAxes,
            clip_on=False, gid=GID_SETA_EIXO)


def _titulo_do_painel(ax: Axes, titulo: str, detalhe: str, tema: Tema) -> None:
    rotulo = ax.text(0.0, 1.04, titulo, transform=ax.transAxes, fontsize=9.5, fontweight="bold",
                     color=tema.destaque, va="bottom")
    ax.annotate(detalhe, xy=(1, 0), xycoords=rotulo, xytext=(10, 0), textcoords="offset points",
                fontsize=9.5, color=tema.texto_suave, va="bottom")


def _rotular(ax: Axes, rotulo_x: str | None, rotulo_y: str, tema: Tema, destacar: bool) -> None:
    cor = tema.destaque if destacar else tema.texto
    peso = "bold" if destacar else "normal"
    if rotulo_x is not None:
        ax.set_xlabel(rotulo_x, loc="right", color=cor, fontsize=10.5, fontweight=peso,
                      labelpad=6)
    ax.set_ylabel(rotulo_y, loc="top", color=cor, fontsize=10.5, fontweight=peso,
                  labelpad=8)
    cor_seta = tema.destaque if destacar else tema.eixo
    if destacar:
        for lado in ("left", "bottom"):
            ax.spines[lado].set_color(tema.destaque)
            ax.spines[lado].set_linewidth(2.2)
    _desenhar_setas_dos_eixos(ax, cor_seta)


def desenhar_solucoes(
    ax: Axes, cenario: CenarioComparacao, opcoes: OpcoesGrafico
) -> dict[str, Line2D]:
    """Plota no mesmo eixo a solução exata (curva densa) e cada método visível."""
    x_min, x_max = intervalo_efetivo(cenario, opcoes)
    linhas: dict[str, Line2D] = {}

    exata = cenario.pvi.solucao_exata
    if exata is not None and NOME_EXATA in opcoes.visiveis:
        xs, ys = amostrar_exata(exata, x_min, x_max)
        (linhas[NOME_EXATA],) = ax.plot(
            xs, ys, label=NOME_EXATA, color=cor_da_curva(NOME_EXATA, opcoes.modo),
            **estilo_da_curva(NOME_EXATA),
        )

    for resultado in cenario.resultados:
        if resultado.nome not in opcoes.visiveis:
            continue
        xs, ys = _recortar(resultado.x, resultado.y, x_min, x_max)
        (linhas[resultado.nome],) = ax.plot(
            xs, ys, label=resultado.nome, color=cor_da_curva(resultado.nome, opcoes.modo),
            markevery=_marcar_a_cada(len(xs)), **estilo_da_curva(resultado.nome),
        )

    ax.set_yscale(opcoes.escala_y)
    ax.set_xlim(x_min, x_max)
    return linhas


def desenhar_erros(
    ax: Axes, cenario: CenarioComparacao, opcoes: OpcoesGrafico
) -> dict[str, Line2D]:
    """Plota o erro (absoluto ou relativo) de cada método visível ao longo da malha."""
    x_min, x_max = intervalo_efetivo(cenario, opcoes)
    erros = cenario.erros_relativos if opcoes.tipo_erro == ERRO_RELATIVO else cenario.erros_absolutos
    linhas: dict[str, Line2D] = {}

    for resultado in cenario.resultados:
        if resultado.nome not in opcoes.visiveis or resultado.nome not in erros:
            continue
        xs, es = _recortar(resultado.x, erros[resultado.nome], x_min, x_max)
        if opcoes.escala_erro == ESCALA_LOG:
            # Em x0 o erro é exatamente 0 e não existe em escala log.
            pares = [(x, e) for x, e in zip(xs, es) if e > 0]
            xs, es = [x for x, _ in pares], [e for _, e in pares]
        estilo = dict(estilo_da_curva(resultado.nome))
        estilo.update(linestyle="-", linewidth=1.6, markersize=4.2)
        (linhas[resultado.nome],) = ax.plot(
            xs, es, label=resultado.nome, color=cor_da_curva(resultado.nome, opcoes.modo),
            markevery=_marcar_a_cada(len(xs)), **estilo,
        )

    ax.set_yscale(opcoes.escala_erro)
    ax.set_xlim(x_min, x_max)
    return linhas


def _estilizar_legenda(ax: Axes, tema: Tema, **kwargs) -> None:
    if not ax.get_legend_handles_labels()[0]:
        return
    legenda = ax.legend(frameon=True, fancybox=True, framealpha=0.92, borderpad=0.8,
                        handlelength=3.2, prop={"size": 9.5}, **kwargs)
    legenda.get_frame().set_facecolor(tema.painel)
    legenda.get_frame().set_edgecolor(tema.grade)
    for texto in legenda.get_texts():
        texto.set_color(tema.texto)


def montar_figura_comparacao(
    cenario: CenarioComparacao,
    opcoes: OpcoesGrafico,
    fig: Figure | None = None,
) -> tuple[Figure, Axes, Axes]:
    """Desenha (ou redesenha em `fig`) o painel de soluções e o painel de erro, alinhados em x."""
    configurar_fontes()
    if fig is None:
        fig = Figure(figsize=(10, 7.2), layout="constrained")
    else:
        fig.clear()
    fig.get_layout_engine().set(h_pad=0.12, w_pad=0.1)

    ax_solucoes, ax_erro = fig.subplots(2, 1, sharex=True, height_ratios=[3, 1.7])
    tema = TEMAS[opcoes.modo]
    aplicar_tema(fig, (ax_solucoes, ax_erro), opcoes.modo)

    desenhar_solucoes(ax_solucoes, cenario, opcoes)
    desenhar_erros(ax_erro, cenario, opcoes)

    ax_solucoes.tick_params(labelbottom=True)
    _rotular(ax_solucoes, None, ROTULO_Y, tema, opcoes.destacar_eixos)
    _rotular(ax_erro, ROTULO_X, ROTULOS_ERRO[opcoes.tipo_erro], tema, opcoes.destacar_eixos)
    _titulo_do_painel(ax_solucoes, "SOLUÇÕES", f"h = {cenario.pvi.h:g}  ·  {len(cenario.resultados[0].x)} pontos"
                      if cenario.resultados else "", tema)
    _titulo_do_painel(ax_erro, TITULOS_ERRO[opcoes.tipo_erro],
                      f"escala {'logarítmica' if opcoes.escala_erro == ESCALA_LOG else 'linear'}", tema)
    _estilizar_legenda(ax_solucoes, tema, loc="upper right")
    return fig, ax_solucoes, ax_erro


def plotar_comparacao(
    cenario: CenarioComparacao,
    caminho_saida: str | Path,
    opcoes: OpcoesGrafico | None = None,
    formatos: Sequence[str] = ("png", "pdf"),
    titulo: str | None = None,
) -> list[Path]:
    """Gera a figura do relatório (letra c) e salva em cada formato pedido. Retorna os caminhos."""
    opcoes = opcoes or OpcoesGrafico()
    fig, _, _ = montar_figura_comparacao(cenario, opcoes)
    tema = TEMAS[opcoes.modo]

    titulo = titulo or "Comparação entre a solução exata e os métodos numéricos"
    fig.suptitle(titulo, color=tema.texto, fontsize=13, fontweight="bold",
                 x=0.02, ha="left")
    if cenario.equacao:
        fig.text(0.98, 0.985, f"{cenario.equacao}     {cenario.solucao_exata_texto}",
                 ha="right", va="top", color=tema.texto_suave, fontsize=9.5)

    base = Path(caminho_saida).with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)
    salvos = []
    for formato in formatos:
        destino = base.with_suffix(f".{formato}")
        fig.savefig(destino, dpi=300, facecolor=fig.get_facecolor())
        salvos.append(destino)
    return salvos
