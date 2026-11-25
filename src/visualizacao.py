"""
Letra (c) — Gráfico comparativo das 3 soluções em um único frame (`matplotlib`).

O que implementar aqui:
- Função que receba a solução exata (ou `ProblemaPVI`), os resultados de Euler e RK4
  (`ResultadoMetodo`) e o caminho de saída em `resultados/`.
- Plotar no mesmo eixo: Solução Exata, Método de Euler e Runge-Kutta (RK4).
- Configurar título, rótulos (`x` e `y(x)`), grade leve, legenda e salvar com boa
  resolução (ex.: `dpi=300`).

Dicas importantes:
- Pode ser desenvolvido antes de A e B usando objetos `ResultadoMetodo` simulados (mock).
- Como o RK4 fica quase sobreposto à curva Exata, use estilos/marcadores distintos para
  que as três curvas fiquem visíveis.
"""
