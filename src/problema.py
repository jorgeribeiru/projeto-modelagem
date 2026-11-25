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
