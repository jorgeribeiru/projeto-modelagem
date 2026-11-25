"""
Análise quantitativa de erros e geração de tabelas para o relatório.

Responsabilidade (Frente 4 — Apoio ao Relatório)
------------------------------------------------
O enunciado pede "descrições básicas e comentários sobre o que realizou", e a
Seção 6 da apostila do Prof. Sansuke discute em detalhes os erros numéricos
(erro de fórmula local vs. acumulado e erro de arredondamento).

Este módulo existe para calcular indicadores objetivos comparando cada método
numérico com a solução analítica exata phi(x), gerando tabelas e métricas prontas
para embasar os comentários do relatório em PDF.

O que pode ser implementado neste arquivo
-----------------------------------------
1. Cálculo do erro absoluto ponto a ponto para um `ResultadoMetodo`:
       erro_n = |phi(x_n) - y_n|
   para cada ponto x_n da malha.
2. Resumo estatístico de cada método no intervalo [0, 5]:
   - Erro absoluto máximo (e em qual valor de `x` ele ocorre — dica: observe onde
     a curvatura da solução exata é mais acentuada!).
   - Erro absoluto médio ao longo dos 51 pontos.
   - Erro absoluto no ponto final x = 5.0.
3. Exibição formatada no terminal e/ou exportação (ex.: CSV ou tabela Markdown em
   `resultados/`) comparando lado a lado:
       x_n | Exata phi(x_n) | Euler y_n | Erro Euler | RK4 y_n | Erro RK4
   em pontos representativos (como x = 0.0, 0.5, 1.0, ..., 5.0 ou todos os 51 pontos).

Observação para o grupo
-----------------------
Este módulo é desacoplado: ele recebe apenas a função `solucao_exata` e uma lista de
`ResultadoMetodo`, sem depender de `matplotlib` nem dos arquivos internos de `metodos/`.
"""
