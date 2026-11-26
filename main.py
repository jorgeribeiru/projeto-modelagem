"""
Ponto de entrada do projeto (Orquestrador).

Papel: conectar os módulos na ordem de execução, sem fazer contas nem configurar gráficos aqui.

Fluxo esperado:
1. Instanciar o PVI definido em `src.problema`.
2. Resolver pelo Método de Euler (`src.metodos.euler`) — Letra (a).
3. Resolver pelo Método de Runge-Kutta (`src.metodos.runge_kutta`) — Letra (b).
4. Gerar métricas e tabela comparativa de erros em `src.analise`.
5. Plotar e salvar o gráfico comparativo das 3 curvas em `src.visualizacao` — Letra (c).
"""
from src.metodos.euler import resolver_euler
from src.metodos.runge_kutta import resolver_runge_kutta
from src.problema import criar_pvi_trabalho
# from src.analise import exibir_analise_erros
# from src.visualizacao import plotar_comparacao


def main() -> None:
    """Executa o fluxo completo de resolução, análise e plotagem do PVI."""
    pvi = criar_pvi_trabalho()

    resultado_euler = resolver_euler(pvi)
    resultado_rk4 = resolver_runge_kutta(pvi)

    resultados = [
        resultado_euler,
        resultado_rk4,
    ]

    for res in resultados:
        print(
            f"{res.nome}: {len(res.x)} pontos | "
            f"y({res.x[0]}) = {res.y[0]:.4f} -> y({res.x[-1]}) = {res.y[-1]:.6f}"
        )

    # exibir_analise_erros(pvi.solucao_exata, resultados)
    # plotar_comparacao(pvi, resultados, caminho_saida="resultados/comparacao_pvi.png")


if __name__ == "__main__":
    main()
