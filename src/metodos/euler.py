"""
Implementação do Método de Euler para PVIs de 1ª ordem — Letra (a).

Responsabilidade (Frente 1 — Letra A)
-------------------------------------
Resolver numericamente um `ProblemaPVI` qualquer utilizando o Método de Euler
(também chamado de Método da Reta Tangente), conforme fundamentado na Seção 5
(páginas 4 e 5) da apostila do Prof. Sansuke Watanabe.

Formulação matemática (Recorrência)
-----------------------------------
Partindo do ponto inicial exato (x_0, y_0), cada aproximação seguinte é obtida por
aproximação linear local com passo uniforme h:

    y_{n+1} = y_n + f(x_n, y_n) * h

para n = 0, 1, ..., N - 1, onde x_n = x_0 + n * h.

O que implementar neste arquivo
-------------------------------
- Uma função principal (ex.: `resolver_euler(pvi: ProblemaPVI) -> ResultadoMetodo`).
- Gerar (ou reutilizar a função de malha de `src.problema`) a lista de pontos `x`
  de `x0` até `x_fim` com passo `h`.
- Iniciar a lista `y` com a condição inicial `pvi.y0` e iterar aplicando a fórmula
  de recorrência acima a cada passo.
- Devolver um `ResultadoMetodo` com `nome="Método de Euler"`, `x` e `y`.

Regras de desacoplamento (O que NÃO fazer aqui)
-----------------------------------------------
- Não escrever `exp(-x) - 2*y` neste arquivo; use exclusivamente `pvi.f(x_n, y_n)`.
- Não importar `matplotlib`, `runge_kutta` nem `analise`.

Como testar isoladamente
------------------------
- Para o PVI do trabalho em x_0 = 0, y_0 = 3 e h = 0.1:
  No 1º passo, f(0, 3) = -5, logo y_1 deve dar exatamente 3 + (-5) * 0.1 = 2.5.
- A lista `x` e a lista `y` retornadas devem ter exatamente o mesmo tamanho (51 pontos).
"""
