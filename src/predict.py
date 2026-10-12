"""
Script de uso do modelo: pontua pedidos e gera a lista priorizada de risco.

Exemplo (a partir da raiz do repositório):
    python -m src.predict --input data/raw/desafio_nps_fase_1.csv --output reports/pedidos_pontuados.csv

O arquivo de entrada precisa ter as colunas operacionais usadas no treino
(ver MODEL_FEATURES em src/modeling.py). As colunas de pós-experiência
(nps_score, csat_internal_score, repeat_purchase_30d) NÃO são necessárias.
"""

import argparse

import joblib
import pandas as pd

from src.modeling import RISK_BAND_ORDER, score_orders
from src.nps_utils import MODELS_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Pontua pedidos com a nota NPS prevista e a faixa de risco.")
    parser.add_argument("--input", required=True, help="CSV com os pedidos a pontuar")
    parser.add_argument("--output", required=True, help="CSV de saída com nota prevista e faixa de risco")
    parser.add_argument("--model", default=str(MODELS_DIR / "nps_regressor.joblib"), help="Caminho do modelo treinado")
    args = parser.parse_args()

    pipeline = joblib.load(args.model)
    orders = pd.read_csv(args.input)
    scored = score_orders(pipeline, orders)

    # Lista priorizada: pedidos de maior risco (menor nota prevista) primeiro
    scored = scored.sort_values("predicted_nps")
    scored.to_csv(args.output, index=False)

    print(f"{len(scored)} pedidos pontuados -> {args.output}")
    print(scored["risk_band"].value_counts().reindex(RISK_BAND_ORDER).to_string())


if __name__ == "__main__":
    main()
