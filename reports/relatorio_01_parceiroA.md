# Relatorio A/B - Cashback Parceiro A

| Campo | Valor |
|---|---|
| Parceiro | Parceiro A |
| Periodo | 2011-01-01 a 2011-04-02 |
| Arquivo | `dataset_01_parceiroA.csv` |
| Gerado em | 11/06/2026 20:41 |

## Recomendacao

| | |
|---|---|
| **Variante a escalar** | **Grupo 1** |
| **Decisao** | Escalar Grupo 1 para 100% do trafego. |
| **Receita liquida** | R$ 404.711 |
| **Margem liquida** | 7.22% |
| **Cashback efetivo** | 4.16% |
| **Confianca** | Alta |

## Resumo executivo

Escalar Grupo 1 para 100% do trafego. Receita liquida total: R$ 404.711 (7.22% do GMV). Cashback efetivo: 4.16% do GMV. Nota: Grupo 3 gera +18.4% de compradores e R$ 6.785.856 de GMV, mas com R$ 264.287 de receita liquida (R$ -140.424 a menos que Grupo 1). Priorizar volume so faz sentido se a estrategia for crescimento com margem sacrificada.

## Métricas por variante

| Variante | Dias | Compradores | GMV | Comissão | Cashback | Receita líquida | Cashback % | Margem líquida % | Ticket médio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 92 | 9,633 | R$ 5.605.173 | R$ 638.135 | R$ 233.424 | **R$ 404.711** | 4.16% | 7.22% | R$ 586 |
| Grupo 2 | 92 | 10,814 | R$ 6.423.096 | R$ 728.178 | R$ 370.659 | **R$ 357.519** | 5.77% | 5.57% | R$ 595 |
| Grupo 3 | 92 | 11,410 | R$ 6.785.856 | R$ 767.887 | R$ 503.600 | **R$ 264.287** | 7.42% | 3.89% | R$ 594 |

## Testes estatísticos (pareado por dia)

| Comparação | Métrica | Lift | p-value | Significativo? |
|---|---|---:|---:|:---:|
| Grupo 2 vs Grupo 1 | receita liquida diaria | -11.7% | 0.0000 | Sim |
| Grupo 3 vs Grupo 1 | receita liquida diaria | -34.7% | 0.0000 | Sim |
| Grupo 2 vs Grupo 1 | compradores diarios | +12.3% | 0.0000 | Sim |
| Grupo 3 vs Grupo 1 | compradores diarios | +18.4% | 0.0000 | Sim |
| Grupo 2 vs Grupo 1 | GMV diario | +14.6% | 0.0000 | Sim |
| Grupo 3 vs Grupo 1 | GMV diario | +21.1% | 0.0000 | Sim |

## Qualidade dos dados

- ⚠️ Outliers de volume em Grupo 1: 6 dia(s) (pico em 2011-01-13 com 289 compradores).
- ⚠️ Outliers de volume em Grupo 2: 4 dia(s) (pico em 2011-01-13 com 354 compradores).
- ⚠️ Outliers de volume em Grupo 3: 3 dia(s) (pico em 2011-01-13 com 353 compradores).

## Metodologia

A receita líquida (comissão − cashback) é a métrica primária de decisão — representa o valor que o Méliuz retém em cada venda. Testes t pareados comparam métricas diárias entre variantes no mesmo período. Lifts de volume são considerados como contexto, mas não substituem margem quando a diferença de receita líquida é material.
