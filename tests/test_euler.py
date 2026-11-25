"""
Testes de sanidade para o Método de Euler (`src.metodos.euler`).

Cenários sugeridos:
- Condição inicial preservada (`x[0] == 0.0` e `y[0] == 3.0`).
- Malha com exatamente 51 pontos, terminando em `x[-1] == 5.0`.
- Primeiro passo igual ao cálculo manual: `y[1] == 2.5`.
- Erro máximo cai aproximadamente pela metade (~2x) ao testar com `h = 0.05`.
"""
