"""
Modelagem matemática específica da Questão 1 e geração da malha.

Dados do enunciado:
- EDO na forma de Cauchy: f(x, y) = exp(-x) - 2y
- Condição inicial e domínio: y(0) = 3, x em [0, 5], passo h = 0.1 (51 pontos)
- Solução analítica exata: phi(x) = exp(-x) + 2 * exp(-2x)

O que implementar aqui:
- Função da derivada `f(x, y)` e função `solucao_exata(x)` (usando `math.exp`).
- Função `gerar_malha(x0, x_fim, h) -> list[float]` calculando `n = round((x_fim - x0) / h)`
  e gerando pontos por índice (`round(x0 + i * h, 10)`), evitando `while x <= 5.0`.
- Função que monta e retorna o `ProblemaPVI` pronto da questão.
"""
import math

from src.contratos import ProblemaPVI


def f(x: float, y:float) -> float:
    """Derivada explícita do PVI: y' = exp(-x) - 2y"""
    return math.exp(-x) - 2.0 * y


def solucao_exata(x: float) -> float:
    """Solução analítica exata: phi(x) = exp(-x) + 2*exp(-2x)"""
    return math.exp(-x) + 2.0 * math.exp(-2.0 * x)


def gerar_malha(x0: float, x_fim: float, h: float) -> list[float]:
    """Gera os pontos discretos x_0, ..., x_n sem acúmulo de erro flutuante"""
    n_passos = round((x_fim - x0) / h)
    return [round(x0 + i * h, 10) for i in range(n_passos + 1)]


def criar_pvi_trabalho() -> ProblemaPVI:
    """Retorna a instância configurada do PVI da Questão 1"""
    return ProblemaPVI(
        f=f,
        x0=0.0,
        y0=3.0,
        x_fim=5.0,
        h=0.1,
        solucao_exata=solucao_exata
    )