"""
Preparação das variáveis do modelo e regras de uso da previsão no negócio.

As mesmas funções são usadas no treino (notebook 04) e na pontuação de
pedidos novos (src/prever.py), garantindo que o tratamento seja idêntico.
"""

import numpy as np
import pandas as pd

from src.funcoes_nps import COLUNAS_PRE_PESQUISA

REGIOES = ["Centro-Oeste", "Nordeste", "Norte", "Sudeste", "Sul"]

# Faixas de risco a partir da nota prevista. Os limites seguem a régua do NPS
# (nota < 7 = detrator) e separam os casos mais graves (nota < 4).
LIMITES_RISCO = [-np.inf, 4.0, 7.0, np.inf]
FAIXAS_RISCO = ["Risco alto", "Risco moderado", "Risco baixo"]


def preparar_variaveis(pedidos: pd.DataFrame) -> pd.DataFrame:
    """
    Monta a tabela de entrada do modelo a partir das colunas originais.

    A região (texto) vira colunas 0/1 (one-hot encoding). A primeira região
    (Centro-Oeste) fica como referência, para evitar colunas redundantes.

    Args:
        pedidos: DataFrame com as colunas disponíveis antes da pesquisa.

    Returns:
        DataFrame só com números, pronto para o modelo.
    """
    variaveis = pedidos[COLUNAS_PRE_PESQUISA].copy()
    regiao = pd.Categorical(variaveis.pop("customer_region"), categories=REGIOES)
    colunas_regiao = pd.get_dummies(regiao, prefix="regiao", drop_first=True, dtype=int)
    colunas_regiao.index = variaveis.index
    return pd.concat([variaveis, colunas_regiao], axis=1)


def classificar_risco(nota_prevista: pd.Series) -> pd.Series:
    """
    Converte a nota prevista em uma faixa de risco acionável.

    Args:
        nota_prevista: Série com as notas previstas pelo modelo.

    Returns:
        Série categórica: Risco alto, Risco moderado ou Risco baixo.
    """
    return pd.cut(nota_prevista, bins=LIMITES_RISCO, labels=FAIXAS_RISCO, right=False)


def pontuar_pedidos(modelo, pedidos: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica o modelo a pedidos em andamento.

    Args:
        modelo: Modelo de regressão já treinado (com método predict).
        pedidos: DataFrame com as colunas disponíveis antes da pesquisa.

    Returns:
        Cópia dos pedidos com as colunas nota_prevista e faixa_risco.
    """
    resultado = pedidos.copy()
    nota_prevista = modelo.predict(preparar_variaveis(pedidos))
    # A nota só existe entre 0 e 10, então limitamos a previsão a esse intervalo
    resultado["nota_prevista"] = np.clip(nota_prevista, 0, 10).round(1)
    resultado["faixa_risco"] = classificar_risco(resultado["nota_prevista"])
    return resultado
