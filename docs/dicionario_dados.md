# Dicionário de dados

Base: `data/raw/desafio_nps_fase_1.csv` · 2.500 linhas (um pedido por cliente) · 19 colunas · sem nulos.

| Coluna | Descrição | Tipo | Faixa observada | Momento | Uso no modelo |
|---|---|---|---|---|---|
| `customer_id` | Identificador único do cliente | inteiro | 1 – 2.500 | — | Não (ID) |
| `order_id` | Identificador único do pedido | inteiro | 50.001 – 52.500 | — | Não (ID) |
| `customer_age` | Idade do cliente | inteiro | 18 – 69 | Cadastro | Sim |
| `customer_region` | Região geográfica | texto | 5 regiões, ~20% cada | Cadastro | Sim (one-hot) |
| `customer_tenure_months` | Tempo de relacionamento com a empresa (meses) | inteiro | 1 – 119 | Cadastro | Sim |
| `order_value` | Valor total do pedido (R$) | decimal | 7,76 – 1.983,81 | Compra | Sim |
| `items_quantity` | Quantidade de itens | inteiro | 1 – 6 | Compra | Sim |
| `discount_value` | Valor de desconto (R$) | decimal | 0,02 – 230,33 | Compra | Sim |
| `payment_installments` | Número de parcelas | inteiro | 1 – 11 | Compra | Sim |
| `delivery_time_days` | Tempo total de entrega (dias) | inteiro | 2 – 14 | Entrega | Sim |
| `delivery_delay_days` | Dias de atraso na entrega | inteiro | 0 – 8 | Entrega | Sim |
| `freight_value` | Valor do frete (R$) | decimal | 2,62 – 76,13 | Compra | Sim |
| `delivery_attempts` | Número de tentativas de entrega | inteiro | 1 – 3 | Entrega | Sim |
| `customer_service_contacts` | Contatos do cliente com o atendimento | inteiro | 0 – 7 | Pós-entrega | Sim (valor acumulado até o momento) |
| `resolution_time_days` | Tempo para resolução de problemas (dias) | inteiro | 0 – 11 | Pós-entrega | Sim (valor acumulado até o momento) |
| `complaints_count` | Número de reclamações registradas | inteiro | 0 – 11 | Pós-entrega | Sim (valor acumulado até o momento) |
| `repeat_purchase_30d` | Recompra em até 30 dias (0/1) | binário | 9% = 1 | **30 dias após o pedido** | **Não — vazamento** |
| `csat_internal_score` | Score interno de satisfação | decimal | 0 – 10 | **Junto/após a pesquisa** | **Não — vazamento** |
| `nps_score` | Nota NPS (0 a 10), coletada após a experiência | decimal | 0 – 10 | Fim da jornada | **Target** |

## Variáveis derivadas (notebook 02)

| Coluna | Regra |
|---|---|
| `nps_category` | Detrator (< 7), Neutro (7 a < 9), Promotor (≥ 9) |
| `is_detractor` | 1 se `nps_category` = Detrator |
| `is_on_time` | 1 se `delivery_delay_days` = 0 |
| `delay_band` | No prazo · 1 dia · 2 dias · 3 dias · 4+ dias |
| `complaints_band` | 0-1 · 2 · 3 · 4 · 5 · 6+ |
| `contacts_band` | 0 · 1 · 2 · 3 · 4+ |
| `resolution_band` | Até 2 dias · 3-5 · 6-8 · 9+ |
| `age_band`, `tenure_band`, `order_value_band` | Faixas de perfil para a EDA |
| `flag_atraso_inconsistente` | 1 se atraso > tempo total de entrega |
| `flag_desconto_inconsistente` | 1 se desconto > valor do pedido |

## Observações de qualidade

| Achado | Linhas | Hipótese | Recomendação |
|---|---|---|---|
| Atraso maior que o tempo total de entrega | 121 (4,8%) | `delivery_time_days` pode ser o prazo *prometido*, não o realizado | Documentar a definição oficial com Logística |
| Desconto maior que o valor do pedido | 35 (1,4%) | `order_value` pode ser o valor líquido | Documentar a definição com Financeiro |
| Tempo de resolução > 0 sem contato com o SAC | 511 (20,4%) | Problemas tratados por outros canais | Registrar o canal de origem da reclamação |
| Reclamações sem contato com o SAC | 531 (21,2%) | Reclamações via marketplace/redes sociais | Idem |
| Notas NPS com casas decimais | todas | Possível média de várias respostas ou escala transformada | Confirmar a forma de coleta |
