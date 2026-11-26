"""
Estado dos filtros e regras de inspeção de pontos, sem dependência de Tk.

Mantido separado da janela para ser testável sem display.
"""
import bisect
import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from src.contratos import CenarioComparacao
from src.visualizacao import (
    ERRO_ABSOLUTO,
    ESCALA_LINEAR,
    ESCALA_LOG,
    MODO_CLARO,
    OpcoesGrafico,
    nomes_das_curvas,
)

PASSOS_DISPONIVEIS = (0.2, 0.1, 0.05, 0.025)
SOBRESCRITOS = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


@dataclass
class EstadoFiltros:
    visiveis: set[str]
    x_min: float
    x_max: float
    escala_y: str = ESCALA_LINEAR
    escala_erro: str = ESCALA_LOG
    tipo_erro: str = ERRO_ABSOLUTO
    h: float = 0.1
    indice_inspecionado: int | None = None
    modo: str = MODO_CLARO
    destacar_eixos: bool = field(default=False, compare=False)

    @classmethod
    def padrao(cls, cenario: CenarioComparacao, modo: str = MODO_CLARO) -> "EstadoFiltros":
        return cls(
            visiveis=set(nomes_das_curvas(cenario)),
            x_min=cenario.pvi.x0,
            x_max=cenario.pvi.x_fim,
            h=cenario.pvi.h,
            modo=modo,
        )

    def opcoes_grafico(self) -> OpcoesGrafico:
        return OpcoesGrafico(
            visiveis=set(self.visiveis),
            intervalo_x=(self.x_min, self.x_max),
            escala_y=self.escala_y,
            escala_erro=self.escala_erro,
            tipo_erro=self.tipo_erro,
            modo=self.modo,
            destacar_eixos=self.destacar_eixos,
        )

    def definir_intervalo(self, x_min: float, x_max: float, limites: tuple[float, float]) -> None:
        """Aplica o intervalo dentro dos limites do domínio, garantindo largura mínima de um passo."""
        inicio, fim = limites
        x_min = min(max(x_min, inicio), fim)
        x_max = min(max(x_max, inicio), fim)
        if x_max - x_min < self.h:
            if x_min + self.h <= fim:
                x_max = x_min + self.h
            else:
                x_min = x_max - self.h
        self.x_min, self.x_max = round(x_min, 10), round(x_max, 10)


@dataclass(frozen=True)
class LinhaMetodo:
    nome: str
    y: float
    erro_absoluto: float
    erro_relativo: float


@dataclass(frozen=True)
class ResumoPonto:
    indice: int
    x: float
    exato: float
    metodos: list[LinhaMetodo]
    pior: str | None
    melhor: str | None
    razao: float | None


def no_mais_proximo(malha: Sequence[float], x: float) -> int:
    """Índice do nó da malha mais próximo de `x` (malha ordenada)."""
    posicao = bisect.bisect_left(malha, x)
    if posicao == 0:
        return 0
    if posicao == len(malha):
        return len(malha) - 1
    anterior, seguinte = malha[posicao - 1], malha[posicao]
    return posicao if seguinte - x < x - anterior else posicao - 1


def faixa_de_indices(malha: Sequence[float], x_min: float, x_max: float) -> tuple[int, int]:
    """Primeiro e último índices da malha dentro de [x_min, x_max]."""
    tolerancia = 1e-9
    inicio = bisect.bisect_left(malha, x_min - tolerancia)
    fim = bisect.bisect_right(malha, x_max + tolerancia) - 1
    return inicio, max(inicio, fim)


def mover_indice(indice: int, delta: int, inicio: int, fim: int) -> int:
    return min(max(indice + delta, inicio), fim)


def resumo_ponto(cenario: CenarioComparacao, indice: int) -> ResumoPonto:
    """Valores e erros de cada método no nó `indice`, com a razão entre o pior e o melhor erro."""
    x = cenario.resultados[0].x[indice]
    exata = cenario.pvi.solucao_exata
    exato = exata(x) if exata is not None else math.nan

    metodos = [
        LinhaMetodo(
            nome=res.nome,
            y=res.y[indice],
            erro_absoluto=cenario.erros_absolutos.get(res.nome, [math.nan] * len(res.x))[indice],
            erro_relativo=cenario.erros_relativos.get(res.nome, [math.nan] * len(res.x))[indice],
        )
        for res in cenario.resultados
    ]

    comparaveis = [m for m in metodos if m.erro_absoluto > 0]
    pior = melhor = None
    razao = None
    if len(comparaveis) >= 2:
        ordenados = sorted(comparaveis, key=lambda m: m.erro_absoluto)
        melhor, pior = ordenados[0].nome, ordenados[-1].nome
        razao = ordenados[-1].erro_absoluto / ordenados[0].erro_absoluto

    return ResumoPonto(indice=indice, x=x, exato=exato, metodos=metodos,
                       pior=pior, melhor=melhor, razao=razao)


def formatar_numero(valor: float) -> str:
    """Notação legível: decimal para magnitudes usuais, científica para muito pequenas."""
    if math.isnan(valor):
        return "—"
    if valor == 0:
        return "0"
    if 1e-3 <= abs(valor) < 1e4:
        return f"{valor:.6f}"
    mantissa, expoente = f"{valor:.3e}".split("e")
    return f"{mantissa} × 10{str(int(expoente)).translate(SOBRESCRITOS)}"


def formatar_percentual(fracao: float) -> str:
    if math.isnan(fracao):
        return "—"
    percentual = fracao * 100
    if percentual == 0 or 1e-3 <= abs(percentual) < 1e4:
        return f"{percentual:.4g} %"
    return f"{formatar_numero(percentual)} %"


def formatar_razao(razao: float) -> str:
    """Separador de milhar com espaço fino: "6.871" seria lido como decimal."""
    if razao >= 10:
        return f"{razao:,.0f}".replace(",", "\u202f")
    return f"{razao:.1f}"
