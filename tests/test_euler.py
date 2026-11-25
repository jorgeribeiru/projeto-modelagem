"""
Testes unitários e de sanidade para o Método de Euler (`src.metodos.euler`).

Cenários recomendados para implementar aqui (Frente 1 — Letra A)
----------------------------------------------------------------
1. Condição inicial preservada:
   Garantir que `resultado.x[0] == pvi.x0` e `resultado.y[0] == pvi.y0`.
2. Quantidade exata de pontos na malha:
   Para [0, 5] com h = 0.1, verificar se `len(resultado.x) == 51` e
   `len(resultado.y) == 51`, terminando em `x[-1] == 5.0`.
3. Conferência manual do primeiro passo:
   Para y' = exp(-x) - 2y com y(0) = 3 e h = 0.1, temos f(0, 3) = 1 - 6 = -5,
   logo `resultado.y[1]` deve ser igual a 2.5 (dentro da tolerância de ponto flutuante).
4. Ordem de convergência O(h) do erro global:
   Ao resolver o mesmo PVI com passo `h / 2` (0.05), o erro máximo em relação à
   solução exata deve cair aproximadamente pela metade (~2x menor).
"""
