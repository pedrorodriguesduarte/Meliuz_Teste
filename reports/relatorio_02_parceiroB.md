# Teste Cashback — Parceiro B

**Parceiro:** Parceiro B  
**Período:** 2011-05-01 a 2011-06-30  
**Arquivo:** `dataset_02_parceiroB.csv`  
**Gerado em:** 2026-06-11 20:33

## Resumo executivo

**Decisão:** Escalar **Grupo 1** para 100% do tráfego. Receita líquida total: R$ 286,570 (7.00% do GMV). Cashback efetivo: 4.00% do GMV.

**Confiança:** média — possível desbalanceamento de tráfego nos dados

**Variante a escalar:** Grupo 1

## Métricas por variante

| Variante | Dias | Compradores | GMV | Comissão | Cashback | Receita líquida | Cashback % | Margem líquida % | Ticket médio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 61 | 7,990 | R$ 4.093.818 | R$ 450.321 | R$ 163.751 | **R$ 286.570** | 4.00% | 7.00% | R$ 511 |
| Grupo 2 | 61 | 5,452 | R$ 2.863.019 | R$ 314.935 | R$ 171.778 | **R$ 143.157** | 6.00% | 5.00% | R$ 526 |
| Grupo 3 | 61 | 5,029 | R$ 2.629.963 | R$ 289.290 | R$ 236.697 | **R$ 52.593** | 9.00% | 2.00% | R$ 524 |

## Testes estatísticos (pareado por dia)

| Comparação | Métrica | Lift | p-value | Significativo? |
|---|---|---:|---:|:---:|
| Grupo 2 vs Grupo 1 | receita líquida diária | -50.0% | 0.0000 | Sim |
| Grupo 3 vs Grupo 1 | receita líquida diária | -81.6% | 0.0000 | Sim |
| Grupo 2 vs Grupo 1 | compradores diários | -31.8% | 0.0000 | Sim |
| Grupo 3 vs Grupo 1 | compradores diários | -37.1% | 0.0000 | Sim |
| Grupo 2 vs Grupo 1 | GMV diário | -30.1% | 0.0000 | Sim |
| Grupo 3 vs Grupo 1 | GMV diário | -35.8% | 0.0000 | Sim |

## Qualidade dos dados

- ⚠️ Possível desbalanceamento de tráfego (SRM): média diária de compradores varia 159% entre a variante com mais e com menos tráfego. Interpretar lifts de volume com cautela.
- ⚠️ Outliers de volume em Grupo 1: 2 dia(s) (pico em 2011-05-15 com 396 compradores).
- ⚠️ Outliers de volume em Grupo 2: 2 dia(s) (pico em 2011-05-15 com 289 compradores).
- ⚠️ Outliers de volume em Grupo 3: 2 dia(s) (pico em 2011-05-22 com 245 compradores).

## Metodologia

A receita líquida (comissão − cashback) é a métrica primária de decisão — representa o valor que o Méliuz retém em cada venda. Testes t pareados comparam métricas diárias entre variantes no mesmo período. Lifts de volume são considerados como contexto, mas não substituem margem quando a diferença de receita líquida é material.
