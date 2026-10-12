"""
Construção do pipeline do modelo e regras de uso da previsão no negócio.

O pipeline junta pré-processamento + modelo em um único objeto, para que o
mesmo tratamento aplicado no treino seja aplicado automaticamente em novos
pedidos (evita divergências entre treino e produção).
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.nps_utils import PRE_SURVEY_FEATURES

CATEGORICAL_FEATURES = ["customer_region"]
NUMERIC_FEATURES = [c for c in PRE_SURVEY_FEATURES if c not in CATEGORICAL_FEATURES]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Faixas de risco usadas pela operação a partir da nota prevista.
# Limites escolhidos para casar com a régua do NPS (nota < 7 = detrator)
# e para separar os casos "irrecuperáveis sem ação forte" (< 4).
RISK_BANDS = [
    (-np.inf, 4.0, "Risco alto"),
    (4.0, 7.0, "Risco moderado"),
    (7.0, np.inf, "Risco baixo"),
]
RISK_BAND_ORDER = [label for _, _, label in RISK_BANDS]


def build_preprocessor(scale_numeric: bool = True, numeric_features: list = None) -> ColumnTransformer:
    """
    Pré-processamento:
    - numéricas: padronização (média 0, desvio 1) -> coeficientes comparáveis
      no modelo linear; árvores não precisam, por isso é opcional;
    - numeric_features permite trocar a lista de numéricas (usado só no
      experimento de vazamento do notebook 04);
    - região: one-hot encoding (uma coluna 0/1 por região).
    """
    numeric_step = StandardScaler() if scale_numeric else "passthrough"
    numeric_features = numeric_features or NUMERIC_FEATURES
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_step, numeric_features),
            ("categorical", OneHotEncoder(drop="first", handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ],
        verbose_feature_names_out=False,
    )


def build_pipeline(model, scale_numeric: bool = True, numeric_features: list = None) -> Pipeline:
    """Encadeia pré-processamento e modelo em um único objeto treinável."""
    return Pipeline([("preprocess", build_preprocessor(scale_numeric, numeric_features)), ("model", model)])


def assign_risk_band(predicted_score: pd.Series) -> pd.Series:
    """Converte a nota prevista em uma faixa de risco acionável."""
    labels = pd.cut(
        predicted_score,
        bins=[low for low, _, _ in RISK_BANDS] + [RISK_BANDS[-1][1]],
        labels=RISK_BAND_ORDER,
        right=False,
    )
    return labels


def score_orders(pipeline: Pipeline, orders: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica o modelo a pedidos em andamento e devolve, para cada pedido:
    nota prevista (0-10) e faixa de risco.
    """
    predicted = np.clip(pipeline.predict(orders[MODEL_FEATURES]), 0, 10)
    result = orders.copy()
    result["predicted_nps"] = predicted.round(1)
    result["risk_band"] = assign_risk_band(result["predicted_nps"])
    return result
