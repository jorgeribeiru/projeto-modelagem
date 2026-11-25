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
from dataclasses import dataclass
from collections.abc import Callable

FuncaoDerivada = Callable[[float, float], float]
FuncaoExata = Callable[[float], float]

@dataclass
class ProblemaPVI:
    """Entrada padronizada de um PVI de 1ª ordem: y' = f(x,y), y(x0) = y0"""

    f: FuncaoDerivada
    x0: float
    y0: float
    x_fim: float
    h: float
    solucao_exata: FuncaoExata | None = None


@dataclass
class ResultadoMetodo:
    """Saída padronizada devolvida pelos métodos numéricos"""

    nome: str
    x: list[float]
    y: list[float]