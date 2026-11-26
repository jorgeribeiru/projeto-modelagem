"""
Ponto de entrada do projeto (Orquestrador).

Papel: conectar os módulos na ordem de execução, sem fazer contas nem configurar gráficos aqui.

Fluxo esperado:
1. Instanciar o PVI definido em `src.problema`.
2. Resolver pelo Método de Euler (`src.metodos.euler`) — Letra (a).
3. Resolver pelo Método de Runge-Kutta (`src.metodos.runge_kutta`) — Letra (b).
4. Gerar métricas e tabela comparativa de erros em `src.analise`.
5. Plotar e salvar o gráfico comparativo das 3 curvas em `src.visualizacao` — Letra (c).
6. Com `--interativo`, abrir a interface de análise (`src.interface`).

Uso:
    python main.py                      # gera resultados/comparacao_pvi.png e .pdf
    python main.py --interativo         # também abre a interface de análise
    python main.py --interativo --sem-guia
"""
import argparse
import dataclasses
import sys
from collections.abc import Sequence
from pathlib import Path

from src.analise import calcular_erros_absolutos, calcular_erros_relativos, exibir_analise_erros
from src.contratos import CenarioComparacao
from src.metodos.euler import resolver_euler
from src.metodos.runge_kutta import resolver_runge_kutta
from src.problema import EQUACAO_TEXTO, SOLUCAO_EXATA_TEXTO, criar_pvi_trabalho
from src.visualizacao import plotar_comparacao

PASTA_RESULTADOS = Path(__file__).parent / "resultados"
NOME_FIGURA = "comparacao_pvi"


def montar_cenario(h: float | None = None) -> CenarioComparacao:
    """Resolve o PVI da questão com o passo `h` e calcula os erros de cada método."""
    pvi = criar_pvi_trabalho()
    if h is not None:
        pvi = dataclasses.replace(pvi, h=h)

    resultados = [resolver_euler(pvi), resolver_runge_kutta(pvi)]

    return CenarioComparacao(
        pvi=pvi,
        resultados=resultados,
        erros_absolutos={r.nome: calcular_erros_absolutos(pvi.solucao_exata, r) for r in resultados},
        erros_relativos={r.nome: calcular_erros_relativos(pvi.solucao_exata, r) for r in resultados},
        equacao=EQUACAO_TEXTO,
        solucao_exata_texto=SOLUCAO_EXATA_TEXTO,
    )


def _ler_argumentos(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve o PVI por Euler e RK4 e compara com a solução exata.")
    parser.add_argument("--interativo", action="store_true", help="abre a interface de análise do gráfico")
    parser.add_argument("--sem-guia", action="store_true", help="não exibe o guia de boas-vindas da interface")
    parser.add_argument("--saida", type=Path, default=PASTA_RESULTADOS, help="pasta onde a figura é salva")
    return parser.parse_args(list(argv))


def main(argv: Sequence[str] = ()) -> None:
    """Executa o fluxo completo de resolução, análise e plotagem do PVI."""
    args = _ler_argumentos(argv)
    cenario = montar_cenario()

    for res in cenario.resultados:
        print(
            f"{res.nome}: {len(res.x)} pontos | "
            f"y({res.x[0]}) = {res.y[0]:.4f} -> y({res.x[-1]}) = {res.y[-1]:.6f}"
        )

    exibir_analise_erros(cenario.pvi.solucao_exata, cenario.resultados)

    arquivos = plotar_comparacao(cenario, args.saida / NOME_FIGURA)
    print("\nGráfico comparativo salvo em:", ", ".join(str(a) for a in arquivos))

    if args.interativo:
        from src.interface import abrir_interface

        abrir_interface(cenario, recalcular=montar_cenario, mostrar_guia=not args.sem_guia)


if __name__ == "__main__":
    main(sys.argv[1:])
