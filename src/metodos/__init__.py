"""
Subpacote `src.metodos` contendo os métodos numéricos de resolução de PVIs.

Propósito
---------
Agrupar implementações independentes de métodos numéricos de passo simples para
Equações Diferenciais Ordinárias de 1ª ordem:
- `euler`: Método de Euler (Letra a).
- `runge_kutta`: Método de Runge-Kutta clássico de 4ª ordem — RK4 (Letra b).

Padrão de assinatura esperado para todos os métodos deste pacote
----------------------------------------------------------------
Cada módulo deve expor uma função principal clara (ex.: `resolver_euler(pvi)` e
`resolver_runge_kutta(pvi)`) que:
- Recebe um `ProblemaPVI` (definido em `src.contratos`).
- Retorna um `ResultadoMetodo` (definido em `src.contratos`).

Nenhum método aqui dentro deve conhecer a equação específica do trabalho; todos
devem operar genericamente chamando `pvi.f(x, y)`.
"""
