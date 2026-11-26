"""
Interface de análise interativa (CustomTkinter + matplotlib embutido).

Módulos:
- `estado`: filtros e inspeção de pontos (lógica pura, testável sem display).
- `tema`: cores e fontes da janela, derivadas da paleta de `src.visualizacao`.
- `app`: janela principal; `painel_filtros`, `inspetor` e `guia` são seus componentes.

Recebe um `CenarioComparacao` e um callback `recalcular(h)` do `main.py`, sem importar solvers.
"""
from pathlib import Path

from src.contratos import CenarioComparacao, FuncaoRecalculo


def abrir_interface(
    cenario: CenarioComparacao,
    recalcular: FuncaoRecalculo,
    mostrar_guia: bool = True,
    pasta_exportacao: Path | None = None,
) -> None:
    """Abre a janela de análise e bloqueia até ela ser fechada."""
    from src.interface.app import AplicativoAnalise  # Tk só é carregado quando a janela é pedida.

    app = AplicativoAnalise(cenario, recalcular, mostrar_guia, pasta_exportacao)
    app.mainloop()
