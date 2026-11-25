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
- Em x_1 = 0.1, deve resultar próximo de phi(0.1) ~= 2.542300.
- Ao reduzir `h` pela metade (0.05), o erro máximo deve cair ~16x (ordem h^4).
"""
