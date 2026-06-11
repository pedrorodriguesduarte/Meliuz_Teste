# Relatorio A/B - Cashback Parceiro C

| Campo | Valor |
|---|---|
| Parceiro | Parceiro C |
| Periodo | 2011-07-01 a 2011-08-14 |
| Arquivo | `dataset_03_parceiroC.csv` |
| Gerado em | 11/06/2026 20:41 |

## Recomendacao

| | |
|---|---|
| **Variante a escalar** | **Grupo 1** |
| **Decisao** | Escalar Grupo 1 para 100% do trafego. |
| **Receita liquida** | R$ 34.769 |
| **Margem liquida** | 2.00% |
| **Cashback efetivo** | 5.00% |
| **Confianca** | Alta |

## Resumo executivo

Escalar Grupo 1 para 100% do trafego. Receita liquida total: R$ 34.769 (2.00% do GMV). Cashback efetivo: 5.00% do GMV.

## Métricas por variante

| Variante | Dias | Compradores | GMV | Comissão | Cashback | Receita líquida | Cashback % | Margem líquida % | Ticket médio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 45 | 4,549 | R$ 1.738.460 | R$ 121.693 | R$ 86.924 | **R$ 34.769** | 5.00% | 2.00% | R$ 382 |
| Grupo 2 | 45 | 4,522 | R$ 1.685.235 | R$ 117.967 | R$ 117.967 | **R$ 0** | 7.00% | 0.00% | R$ 372 |

## Testes estatísticos (pareado por dia)

| Comparação | Métrica | Lift | p-value | Significativo? |
|---|---|---:|---:|:---:|
| Grupo 2 vs Grupo 1 | receita liquida diaria | -100.0% | 0.0000 | Sim |
| Grupo 2 vs Grupo 1 | compradores diarios | -0.6% | 0.9052 | Não |
| Grupo 2 vs Grupo 1 | GMV diario | -3.1% | 0.5803 | Não |

## Qualidade dos dados

- ⚠️ Cashback escalonado em degraus fixos (5.0%, 7.0%). Confirmar se as variantes representam níveis de cashback distintos.

## Metodologia

A receita líquida (comissão − cashback) é a métrica primária de decisão — representa o valor que o Méliuz retém em cada venda. Testes t pareados comparam métricas diárias entre variantes no mesmo período. Lifts de volume são considerados como contexto, mas não substituem margem quando a diferença de receita líquida é material.
