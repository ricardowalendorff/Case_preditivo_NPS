"""
Funções e constantes compartilhadas pelos notebooks do Case Preditivo de NPS.

Centralizar caminhos, listas de variáveis e regras de negócio (como a
classificação promotor/neutro/detrator) em um único lugar evita que cada
notebook tenha a sua própria versão das mesmas definições.
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Caminhos do projeto (resolvidos a partir da pasta deste arquivo)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "desafio_nps_fase_1.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "nps_tratado.csv"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
MODELS_DIR = PROJECT_ROOT / "models"

RANDOM_STATE = 42

# ---------------------------------------------------------------------------
# Regra de negócio do NPS
# ---------------------------------------------------------------------------
# A metodologia clássica usa notas inteiras: 0-6 detrator, 7-8 neutro,
# 9-10 promotor. Como a base traz notas com casas decimais (ex.: 6.9),
# adotamos limites contínuos: nota < 7 -> detrator; 7 <= nota < 9 -> neutro;
# nota >= 9 -> promotor. Assim 6.9 continua sendo detrator (não "arredonda"
# um cliente insatisfeito para neutro).
DETRACTOR_THRESHOLD = 7.0
PROMOTER_THRESHOLD = 9.0
NPS_CATEGORY_ORDER = ["Detrator", "Neutro", "Promotor"]

# ---------------------------------------------------------------------------
# Grupos de variáveis
# ---------------------------------------------------------------------------
ID_COLUMNS = ["customer_id", "order_id"]
TARGET_COLUMN = "nps_score"

CUSTOMER_FEATURES = ["customer_age", "customer_region", "customer_tenure_months"]
ORDER_FEATURES = ["order_value", "items_quantity", "discount_value", "payment_installments"]
LOGISTICS_FEATURES = ["delivery_time_days", "delivery_delay_days", "freight_value", "delivery_attempts"]
SERVICE_FEATURES = ["customer_service_contacts", "resolution_time_days", "complaints_count"]

# Variáveis observadas DEPOIS (ou no mesmo momento) da pesquisa de NPS.
# Elas são consequência da satisfação, não causa operacional, e não estariam
# disponíveis no momento em que queremos prever a nota -> risco de vazamento
# de informação (data leakage) se entrarem no modelo.
POST_EXPERIENCE_FEATURES = ["repeat_purchase_30d", "csat_internal_score"]

# Variáveis disponíveis antes da pesquisa e que podem alimentar o modelo.
PRE_SURVEY_FEATURES = CUSTOMER_FEATURES + ORDER_FEATURES + LOGISTICS_FEATURES + SERVICE_FEATURES

# Nomes amigáveis para gráficos e tabelas voltados ao negócio.
FRIENDLY_NAMES = {
    "customer_age": "Idade do cliente",
    "customer_region": "Região",
    "customer_tenure_months": "Tempo de casa (meses)",
    "order_value": "Valor do pedido (R$)",
    "items_quantity": "Qtd. de itens",
    "discount_value": "Desconto (R$)",
    "payment_installments": "Nº de parcelas",
    "delivery_time_days": "Tempo de entrega (dias)",
    "delivery_delay_days": "Atraso na entrega (dias)",
    "freight_value": "Frete (R$)",
    "delivery_attempts": "Tentativas de entrega",
    "customer_service_contacts": "Contatos com o SAC",
    "resolution_time_days": "Tempo de resolução (dias)",
    "complaints_count": "Nº de reclamações",
    "repeat_purchase_30d": "Recompra em 30 dias",
    "csat_internal_score": "CSAT interno",
    "nps_score": "Nota NPS",
}


# Faixas criadas no notebook 02. O CSV não guarda a ordem das categorias,
# então ela é restaurada aqui (senão "Até 2 dias" iria para o fim, por ordem alfabética).
BAND_ORDERS = {
    "nps_category": NPS_CATEGORY_ORDER,
    "delay_band": ["No prazo", "1 dia", "2 dias", "3 dias", "4+ dias"],
    "complaints_band": ["0-1", "2", "3", "4", "5", "6+"],
    "contacts_band": ["0", "1", "2", "3", "4+"],
    "resolution_band": ["Até 2 dias", "3-5 dias", "6-8 dias", "9+ dias"],
    "age_band": ["18-25", "26-35", "36-45", "46-55", "56+"],
    "tenure_band": ["Até 1 ano", "1-2 anos", "2-5 anos", "5+ anos"],
    "order_value_band": ["Até R$150", "R$150-300", "R$300-500", "R$500-800", "R$800+"],
}


def load_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Lê a base original (CSV) sem nenhuma transformação."""
    return pd.read_csv(path)


def load_processed_data(path: Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Lê a base tratada pelo notebook 02 e restaura a ordem das faixas."""
    df = pd.read_csv(path, dtype={"contacts_band": str, "complaints_band": str})
    for column, order in BAND_ORDERS.items():
        df[column] = pd.Categorical(df[column], categories=order, ordered=True)
    return df


def classify_nps(score: pd.Series) -> pd.Series:
    """Converte a nota (0-10) em Detrator / Neutro / Promotor."""
    category = np.select(
        [score < DETRACTOR_THRESHOLD, score < PROMOTER_THRESHOLD],
        ["Detrator", "Neutro"],
        default="Promotor",
    )
    return pd.Series(pd.Categorical(category, categories=NPS_CATEGORY_ORDER, ordered=True), index=score.index)


def nps_index(score: pd.Series) -> float:
    """Calcula o NPS (% promotores - % detratores), em pontos de -100 a +100."""
    category = classify_nps(score)
    return 100 * ((category == "Promotor").mean() - (category == "Detrator").mean())


def nps_summary_by(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """
    Resume a satisfação por grupo, na linguagem do negócio:
    quantidade de pedidos, nota média, % detratores, % promotores e NPS.
    """
    grouped = df.groupby(group_column, observed=True)["nps_score"]
    summary = pd.DataFrame(
        {
            "pedidos": grouped.size(),
            "nota_media": grouped.mean(),
            "pct_detratores": grouped.apply(lambda s: 100 * (s < DETRACTOR_THRESHOLD).mean()),
            "pct_promotores": grouped.apply(lambda s: 100 * (s >= PROMOTER_THRESHOLD).mean()),
            "nps": grouped.apply(nps_index),
        }
    )
    return summary.round(1)
