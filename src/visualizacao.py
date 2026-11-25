"""
Geração do gráfico comparativo das soluções — Letra (c).

Responsabilidade (Frente 3 — Letra C)
-------------------------------------
Plotar em um único gráfico (mesmo frame / eixo do Matplotlib) as três soluções do PVI:
1. Solução Exata (analítica)
2. Solução numérica pelo Método de Euler
3. Solução numérica pelo Método de Runge-Kutta (RK4)

Como desenvolver antes dos métodos A e B ficarem prontos
--------------------------------------------------------
Você não precisa esperar `euler.py` nem `runge_kutta.py` terminarem! Durante o
desenvolvimento, crie no seu teste local dois objetos `ResultadoMetodo` simulados
(com listas `x` e `y` fictícias quaisquer) e uma função exata de exemplo para
deixar todo o design visual, legendas e salvamento de arquivo prontos.

O que implementar neste arquivo
-------------------------------
- Uma função principal de plotagem (ex.: `plotar_comparacao(...)`) que receba:
  * O `ProblemaPVI` (ou a função `solucao_exata` e limites do intervalo) para
    desenhar a curva analítica exata (dica: avaliá-la em ~300 a 500 pontos deixa
    a curva contínua bem suave, contrastando com os 51 pontos discretos h = 0.1).
  * Uma coleção de `ResultadoMetodo` contendo os resultados de Euler e Runge-Kutta.
  * O caminho onde salvar a imagem (ex.: `resultados/comparacao_pvi.png` ou `.pdf`)
    e/ou uma flag opcional para exibir na tela.
- Configurar elementos essenciais de um gráfico acadêmico de relatório:
  * Título descritivo (identificando o PVI e o passo h = 0.1).
  * Rótulos nos eixos (`x` e `y(x)`).
  * Grade leve (`grid`) para facilitar leitura comparativa.
  * Legenda clara identificando as três curvas.
  * Resolução adequada para impressão/PDF (ex.: `dpi=300` e `bbox_inches="tight"`).

Cuidado visual importante
-------------------------
Com h = 0.1, o erro do Runge-Kutta é da ordem de 10^-6, fazendo sua curva ficar
praticamente em cima da Solução Exata. Escolha combinações distintas de linha,
espessura e marcadores (ex.: linha sólida contínua para a Exata, tracejada com
marcadores para Euler e marcadores espaçados/vazados para o RK4) para que as
TRÊS curvas apareçam nitidamente no mesmo frame.

O que NÃO fazer neste arquivo
-----------------------------
- Não implementar cálculos de Euler ou Runge-Kutta aqui dentro; apenas consuma os
  dados já prontos nos objetos `ResultadoMetodo`.
"""
