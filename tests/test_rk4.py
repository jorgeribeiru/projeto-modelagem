"""
Testes de sanidade para o Método de Runge-Kutta (`src.metodos.runge_kutta`).

Cenários sugeridos:
- Condição inicial preservada (`x[0] == 0.0` e `y[0] == 3.0`).
- Malha com exatamente 51 pontos, terminando em `x[-1] == 5.0`.
- Erro máximo em `h = 0.1` na casa de 10^-5 ou menor frente à solução exata.
- Erro máximo cai aproximadamente 16 vezes (~2^4) ao testar com `h = 0.05`.
"""
