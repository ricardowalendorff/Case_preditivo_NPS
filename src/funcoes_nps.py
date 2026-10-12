"""
Funções e constantes usadas por todos os notebooks do projeto.

Seguindo o "workflow híbrido" (Aula 1 de Ambientes de Trabalho), a lógica
que se repete nos notebooks foi movida para cá: assim cada regra de negócio
(como a classificação promotor/neutro/detrator) existe em um só lugar.
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Caminhos do projeto
# ---------------------------------------------------------------------------
PASTA_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_DADOS_BRUTOS = PASTA_PROJETO / "data" / "raw" / "desafio_nps_fase_1.csv"
CAMINHO_DADOS_TRATADOS = PASTA_PROJETO / "data" / "processed" / "nps_tratado.csv"
PASTA_FIGURAS = PASTA_PROJETO / "reports" / "figures"
PASTA_MODELOS = PASTA_PROJETO / "models"

SEMENTE_ALEATORIA = 42

# ---------------------------------------------------------------------------
# Regra de negócio do NPS
# ---------------------------------------------------------------------------
# Metodologia clássica (notas inteiras): 0-6 detrator, 7-8 neutro, 9-10 promotor.
# Como a base tem notas com casas decimais (ex.: 6.9), usamos limites
# contínuos: nota < 7 = detrator; 7 <= nota < 9 = neutro; nota >= 9 = promotor.
LIMITE_DETRATOR = 7.0
LIMITE_PROMOTOR = 9.0
CATEGORIAS_NPS = ["Detrator", "Neutro", "Promotor"]

# ---------------------------------------------------------------------------
# Grupos de colunas (os nomes das colunas são os originais da base, em inglês)
# ---------------------------------------------------------------------------
COLUNAS_ID = ["customer_id", "order_id"]
COLUNA_ALVO = "nps_score"

COLUNAS_CLIENTE = ["customer_age", "customer_region", "customer_tenure_months"]
COLUNAS_PEDIDO = ["order_value", "items_quantity", "discount_value", "payment_installments"]
COLUNAS_LOGISTICA = ["delivery_time_days", "delivery_delay_days", "freight_value", "delivery_attempts"]
COLUNAS_ATENDIMENTO = ["customer_service_contacts", "resolution_time_days", "complaints_count"]

# Medidas coletadas junto ou DEPOIS da pesquisa de NPS. Não podem entrar no
# modelo, pois não existem no momento da previsão (vazamento / data leakage).
COLUNAS_POS_PESQUISA = ["repeat_purchase_30d", "csat_internal_score"]

# Colunas disponíveis ANTES da pesquisa (candidatas a entrar no modelo)
COLUNAS_PRE_PESQUISA = COLUNAS_CLIENTE + COLUNAS_PEDIDO + COLUNAS_LOGISTICA + COLUNAS_ATENDIMENTO

# Nomes em português para gráficos e tabelas
NOMES_AMIGAVEIS = {
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
# então ela é restaurada na leitura (senão "Até 2 dias" iria para o fim).
ORDEM_DAS_FAIXAS = {
    "categoria_nps": CATEGORIAS_NPS,
    "faixa_atraso": ["No prazo", "1 dia", "2 dias", "3 dias", "4+ dias"],
    "faixa_reclamacoes": ["0-1", "2", "3", "4", "5", "6+"],
    "faixa_contatos": ["0", "1", "2", "3", "4+"],
    "faixa_resolucao": ["Até 2 dias", "3-5 dias", "6-8 dias", "9+ dias"],
    "faixa_idade": ["18-25", "26-35", "36-45", "46-55", "56+"],
    "faixa_tempo_casa": ["Até 1 ano", "1-2 anos", "2-5 anos", "5+ anos"],
    "faixa_valor_pedido": ["Até R$150", "R$150-300", "R$300-500", "R$500-800", "R$800+"],
}


def carregar_dados_brutos(caminho: Path = CAMINHO_DADOS_BRUTOS) -> pd.DataFrame:
    """
    Lê a base original, sem nenhuma alteração.

    Args:
        caminho: Caminho do arquivo CSV original.

    Returns:
        DataFrame com os 2.500 pedidos.
    """
    return pd.read_csv(caminho)


def carregar_dados_tratados(caminho: Path = CAMINHO_DADOS_TRATADOS) -> pd.DataFrame:
    """
    Lê a base tratada pelo notebook 02 e restaura a ordem das faixas.

    Args:
        caminho: Caminho do CSV gerado pelo notebook 02.

    Returns:
        DataFrame tratado, com as colunas de faixa como categorias ordenadas.
    """
    dados = pd.read_csv(caminho, dtype={"faixa_contatos": str, "faixa_reclamacoes": str})
    for coluna, ordem in ORDEM_DAS_FAIXAS.items():
        dados[coluna] = pd.Categorical(dados[coluna], categories=ordem, ordered=True)
    return dados


def classificar_nps(notas: pd.Series) -> pd.Series:
    """
    Classifica cada nota (0 a 10) em Detrator, Neutro ou Promotor.

    Args:
        notas: Série com as notas NPS.

    Returns:
        Série categórica com a categoria de cada nota.
    """
    # right=False: o intervalo inclui o limite inferior (ex.: nota 7.0 já é Neutro)
    return pd.cut(
        notas,
        bins=[-np.inf, LIMITE_DETRATOR, LIMITE_PROMOTOR, np.inf],
        labels=CATEGORIAS_NPS,
        right=False,
    )


def calcular_nps(notas: pd.Series) -> float:
    """
    Calcula o índice NPS: % de promotores menos % de detratores.

    Args:
        notas: Série com as notas NPS.

    Returns:
        NPS em pontos, de -100 a +100.
    """
    pct_promotores = (notas >= LIMITE_PROMOTOR).mean() * 100
    pct_detratores = (notas < LIMITE_DETRATOR).mean() * 100
    return pct_promotores - pct_detratores


def resumir_nps_por_grupo(dados: pd.DataFrame, coluna_grupo: str) -> pd.DataFrame:
    """
    Resume a satisfação de cada grupo na linguagem do negócio.

    Args:
        dados: DataFrame com a coluna nps_score.
        coluna_grupo: Coluna usada para formar os grupos (ex.: faixa_atraso).

    Returns:
        Tabela com pedidos, nota média, % de detratores, % de promotores e NPS.
    """
    grupos = dados.groupby(coluna_grupo, observed=True)["nps_score"]
    resumo = pd.DataFrame(
        {
            "pedidos": grupos.size(),
            "nota_media": grupos.mean(),
            "pct_detratores": grupos.apply(lambda notas: (notas < LIMITE_DETRATOR).mean() * 100),
            "pct_promotores": grupos.apply(lambda notas: (notas >= LIMITE_PROMOTOR).mean() * 100),
            "nps": grupos.apply(calcular_nps),
        }
    )
    return resumo.round(1)


def intervalo_confianca_nps_bootstrap(notas: pd.Series, n_reamostragens: int = 5000, confianca: float = 0.95) -> tuple:
    """
    Intervalo de confiança do NPS por bootstrap (Aula 1 de Estatística).

    O NPS não segue distribuição normal, por isso usamos o bootstrap:
    sorteamos novas amostras COM reposição, calculamos o NPS de cada uma
    e pegamos os percentis da distribuição obtida.

    Args:
        notas: Série com as notas NPS.
        n_reamostragens: Quantidade de amostras sorteadas.
        confianca: Nível de confiança (0.95 = 95%).

    Returns:
        Tupla (limite_inferior, limite_superior) do NPS.
    """
    gerador = np.random.default_rng(SEMENTE_ALEATORIA)
    valores = notas.to_numpy()
    nps_reamostrados = [
        calcular_nps(pd.Series(gerador.choice(valores, size=len(valores), replace=True)))
        for _ in range(n_reamostragens)
    ]
    alfa = (1 - confianca) / 2
    return np.percentile(nps_reamostrados, 100 * alfa), np.percentile(nps_reamostrados, 100 * (1 - alfa))
