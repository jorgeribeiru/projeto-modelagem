"""
Pacote principal `src` do projeto de Modelagem Matemática.

Organização interna
-------------------
- `contratos`: estruturas de dados padronizadas (`ProblemaPVI` e `ResultadoMetodo`)
  que servem de interface comum entre todos os módulos da equipe.
- `problema`: formulação matemática específica do PVI do enunciado, solução exata
  analítica e geração segura da malha discreta de pontos `x`.
- `metodos`: pacote contendo os algoritmos numéricos isolados (`euler` e `runge_kutta`).
- `analise`: pós-processamento numérico (cálculo de erros e tabelas comparativas).
- `visualizacao`: geração do gráfico comparativo das três soluções em um único frame.

Regra arquitetural
------------------
Os módulos irmãos dentro de `src` não devem criar dependências cruzadas entre si;
a comunicação entre eles ocorre por meio das estruturas definidas em `src.contratos`
sob coordenação do `main.py`.
"""
