"""
Contratos de dados compartilhados entre os módulos (`dataclasses` + `typing`).

Permite que os 4 integrantes programem em paralelo usando o mesmo formato de entrada e saída.

Estruturas para declarar aqui:
1. `ProblemaPVI` (entrada dos métodos):
   - `f`: `Callable[[float, float], float]` — derivada f(x, y).
   - `x0`: `float` — início do intervalo.
   - `y0`: `float` — condição inicial y(x0).
   - `x_fim`: `float` — fim do intervalo.
   - `h`: `float` — tamanho do passo.
   - `solucao_exata`: `Callable[[float], float] | None` — função analítica phi(x), se conhecida.

2. `ResultadoMetodo` (saída padronizada dos métodos):
   - `nome`: `str` — nome legível da curva para legendas e tabelas.
   - `x`: `list[float]` — pontos da malha (x_0, ..., x_n).
   - `y`: `list[float]` — valores calculados (y_0, ..., y_n).
"""
