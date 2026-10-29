# Case Preditivo de NPS: Tech Challenge Fase 1

**Pós Tech · IA para Cientistas de Dados (FIAP)** · Autores: Ricardo Fritsch Walendorff (RM378526) e Chrystopher Alves (RM377391)

> **Quais fatores operacionais realmente influenciam a satisfação do cliente e como a empresa pode agir de forma proativa para melhorar a experiência antes mesmo da aplicação da pesquisa de NPS?**

---

## 1. Objetivo do projeto

Uma empresa de e-commerce em forte crescimento observa grande variação no NPS entre clientes com indicadores operacionais aparentemente parecidos. Hoje o NPS só é coletado **depois** do fim da jornada de compra, quando já não há como evitar a experiência ruim.

Este projeto:

1. **Entende o problema de negócio** e define a variável alvo de forma crítica (riscos de uso e vazamento de informação);
2. **Explora os dados** com foco em negócio, para identificar o que gera detratores e onde estão os "pontos de ruptura" da experiência;
3. **Implementa um modelo preditivo** que estima a nota NPS de cada pedido com dados disponíveis *antes* da pesquisa, convertendo-a em faixas de risco acionáveis;
4. **Traduz os achados em recomendações** para logística, atendimento, produto e estratégia, em uma apresentação para público não técnico.

## 2. Principais resultados

| | |
|---|---|
| **Situação atual** | NPS de **−80** (IC 95%: −82 a −78): 84% dos clientes são detratores, 4% promotores |
| **Fator nº 1** | **Atraso na entrega**: cada dia de atraso custa ~1 ponto na nota |
| **Pontos de ruptura** | **1º dia de atraso** (74% de detratores) e **2ª reclamação** (65%); com **3+ dias de atraso**, ~97-100% viram detratores |
| **Insight-chave** | O cliente não se incomoda com o prazo longo, e sim com a **promessa quebrada**: o tempo total de entrega não afeta a nota; o atraso sobre o prometido, sim |
| **O que não importa** | Frete, valor do pedido, desconto, parcelamento, tentativas de entrega, região, idade e tempo de casa praticamente não mudam a nota |
| **Modelo** | Regressão Linear com 17 variáveis operacionais: erro médio de **1,4 ponto** (baseline: 2,1) e AUC de **0,87** para identificar detratores |
| **Faixas de risco** | Na faixa de *risco alto*, **100%** viraram detratores; na de *risco baixo*, 32% (e 30% de promotores) |
| **Potencial** | Simulação: atraso ≤ 1 dia + resolução com 1 contato e em até 2 dias → **+25 pontos de NPS** (a validar com teste A/B) |

## 3. Base de dados

Arquivo: [`data/raw/desafio_nps_fase_1.csv`](data/raw/desafio_nps_fase_1.csv), com **2.500 pedidos** (um por cliente) e 19 colunas, sem valores ausentes ou duplicados.

| Grupo | Colunas | Momento na jornada |
|---|---|---|
| Identificadores | `customer_id`, `order_id` | — |
| Cliente | `customer_age`, `customer_region`, `customer_tenure_months` | Antes da compra |
| Pedido | `order_value`, `items_quantity`, `discount_value`, `payment_installments` | Compra |
| Logística | `delivery_time_days`, `delivery_delay_days`, `freight_value`, `delivery_attempts` | Entrega |
| Atendimento | `customer_service_contacts`, `resolution_time_days`, `complaints_count` | Pós-entrega |
| Pós-pesquisa ⚠️ | `csat_internal_score`, `repeat_purchase_30d` | Junto ou depois da pesquisa |
| **Target** | `nps_score` (0 a 10, com decimais) | Fim da jornada |

O dicionário completo (tipos de variáveis, faixas observadas e observações de qualidade) está em [`docs/dicionario_dados.md`](docs/dicionario_dados.md).

⚠️ As variáveis de **pós-pesquisa** são medidas de resultado coletadas junto ou depois do NPS. Elas **não entram no modelo** para evitar vazamento de informação (*data leakage*); o notebook 04 demonstra o efeito.

## 4. Metodologia

O projeto segue o **CRISP-DM**:

```
Entendimento do negócio → Entendimento dos dados → Preparação → Modelagem → Avaliação → Implantação
        (01)                    (02, 03)              (02)          (04)         (04)        (04, apresentação)
```

| Etapa | Notebook | O que contém |
|---|---|---|
| Negócio e target | [`01_entendimento_negocio_e_target.ipynb`](notebooks/01_entendimento_negocio_e_target.ipynb) | Dor de negócio, tipo de problema (descritivo/preditivo/prescritivo), importância do NPS, áreas beneficiadas, impacto em recompra/boca a boca/market share, indicadores de mercado, **metas de negócio × metas analíticas**, hipóteses iniciais, definição e riscos da target |
| Preparação | [`02_preparacao_dados.ipynb`](notebooks/02_preparacao_dados.ipynb) | Estrutura e tipos de variáveis, completude, duplicidades, validade, consistência, outliers e criação de faixas; salva `data/processed/nps_tratado.csv` |
| EDA | [`03_analise_exploratoria.ipynb`](notebooks/03_analise_exploratoria.ipynb) | Intervalos de confiança (bootstrap e Wilson), matriz de correlação, Spearman, pontos de ruptura, testes de hipótese (Mann-Whitney, Kruskal-Wallis, qui-quadrado), perfil de cliente, registro de descobertas |
| Modelo | [`04_modelo_preditivo.ipynb`](notebooks/04_modelo_preditivo.ipynb) | Separação treino/teste, comparação de modelos, teste de vazamento, métricas (MAE, MSE, RMSE, R²), interpretação com `statsmodels`, faixas de risco, classificação (precisão, *recall*, F1, AUC), simulação de cenários, uso prático, proposta de teste A/B e limitações |

### Como as disciplinas da Fase 1 aparecem no projeto

| Disciplina | Onde foi aplicada |
|---|---|
| **Metodologia CRISP-DM e negócio** | Estrutura dos notebooks; dor → perguntas → hipóteses; fórmula da target *"[Unidade] irá [Ação] nos próximos [Período]"*; metas de negócio × analíticas; armadilhas da target (vazamento, proxy, viés); model card |
| **Análise exploratória de dados** | Diagnóstico de qualidade (`info`, `isnull`, `duplicated`, `describe`), tipos de variáveis, gráficos por tipo de pergunta (barras, histograma, boxplot, heatmap, dispersão, barras empilhadas), registro de descobertas, storytelling na apresentação |
| **Estatística essencial** | Intervalo de confiança do NPS (bootstrap) e da % de detratores (Wilson), correlação de Pearson e Spearman, testes de hipótese com H₀/H₁, regressão linear múltipla com `statsmodels`, MAE/MSE/RMSE/R², proposta de teste A/B |
| **Ambientes de trabalho** | Workflow híbrido (notebooks para explorar, `src/` para código reutilizável), estrutura de pastas no estilo *cookiecutter-data-science*, `requirements.txt` + `environment.yml` + `Dockerfile`, Black + Flake8 + pre-commit, docstrings, Git com branch e Pull Request |

**Decisões principais**

- **Categoria NPS com notas decimais:** detrator < 7; neutro 7 a < 9; promotor ≥ 9;
- **Inconsistências** (ex.: atraso maior que o tempo de entrega em 5% dos pedidos) foram **marcadas, não removidas**, e viraram recomendação de governança de dados;
- **Modelo:** regressão da nota (0-10) como abordagem principal e classificação detrator/não detrator como comparação. Foram comparados baseline, Regressão Linear, Árvore de Decisão e Random Forest; a **Regressão Linear** teve o menor erro e é a mais explicável;
- **Avaliação:** treino/teste 80/20 estratificado e validação cruzada de 5 dobras.

## 5. Estrutura do repositório

```
Case_preditivo_NPS/
├── data/
│   ├── raw/                     # base original (nunca alterada)
│   └── processed/               # base tratada, gerada pelo notebook 02
├── docs/
│   ├── dicionario_dados.md      # dicionário de dados e observações de qualidade
│   ├── model_card.md            # resumo do modelo: objetivo, métricas, limites
│   └── roteiro_video.md         # roteiro do vídeo executivo (até 5 min)
├── models/
│   └── modelo_nps.joblib        # modelo treinado (gerado pelo notebook 04)
├── notebooks/                   # 01 → 04, executar em ordem
├── reports/
│   ├── figures/                 # gráficos gerados pelos notebooks
│   ├── apresentacao_nps_preditivo.pptx  # apresentação gerencial (editável)
│   └── apresentacao_nps_preditivo.pdf   # mesma apresentação em PDF
├── src/
│   ├── funcoes_nps.py           # caminhos, regras do NPS, grupos de colunas, intervalo de confiança
│   ├── graficos.py              # cores e padrão visual
│   ├── modelo.py                # preparação das variáveis e faixas de risco
│   └── prever.py                # script que pontua pedidos novos
├── requirements.txt             # dependências (pip / venv)
├── environment.yml              # dependências (Conda)
├── Dockerfile                   # execução do projeto em container
├── .pre-commit-config.yaml      # Black + Flake8 antes de cada commit
├── pyproject.toml, .flake8      # configurações do Black e do Flake8
└── README.md
```

## 6. Como reproduzir

### Opção A: venv + pip

```bash
git clone https://github.com/ricardowalendorff/Case_preditivo_NPS.git
cd Case_preditivo_NPS
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Opção B: Conda

```bash
conda env create -f environment.yml
conda activate case-nps
```

### Executar a análise

Execute os notebooks **em ordem e do início ao fim** (o 02 gera a base tratada usada pelo 03 e pelo 04; o 04 gera o modelo). Rodar "do início ao fim" evita o problema de *estado oculto* dos notebooks:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/0*.ipynb
```

Ou abra no JupyterLab / VS Code e use **Restart Kernel and Run All**. Os resultados são determinísticos (`SEMENTE_ALEATORIA = 42`).

Para pontuar pedidos com o modelo treinado (gera a lista priorizada por risco):

```bash
python -m src.prever --entrada data/raw/desafio_nps_fase_1.csv --saida reports/pedidos_pontuados.csv
```

### Opção C: Docker

```bash
docker build -t case-nps .
docker run --rm case-nps
```

O container instala as dependências, executa os quatro notebooks em ordem e pontua os pedidos.

## 7. Qualidade de código e versionamento

- **Formatação e estilo:** `black src` formata o código e `flake8 src` verifica o padrão PEP 8;
- **Pre-commit:** após `pre-commit install`, Black e Flake8 rodam automaticamente antes de cada commit;
- **Git:** cada evolução é feita em uma branch própria e integrada à `main` por Pull Request.

## 8. Limitações

- A análise mostra **associações**, não prova causalidade: as ações recomendadas devem ser validadas com teste A/B (grupo de controle);
- Base sem datas, canal, categoria de produto, transportadora ou texto das reclamações; separação treino/teste aleatória (em produção, usar separação temporal);
- O modelo explica cerca de metade da variação da nota: é um **sinal de alerta**, não uma previsão exata, e é melhor em detectar risco do que em identificar encantamento;
- Possível viés de seleção: só quem respondeu à pesquisa está na base.

## 9. Apresentação e vídeo

- Slides para público não técnico: [`reports/apresentacao_nps_preditivo.pptx`](reports/apresentacao_nps_preditivo.pptx) (versão PDF: [`reports/apresentacao_nps_preditivo.pdf`](reports/apresentacao_nps_preditivo.pdf)); as notas do apresentador estão em cada slide;
- Roteiro do vídeo executivo: [`docs/roteiro_video.md`](docs/roteiro_video.md).
