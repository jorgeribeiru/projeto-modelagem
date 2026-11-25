"""
Implementação do Método de Runge-Kutta de 4ª Ordem (RK4) — Letra (b).

Responsabilidade (Frente 2 — Letra B)
-------------------------------------
Resolver numericamente um `ProblemaPVI` qualquer utilizando as fórmulas clássicas
do Método de Runge-Kutta de 4ª ordem (equivalente em precisão à série de Taylor de
cinco termos, com erro local proporcional a h^5), conforme a Seção 8.2 (página 10)
da apostila do Prof. Sansuke Watanabe.

Formulação matemática (Recorrência)
-----------------------------------
Partindo da condição inicial (x_0, y_0), para cada passo n = 0, 1, ..., N - 1,
calculam-se quatro inclinações intermediárias no intervalo [x_n, x_{n+1}]:

    K_n1 = f(x_n, y_n)
    K_n2 = f(x_n + 0.5 * h, y_n + 0.5 * h * K_n1)
    K_n3 = f(x_n + 0.5 * h, y_n + 0.5 * h * K_n2)
    K_n4 = f(x_n + h, y_n + h * K_n3)

E atualiza-se a aproximação pela média ponderada dessas inclinações:

    y_{n+1} = y_n + (h / 6) * (K_n1 + 2 * K_n2 + 2 * K_n3 + K_n4)

O que implementar neste arquivo
-------------------------------
- Uma função principal (ex.: `resolver_runge_kutta(pvi: ProblemaPVI) -> ResultadoMetodo`).
- Construir os pontos da malha `x` de `x0` até `x_fim` com passo `h` (sem erro de
  acumulação de ponto flutuante no limite final).
- Calcular iterativamente os valores `y` usando `K_n1`, `K_n2`, `K_n3` e `K_n4`.
- Devolver um `ResultadoMetodo` com `nome="Runge-Kutta (RK4)"`, `x` e `y`.

Regras de desacoplamento (O que NÃO fazer aqui)
-----------------------------------------------
- Não fixar a equação `exp(-x) - 2*y` aqui; chame sempre `pvi.f(...)`.
- Não importar `euler`, `visualizacao` nem `analise`.

Como testar isoladamente
------------------------
- Para o PVI do trabalho (x_0 = 0, y_0 = 3, h = 0.1), o valor em x_1 = 0.1 deve ficar
  muito próximo da solução exata phi(0.1) = exp(-0.1) + 2*exp(-0.2) ~= 2.542300.
- Teste de ordem de convergência: ao reduzir `h` pela metade (de 0.1 para 0.05),
  o erro máximo em relação à solução exata deve cair aproximadamente 16 vezes (2^4).
"""
