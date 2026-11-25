"""
Contratos de dados compartilhados entre todos os módulos do projeto.

Responsabilidade
----------------
Definir os tipos de entrada e saída que conectam o problema matemático, os métodos
numéricos (Euler e Runge-Kutta), a análise de erros e a visualização gráfica.
Com este contrato fixo, os 4 integrantes podem desenvolver seus arquivos em paralelo
sem depender da implementação interna um do outro.

Estruturas que devem ser declaradas aqui (usando `dataclasses` e `typing`)
--------------------------------------------------------------------------
1. `ProblemaPVI`:
   Representa um Problema de Valor Inicial de 1ª ordem na forma explícita de Cauchy
   y' = f(x, y), sujeito a y(x0) = y0 no intervalo [x0, x_fim].
   Campos esperados:
   - `f`: função `Callable[[float, float], float]` que calcula a derivada f(x, y).
   - `x0`: `float` indicando o valor inicial da variável independente.
   - `y0`: `float` indicando o valor inicial y(x0).
   - `x_fim`: `float` indicando o limite final do intervalo.
   - `h`: `float` indicando o tamanho do passo de integração.
   - `solucao_exata`: `Callable[[float], float] | None` (opcional) com a solução
     analítica exata para comparação posterior na análise e no gráfico.

2. `ResultadoMetodo`:
   Empacota a resposta gerada por qualquer método de solução do PVI.
   Campos esperados:
   - `nome`: `str` com o identificador legível da curva (ex.: "Método de Euler",
     "Runge-Kutta (RK4)", "Solução Exata").
   - `x`: `list[float]` contendo os pontos discretos do domínio (x_0, x_1, ..., x_n).
   - `y`: `list[float]` contendo os valores calculados correspondentes (y_0, y_1, ..., y_n).

O que NÃO fazer neste arquivo
-----------------------------
- Não colocar cálculos matemáticos, valores fixos da questão (como 0, 5 ou 0.1)
  nem lógica de métodos numéricos. Este arquivo define apenas "formatos de dados".
"""
