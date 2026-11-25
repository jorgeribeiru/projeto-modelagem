"""
Módulo principal de orquestração do projeto (Ponto de Entrada).

Responsabilidade
----------------
Este arquivo funciona apenas como o "maestro" da aplicação: ele conecta os módulos
independentes na ordem correta para executar o Trabalho 1 de ponta a ponta.

Fluxo esperado quando implementado
----------------------------------
1. Obter a instância do Problema de Valor Inicial (PVI) definida em `src.problema`.
2. Executar o Método de Euler (`src.metodos.euler`) passando o PVI — Letra (a).
3. Executar o Método de Runge-Kutta (`src.metodos.runge_kutta`) passando o PVI — Letra (b).
4. Acionar `src.analise` para comparar as aproximações numéricas com a solução exata
   e exibir/salvar a tabela de erros que servirá de base para o relatório.
5. Acionar `src.visualizacao` para plotar no mesmo gráfico (frame) as três curvas
   (Exata, Euler e Runge-Kutta) e salvar a figura final em `resultados/` — Letra (c).

O que NÃO fazer neste arquivo
-----------------------------
- Não escrever fórmulas matemáticas do PVI nem laços de métodos numéricos aqui.
- Não configurar detalhes visuais do Matplotlib (cores, fontes, eixos) diretamente aqui.
- Manter este arquivo enxuto (idealmente entre 15 e 30 linhas de código limpo).
"""
