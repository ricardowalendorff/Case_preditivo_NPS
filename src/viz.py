"""
Padrão visual dos gráficos do projeto (notebooks e apresentação).

Regras adotadas:
- Uma cor principal (azul) para dados "neutros" e vermelho apenas para
  destacar o que é problema (detratores, ponto de ruptura);
- Categorias do NPS: Detrator = vermelho, Neutro = cinza, Promotor = azul;
- Eixos e grade discretos, rótulos diretos só onde ajudam a leitura;
- Títulos que contam a conclusão ("o que o gráfico diz"), não só o nome da variável.
"""

import matplotlib.pyplot as plt
import seaborn as sns

from src.nps_utils import FIGURES_DIR

# Paleta (tons validados para contraste e daltonismo)
COLOR_PRIMARY = "#2a78d6"      # azul: série principal / promotores
COLOR_ALERT = "#e34948"        # vermelho: detratores / ponto crítico
COLOR_NEUTRAL = "#b5b3ad"      # cinza: neutros / contexto
COLOR_MUTED = "#d9d8d4"        # cinza claro: barras sem destaque
COLOR_TEXT = "#0b0b0b"
COLOR_TEXT_SECONDARY = "#52514e"
COLOR_GRID = "#e6e5e1"

NPS_CATEGORY_COLORS = {"Detrator": COLOR_ALERT, "Neutro": COLOR_NEUTRAL, "Promotor": COLOR_PRIMARY}

# Mapa divergente para heatmaps de nota: vermelho (nota baixa) -> cinza (7) -> azul (nota alta)
DIVERGING_CMAP = sns.blend_palette([COLOR_ALERT, "#f0efec", COLOR_PRIMARY], as_cmap=True)


def set_style() -> None:
    """Aplica o estilo padrão a todos os gráficos matplotlib/seaborn."""
    sns.set_theme(style="white")
    plt.rcParams.update(
        {
            "figure.dpi": 110,
            "savefig.dpi": 200,
            "savefig.bbox": "tight",
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.labelcolor": COLOR_TEXT_SECONDARY,
            "axes.edgecolor": COLOR_GRID,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": COLOR_GRID,
            "grid.linewidth": 0.8,
            "xtick.color": COLOR_TEXT_SECONDARY,
            "ytick.color": COLOR_TEXT_SECONDARY,
            "text.color": COLOR_TEXT,
            "legend.frameon": False,
        }
    )


def save_figure(fig, file_name: str) -> None:
    """Salva a figura em reports/figures/ (usada também nos slides)."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / file_name, facecolor="white")


def label_bars(ax, fmt: str = "{:.0f}", suffix: str = "", inside: bool = False, fontsize: int = 10) -> None:
    """Escreve o valor de cada barra (rótulo direto, cor de texto, não da série)."""
    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[fmt.format(v) + suffix for v in container.datavalues],
            padding=3,
            fontsize=fontsize,
            color=COLOR_TEXT_SECONDARY,
            label_type="center" if inside else "edge",
        )
