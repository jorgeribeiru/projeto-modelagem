"""
Testes unitários e de sanidade para o Método de Runge-Kutta (`src.metodos.runge_kutta`).

Cenários recomendados para implementar aqui (Frente 2 — Letra B)
----------------------------------------------------------------
1. Condição inicial preservada:
   Garantir que `resultado.x[0] == pvi.x0` e `resultado.y[0] == pvi.y0`.
2. Quantidade exata de pontos na malha:
   Para [0, 5] com h = 0.1, verificar se `len(resultado.x) == 51` e
   `len(resultado.y) == 51`, terminando em `x[-1] == 5.0`.
3. Precisão elevada já no primeiro passo e no intervalo completo:
   Comparar `resultado.y` com `phi(x) = exp(-x) + 2*exp(-2x)` nos 51 pontos; para
   h = 0.1, o erro absoluto máximo em todo o intervalo deve ser da ordem de 10^-5
   ou menor (muito inferior ao erro do Método de Euler).
4. Ordem de convergência O(h^4) do erro global:
   Ao resolver o mesmo PVI reduzindo o passo pela metade (`h = 0.05`), o erro máximo
   global deve cair aproximadamente 16 vezes (2^4), confirmando que os quatro
   coeficientes K_n1, K_n2, K_n3 e K_n4 e seus pesos estão corretos.
"""
