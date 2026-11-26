"""
Letra (a) — Método de Euler (Seção 5 da apostila).

Assinatura esperada: recebe `ProblemaPVI` -> retorna `ResultadoMetodo`.

Recorrência em cada passo (n = 0, ..., N - 1):
    y_{n+1} = y_n + h * f(x_n, y_n)

Regras e validação:
- Chamar sempre `pvi.f(x_n, y_n)` (não fixar `exp(-x) - 2y` neste arquivo).
- Não importar `runge_kutta`, `analise` nem `matplotlib`.
- Para o PVI do trabalho (y(0) = 3, h = 0.1), o 1º passo deve resultar em y_1 = 2.5,
  retornando listas `x` e `y` com 51 pontos.
"""
from src.contratos import ProblemaPVI, ResultadoMetodo
from src.problema import gerar_malha


def resolver_euler(pvi: ProblemaPVI) -> ResultadoMetodo:
    """Resolve um PVI de 1ª ordem pelo Método de Euler"""
    pontos_x = gerar_malha(pvi.x0, pvi.x_fim, pvi.h)
    pontos_y = [pvi.y0]

    for x_n in pontos_x[:-1]:
        y_n = pontos_y[-1]
        y_proximo = y_n + pvi.h * pvi.f(x_n, y_n)
        pontos_y.append(y_proximo)

    return ResultadoMetodo(
        nome="Método de Euler",
        x=pontos_x,
        y=pontos_y,
    )