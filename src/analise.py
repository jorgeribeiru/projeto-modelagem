"""
Cálculo de erros e tabelas comparativas para embasar o relatório (Seção 6 da apostila).

O que implementar aqui:
- Receber a função `solucao_exata` e uma lista de `ResultadoMetodo`.
- Calcular o erro absoluto em cada ponto: erro_n = |phi(x_n) - y_n|.
- Extrair erro máximo, erro médio e erro final (em x = 5.0) de cada método.
- Exibir no terminal ou exportar tabela comparativa (x, Exata, Euler, RK4 e erros)
  para facilitar os comentários do relatório em PDF.
"""
import math
from dataclasses import dataclass

from src.contratos import FuncaoExata, ResultadoMetodo


@dataclass
class ResumoErro:
    """Métricas resumidas do erro absoluto de um método numérico."""

    nome: str
    erro_maximo: float
    x_erro_maximo: float
    erro_medio: float
    erro_final: float


def calcular_erros_absolutos(
    solucao_exata: FuncaoExata,
    resultado: ResultadoMetodo,
) -> list[float]:
    """Calcula |phi(x_n) - y_n| em cada ponto da malha."""
    return [abs(solucao_exata(x) - y) for x, y in zip(resultado.x, resultado.y)]


def calcular_erros_relativos(
    solucao_exata: FuncaoExata,
    resultado: ResultadoMetodo,
) -> list[float]:
    """Calcula |phi(x_n) - y_n| / |phi(x_n)|; `nan` onde phi(x_n) = 0."""
    erros = calcular_erros_absolutos(solucao_exata, resultado)
    relativos = []
    for x, erro in zip(resultado.x, erros):
        referencia = abs(solucao_exata(x))
        relativos.append(erro / referencia if referencia != 0.0 else math.nan)
    return relativos


def resumir_erro(
    solucao_exata: FuncaoExata,
    resultado: ResultadoMetodo,
) -> ResumoErro:
    """Extrai erro máximo (e onde ocorre), erro médio e erro no último ponto."""
    erros = calcular_erros_absolutos(solucao_exata, resultado)
    indice_max = max(range(len(erros)), key=lambda i: erros[i])

    return ResumoErro(
        nome=resultado.nome,
        erro_maximo=erros[indice_max],
        x_erro_maximo=resultado.x[indice_max],
        erro_medio=sum(erros) / len(erros),
        erro_final=erros[-1],
    )


def exibir_analise_erros(
    solucao_exata: FuncaoExata | None,
    resultados: list[ResultadoMetodo],
    passo_amostra: int = 5,
) -> None:
    """Exibe no terminal as métricas de erro e uma tabela comparativa resumida."""
    if solucao_exata is None or not resultados:
        return

    print("\n=== Resumo de Erros Absolutos ===")
    erros_por_metodo: list[list[float]] = []
    for res in resultados:
        resumo = resumir_erro(solucao_exata, res)
        erros_por_metodo.append(calcular_erros_absolutos(solucao_exata, res))
        print(
            f"- {resumo.nome}: máx = {resumo.erro_maximo:.4e} (em x = {resumo.x_erro_maximo}) | "
            f"médio = {resumo.erro_medio:.4e} | final = {resumo.erro_final:.4e}"
        )

    colunas_metodos = " | ".join(f"{res.nome:>22}" for res in resultados)
    cabecalho = f"\n{'x':>5} | {'Exata':>10} | {colunas_metodos}"
    print(cabecalho)
    print("-" * len(cabecalho))

    malha_x = resultados[0].x
    for i in range(0, len(malha_x), passo_amostra):
        x = malha_x[i]
        y_exato = solucao_exata(x)
        celulas = " | ".join(
            f"{res.y[i]:>10.6f} ({erros[i]:.2e})"
            for res, erros in zip(resultados, erros_por_metodo)
        )
        print(f"{x:>5.1f} | {y_exato:>10.6f} | {celulas}")