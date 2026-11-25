"""
Ponto de entrada do projeto (Orquestrador).

Papel: conectar os módulos na ordem de execução, sem fazer contas nem configurar gráficos aqui.

Fluxo esperado:
1. Instanciar o PVI definido em `src.problema`.
2. Resolver pelo Método de Euler (`src.metodos.euler`) — Letra (a).
3. Resolver pelo Método de Runge-Kutta (`src.metodos.runge_kutta`) — Letra (b).
4. Gerar métricas e tabela comparativa de erros em `src.analise`.
5. Plotar e salvar o gráfico comparativo das 3 curvas em `src.visualizacao` — Letra (c).
"""
