"""
Cálculo de erros e tabelas comparativas para embasar o relatório (Seção 6 da apostila).

O que implementar aqui:
- Receber a função `solucao_exata` e uma lista de `ResultadoMetodo`.
- Calcular o erro absoluto em cada ponto: erro_n = |phi(x_n) - y_n|.
- Extrair erro máximo, erro médio e erro final (em x = 5.0) de cada método.
- Exibir no terminal ou exportar tabela comparativa (x, Exata, Euler, RK4 e erros)
  para facilitar os comentários do relatório em PDF.
"""
