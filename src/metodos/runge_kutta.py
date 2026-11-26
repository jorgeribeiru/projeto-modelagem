"""
Letra (b) — Método de Runge-Kutta de 4ª Ordem / RK4 (Seção 8.2, pág. 10 da apostila).

Assinatura esperada: recebe `ProblemaPVI` -> retorna `ResultadoMetodo`.

Recorrência em cada passo (n = 0, ..., N - 1):
    K1 = f(x_n, y_n)
    K2 = f(x_n + 0.5 * h, y_n + 0.5 * h * K1)
    K3 = f(x_n + 0.5 * h, y_n + 0.5 * h * K2)
    K4 = f(x_n + h, y_n + h * K3)
    y_{n+1} = y_n + (h / 6) * (K1 + 2*K2 + 2*K3 + K4)

Regras e validação:
- Chamar sempre `pvi.f(...)` (não fixar a equação da questão aqui).
- Não importar `euler`, `analise` nem `matplotlib`.
- Em x_1 = 0.1, a recorrência produz y_1 ~= 2.542304799.
- Ao reduzir `h` pela metade (0.05), o erro máximo deve cair ~16x (ordem h^4).
"""
from src.contratos import ProblemaPVI, ResultadoMetodo
from src.problema import gerar_malha


def resolver_runge_kutta(pvi: ProblemaPVI) -> ResultadoMetodo:
    """Resolve um PVI de 1ª ordem pelo Método de Runge-Kutta clássico."""
    h = pvi.h
    meio_passo = 0.5 * h
    pontos_x = gerar_malha(pvi.x0, pvi.x_fim, h)
    pontos_y = [pvi.y0]

    for x_n in pontos_x[:-1]:
        y_n = pontos_y[-1]
        k1 = pvi.f(x_n, y_n)
        k2 = pvi.f(x_n + meio_passo, y_n + meio_passo * k1)
        k3 = pvi.f(x_n + meio_passo, y_n + meio_passo * k2)
        k4 = pvi.f(x_n + h, y_n + h * k3)
        y_proximo = y_n + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        pontos_y.append(y_proximo)

    return ResultadoMetodo(
        nome="Runge-Kutta (RK4)",
        x=pontos_x,
        y=pontos_y,
    )
