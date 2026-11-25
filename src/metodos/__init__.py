"""
Subpacote `src.metodos` com os solvers numéricos de PVIs de 1ª ordem.

Padrão de todos os métodos:
- Recebem um `ProblemaPVI` e retornam um `ResultadoMetodo`.
- Operam de forma genérica chamando `pvi.f(x, y)`, sem fixar a EDO da questão.
"""
