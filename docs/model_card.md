# Model Card: Modelo de NPS previsto

Documento-resumo do modelo, no formato de *Model Card* (referência das apostilas de Ambientes de Trabalho e de Definição da Target). Serve para que qualquer pessoa entenda o que o modelo faz, como foi avaliado e onde ele **não** deve ser usado.

## Identificação

| Item | Descrição |
|---|---|
| Nome | Modelo de NPS previsto |
| Versão | 1.0 (Tech Challenge Fase 1) |
| Arquivo | `models/modelo_nps.joblib` (gerado pelo notebook 04) |
| Tipo | Regressão linear múltipla (mínimos quadrados) |
| Autores | Ricardo Fritsch Walendorff e Chrystopher Alves |

## Objetivo

Estimar, **antes da pesquisa de NPS**, a nota (0 a 10) que o cliente de um pedido tende a dar, e convertê-la em uma faixa de risco para priorizar ações preventivas.

- **Unidade:** pedido;
- **Uso previsto:** priorizar a fila de ação dos times de Logística e Atendimento;
- **Usos não previstos:** decidir sobre crédito, preço ou qualquer tratamento pior para clientes "com risco de reclamar"; avaliar desempenho individual de funcionários.

## Dados

- **Treino:** 2.000 pedidos (80%), separados de forma estratificada pela categoria NPS;
- **Teste:** 500 pedidos (20%) nunca usados no treino;
- **Variáveis de entrada (17):** 12 numéricas operacionais (idade, tempo de casa, valor, itens, desconto, parcelas, tempo de entrega, atraso, frete, tentativas, contatos com o SAC, tempo de resolução, reclamações) e 4 colunas 0/1 de região (Centro-Oeste como referência);
- **Variáveis excluídas por vazamento:** `csat_internal_score` e `repeat_purchase_30d`.

## Desempenho (conjunto de teste)

| Métrica | Valor | Referência |
|---|---|---|
| MAE (erro absoluto médio) | 1,39 ponto | Baseline (média): 2,11 |
| RMSE | 1,78 ponto | |
| R² | 0,51 | Validação cruzada no treino: 0,57 |
| AUC para identificar detratores | 0,87 | |
| % de detratores reais na faixa "Risco alto" | 100% (175 pedidos) | Base: 84% |
| % de detratores reais na faixa "Risco baixo" | 32% (37 pedidos) | |

## Principais fatores (coeficientes)

| Fator | Efeito na nota |
|---|---|
| +1 dia de atraso | −0,94 |
| +1 reclamação | −0,37 |
| +1 contato com o SAC | −0,35 |
| +1 dia para resolver | −0,14 |

Contatos com o SAC e reclamações são correlacionados (0,75): seus efeitos devem ser lidos em conjunto.

## Faixas de risco

| Faixa | Nota prevista | Ação |
|---|---|---|
| Risco alto | < 4 | Contato humano imediato |
| Risco moderado | 4 a < 7 | Ações automáticas preventivas |
| Risco baixo | ≥ 7 | Fluxo padrão; convite para indicação |

## Limitações e cuidados

- Explica cerca de metade da variação da nota: é um alerta, não uma sentença;
- Mostra associações, não causas: validar ações com teste A/B antes de escalar;
- Base sem datas: separação treino/teste aleatória (em produção, usar separação temporal);
- Notas acima de ~8,5 são pouco previsíveis;
- Contatos, reclamações e tempo de resolução devem ser usados com o valor acumulado até o momento da previsão.

## Manutenção

- Comparar mensalmente nota prevista × nota real (MAE) e a % de detratores por faixa;
- Re-treinar se o MAE subir de forma consistente ou se a forma de aplicar a pesquisa mudar (target drift);
- Qualquer mudança na definição da target (ex.: limites de detrator) gera uma nova versão do modelo.
