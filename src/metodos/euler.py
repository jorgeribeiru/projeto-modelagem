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
