# Pasta do Relatório (`relatorio/`)

Espaço dedicado à **Frente 4 (Relatório)** para armazenar os arquivos editáveis (LaTeX, Typst, Markdown ou documento de texto) e o **PDF final** exigido na entrega.

## Checklist do que o relatório precisa conter (conforme o enunciado)
1. **Identificação:** Nome completo de todos os integrantes do grupo, disciplina e professor.
2. **Descrição básica do problema:** Apresentação do PVI ($y' + 2y = e^{-x}$, $y(0) = 3$), intervalo $[0, 5]$, passo $h = 0.1$ e solução analítica exata $\varphi(x) = e^{-x} + 2e^{-2x}$.
3. **Resumo dos métodos implementados:** Breve explicação das recorrências do Método de Euler (aproximação linear) e do Método de Runge-Kutta de 4ª ordem (média ponderada de 4 inclinações sem cálculo de derivadas superiores).
4. **Gráfico comparativo (Letra c):** Inclusão da figura gerada em `resultados/` mostrando as três soluções (Exata, Euler e Runge-Kutta) em um mesmo *frame*.
5. **Comentários e análise dos resultados:** Discussão sobre a diferença de precisão observada entre Euler e Runge-Kutta frente à curva exata (relacionando com o erro de fórmula local/acumulado da Seção 6 da apostila).
