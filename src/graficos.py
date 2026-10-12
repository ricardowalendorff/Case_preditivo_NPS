"""
Padrão visual dos gráficos do projeto.

Regras (Aulas 3 e 4 de Análise Exploratória):
- cor usada com intenção: azul para o que é bom, vermelho só para destacar
  problemas (detratores, ponto de ruptura) e cinza para contexto;
- títulos que contam a conclusão do gráfico, não apenas o nome da variável;
- eixos começando em zero nas comparações, sem efeitos 3D ou decoração.
"""

import matplotlib.pyplot as plt
import seaborn as sns

from src.funcoes_nps import PASTA_FIGURAS

COR_AZUL = "#2a78d6"  # promotores / situação boa
COR_VERMELHA = "#e34948"  # detratores / ponto crítico
COR_CINZA = "#b5b3ad"  # neutros / contexto
COR_CINZA_CLARO = "#d9d8d4"  # barras sem destaque

CORES_CATEGORIA_NPS = {"Detrator": COR_VERMELHA, "Neutro": COR_CINZA, "Promotor": COR_AZUL}


def configurar_estilo() -> None:
    """Aplica um estilo limpo, com grade discreta, a todos os gráficos."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (9, 5)
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.titlelocation"] = "left"


def salvar_figura(figura, nome_arquivo: str) -> None:
    """
    Salva a figura em reports/figures/.

    Args:
        figura: Figura do matplotlib.
        nome_arquivo: Nome do arquivo PNG (ex.: "04_atraso.png").
    """
    PASTA_FIGURAS.mkdir(parents=True, exist_ok=True)
    figura.savefig(PASTA_FIGURAS / nome_arquivo, dpi=150, bbox_inches="tight")


def rotular_barras(eixo, formato: str = "{:.0f}", sufixo: str = "") -> None:
    """
    Escreve o valor em cima de cada barra do gráfico.

    Args:
        eixo: Eixo (ax) do matplotlib que contém as barras.
        formato: Formato do número (ex.: "{:.1f}" para uma casa decimal).
        sufixo: Texto colocado depois do número (ex.: "%").
    """
    for grupo_de_barras in eixo.containers:
        rotulos = [formato.format(valor) + sufixo for valor in grupo_de_barras.datavalues]
        eixo.bar_label(grupo_de_barras, labels=rotulos, padding=3, fontsize=10)
