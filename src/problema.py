"""
Definição matemática do PVI do Trabalho 1 e geração da malha discreta.

Responsabilidade (Frente 1 — Estrutura Base)
--------------------------------------------
Concentrar em um único lugar todas as informações específicas da Questão 1 do
enunciado, isolando a equação diferencial dos algoritmos numéricos.

Dados matemáticos do enunciado que devem ser modelados aqui
-----------------------------------------------------------
- EDO original: y' + 2y = exp(-x)
- Forma explícita de Cauchy para `f(x, y)`: f(x, y) = exp(-x) - 2y
- Condição inicial: x0 = 0.0 e y0 = 3.0
- Intervalo de integração: 0.0 <= x <= 5.0 (logo, x_fim = 5.0)
- Passo: h = 0.1
- Solução analítica exata: phi(x) = exp(-x) + 2 * exp(-2x)

Funções sugeridas para implementar neste módulo
-----------------------------------------------
1. Função da derivada `f(x, y)` usando `math.exp`.
2. Função da solução exata `solucao_exata(x)` usando `math.exp`.
3. Função utilitária `gerar_malha(x0, x_fim, h) -> list[float]`:
   Deve calcular a quantidade inteira de passos `n_passos = round((x_fim - x0) / h)`
   e gerar os `n_passos + 1` pontos por índice (`round(x0 + i * h, 10)`), evitando o
   erro clássico de arredondamento binário de laços `while x <= x_fim` com `x += h`.
   Para [0, 5] e h = 0.1, deve produzir exatamente 51 pontos (de 0.0 até 5.0).
4. Função fábrica (ex.: `criar_pvi_trabalho() -> ProblemaPVI`) que devolve o objeto
   `ProblemaPVI` pronto para ser consumido pelo `main.py`.

Validação rápida isolada
------------------------
- Verificar se f(0.0, 3.0) retorna exatamente -5.0.
- Verificar se solucao_exata(0.0) retorna exatamente 3.0.
- Verificar se a malha possui tamanho 51, iniciando em 0.0 e terminando em 5.0.
"""
