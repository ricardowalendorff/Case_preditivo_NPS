# Case Preditivo de NPS — Tech Challenge Fase 1

**Pós Tech · IA para Cientistas de Dados (FIAP)** · Autor: Ricardo Walendorff

> **Quais fatores operacionais realmente influenciam a satisfação do cliente e como a empresa pode agir de forma proativa para melhorar a experiência antes mesmo da aplicação da pesquisa de NPS?**

---

## 1. Objetivo do projeto

Uma empresa de e-commerce em forte crescimento observa grande variação no NPS entre clientes com indicadores operacionais aparentemente parecidos. Hoje o NPS só é coletado **depois** do fim da jornada de compra, quando já não há como evitar a experiência ruim.

Este projeto:

1. **Entende o problema de negócio** e define a variável alvo de forma crítica (riscos de uso e vazamento de informação);
2. **Explora os dados** com foco em negócio, para identificar o que gera detratores e onde estão os "pontos de ruptura" da experiência;
3. **Propõe e implementa um modelo preditivo** que estima a nota NPS de cada pedido com dados disponíveis *antes* da pesquisa, convertendo-a em faixas de risco acionáveis;
4. **Traduz os achados em recomendações** para logística, atendimento, produto e estratégia, em uma apresentação para público não técnico.

## 2. Principais resultados

| | |
|---|---|
| **Situação atual** | NPS de **−80**: 84% dos clientes são detratores, 4% promotores |
| **Fator nº 1** | **Atraso na entrega**: cada dia de atraso custa ~1 ponto na nota |
| **Pontos de ruptura** | **1º dia de atraso** (74% de detratores) e **2ª reclamação** (65%); com **3+ dias de atraso**, ~97-100% viram detratores |
| **Insight-chave** | O cliente não se incomoda com o prazo longo — se incomoda com a **promessa quebrada**. Tempo total de entrega não afeta a nota; atraso sobre o prometido sim |
| **O que não importa** | Frete, valor do pedido, desconto, parcelamento, tentativas de entrega, região, idade e tempo de casa praticamente não mudam a nota |
| **Modelo** | Regressão Linear com 14 variáveis operacionais: erro médio de **1,4 ponto** (baseline 2,1), AUC **0,87** para identificar detratores |
| **Faixas de risco** | Na faixa de *risco alto*, **100%** viraram detratores; na de *risco baixo*, 32% (e 30% de promotores) |
| **Potencial** | Simulação: atraso ≤ 1 dia + resolução em 1 contato e ≤ 2 dias → **+25 pontos de NPS** |

## 3. Base de dados

Arquivo: [`data/raw/desafio_nps_fase_1.csv`](data/raw/desafio_nps_fase_1.csv) — **2.500 pedidos**, um por cliente, 19 colunas, sem valores ausentes ou duplicados.

| Grupo | Colunas | Momento na jornada |
|---|---|---|
| Identificadores | `customer_id`, `order_id` | — |
| Cliente | `customer_age`, `customer_region`, `customer_tenure_months` | Antes da compra |
| Pedido | `order_value`, `items_quantity`, `discount_value`, `payment_installments` | Compra |
| Logística | `delivery_time_days`, `delivery_delay_days`, `freight_value`, `delivery_attempts` | Entrega |
| Atendimento | `customer_service_contacts`, `resolution_time_days`, `complaints_count` | Pós-entrega |
| Pós-experiência ⚠️ | `csat_internal_score`, `repeat_purchase_30d` | Junto/depois da pesquisa |
| **Target** | `nps_score` (0 a 10, com decimais) | Fim da jornada |

O dicionário completo, com as definições e as observações de qualidade, está em [`docs/dicionario_dados.md`](docs/dicionario_dados.md).

⚠️ As variáveis de **pós-experiência** são medidas de resultado coletadas junto ou depois do NPS. Elas **não entram no modelo preditivo** para evitar vazamento de informação (*data leakage*) — o notebook 04 demonstra o efeito.

## 4. Metodologia

O projeto segue o **CRISP-DM**:

```
Entendimento do negócio → Entendimento dos dados → Preparação → Modelagem → Avaliação → Uso no negócio
        (01)                    (02, 03)              (02)          (04)         (04)        (apresentação)
```

| Etapa | Notebook | O que contém |
|---|---|---|
| Negócio e target | [`01_entendimento_negocio_e_target.ipynb`](notebooks/01_entendimento_negocio_e_target.ipynb) | Problema, importância do NPS, áreas beneficiadas, impacto em recompra/boca a boca/market share, indicadores de mercado, definição e riscos da target |
| Preparação | [`02_preparacao_dados.ipynb`](notebooks/02_preparacao_dados.ipynb) | Tipos, completude, duplicidades, regras de consistência, outliers, criação de faixas e da categoria NPS; salva `data/processed/nps_tratado.csv` |
| EDA | [`03_analise_exploratoria.ipynb`](notebooks/03_analise_exploratoria.ipynb) | Fatores críticos, causas de detração, pontos de ruptura, perfil de cliente, fatores sem impacto — linguagem para gestor(a) de operações |
| Modelo | [`04_modelo_preditivo.ipynb`](notebooks/04_modelo_preditivo.ipynb) | Estratégia, separação treino/teste, comparação de modelos, teste de vazamento, avaliação, faixas de risco, interpretação, simulação de cenários, uso prático e limitações |

**Decisões principais**

- **Categoria NPS com notas decimais:** detrator < 7; neutro 7 a < 9; promotor ≥ 9;
- **Inconsistências** (ex.: atraso maior que o tempo de entrega em 5% dos pedidos) foram **sinalizadas, não removidas**, e viraram recomendação de governança de dados;
- **Modelo:** regressão da nota (0-10) como abordagem principal + classificação detrator/não detrator como comparação. Regressão Linear, Random Forest e Gradient Boosting empataram; foi escolhida a **Regressão Linear** por ser explicável e estável;
- **Avaliação:** treino/teste 80/20 estratificado + validação cruzada de 5 dobras; métricas MAE, R², AUC, precisão/*recall* e taxa real de detratores por faixa de risco.

## 5. Estrutura do repositório

```
Case_preditivo_NPS/
├── data/
│   ├── raw/                  # base original (não alterada)
│   └── processed/            # base tratada gerada pelo notebook 02
├── docs/
│   ├── dicionario_dados.md   # dicionário de dados + observações de qualidade
│   └── roteiro_video.md      # roteiro do vídeo executivo (até 5 min)
├── models/
│   └── nps_regressor.joblib  # pipeline treinado (pré-processamento + modelo)
├── notebooks/                # 01 → 04, executar em ordem
├── reports/
│   ├── figures/              # gráficos gerados pelos notebooks
│   ├── apresentacao_nps_preditivo.pptx  # storytelling gerencial (editável)
│   └── apresentacao_nps_preditivo.pdf   # mesma apresentação em PDF
├── src/
│   ├── nps_utils.py          # caminhos, regras do NPS, grupos de variáveis
│   ├── viz.py                # padrão visual dos gráficos
│   ├── modeling.py           # pipeline do modelo e faixas de risco
│   └── predict.py            # script para pontuar novos pedidos
├── requirements.txt
└── README.md
```

## 6. Como reproduzir

Pré-requisito: Python 3.11+ (desenvolvido em 3.13).

```bash
git clone https://github.com/ricardowalendorff/Case_preditivo_NPS.git
cd Case_preditivo_NPS
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Execute os notebooks **em ordem** (o 02 gera a base tratada usada pelo 03 e 04; o 04 gera o modelo):

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/0*.ipynb
```

Ou abra no Jupyter (`jupyter lab`) e rode célula a célula. Todos os resultados são determinísticos (`random_state = 42`).

Para pontuar pedidos com o modelo treinado (gera a lista priorizada por risco):

```bash
python -m src.predict --input data/raw/desafio_nps_fase_1.csv --output reports/pedidos_pontuados.csv
```

## 7. Limitações

- A análise mostra **associações**, não prova causalidade — as ações recomendadas devem ser validadas com testes controlados (grupo de controle);
- Base sem datas, canal, categoria de produto, transportadora ou texto das reclamações; separação treino/teste aleatória (em produção, usar separação temporal);
- O modelo explica ~51-57% da variação da nota: é um **sinal de alerta**, não uma previsão exata — e é melhor em detectar risco do que em identificar encantamento;
- Possível viés de resposta da pesquisa de NPS.

## 8. Apresentação e vídeo

- Slides para público não técnico: [`reports/apresentacao_nps_preditivo.pptx`](reports/apresentacao_nps_preditivo.pptx) (versão PDF: [`reports/apresentacao_nps_preditivo.pdf`](reports/apresentacao_nps_preditivo.pdf)); as notas do apresentador estão em cada slide
- Roteiro do vídeo executivo: [`docs/roteiro_video.md`](docs/roteiro_video.md)
