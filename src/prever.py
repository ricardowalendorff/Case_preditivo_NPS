"""
Pontua pedidos com o modelo treinado e gera a lista priorizada por risco.

Uso (a partir da raiz do repositório):
    python -m src.prever --entrada data/raw/desafio_nps_fase_1.csv --saida reports/pedidos_pontuados.csv

O arquivo de entrada precisa das colunas operacionais (as mesmas do treino).
As colunas de pós-pesquisa (nps_score, csat_internal_score,
repeat_purchase_30d) NÃO são necessárias.
"""

import argparse

import joblib
import pandas as pd

from src.funcoes_nps import PASTA_MODELOS
from src.modelo import FAIXAS_RISCO, pontuar_pedidos


def main() -> None:
    """Lê os pedidos, aplica o modelo e salva o resultado ordenado por risco."""
    parser = argparse.ArgumentParser(description="Pontua pedidos com a nota NPS prevista.")
    parser.add_argument("--entrada", required=True, help="CSV com os pedidos a pontuar")
    parser.add_argument("--saida", required=True, help="CSV de saída com nota prevista e faixa de risco")
    parser.add_argument("--modelo", default=str(PASTA_MODELOS / "modelo_nps.joblib"), help="Arquivo do modelo")
    argumentos = parser.parse_args()

    modelo = joblib.load(argumentos.modelo)
    pedidos = pd.read_csv(argumentos.entrada)
    pedidos_pontuados = pontuar_pedidos(modelo, pedidos)

    # Lista priorizada: menor nota prevista (maior risco) primeiro
    pedidos_pontuados = pedidos_pontuados.sort_values("nota_prevista")
    pedidos_pontuados.to_csv(argumentos.saida, index=False)

    print(f"{len(pedidos_pontuados)} pedidos pontuados -> {argumentos.saida}")
    print(pedidos_pontuados["faixa_risco"].value_counts().reindex(FAIXAS_RISCO).to_string())


if __name__ == "__main__":
    main()
