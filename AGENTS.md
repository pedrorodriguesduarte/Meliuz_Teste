# Instruções para Agentes de IA — Méliuz AB Analyzer

Você está no projeto de análise automatizada de testes A/B de cashback do Méliuz.

## Sua missão

Quando o usuário pedir para analisar um teste A/B, você deve:

1. **Identificar** o arquivo CSV indicado
2. **Garantir** que o ambiente está pronto (venv + dependências)
3. **Executar** o script de análise
4. **Ler** o relatório gerado
5. **Apresentar** decisão, justificativa e alertas ao usuário

## Comandos

### Setup (só na primeira vez)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Analisar um teste

```bash
source .venv/bin/activate
python analyze_ab_test.py <caminho_do_csv>
```

### Analisar todos os exemplos

```bash
./run_all.sh
```

## Regras obrigatórias

- **NUNCA** altere `analyze_ab_test.py` para processar um dataset diferente
- **NUNCA** edite os CSVs de entrada
- **SEMPRE** use o script — não faça a análise "na mão" sem executá-lo
- A planilha `tracking_sheet.csv` é atualizada automaticamente
- Para testes novos: coloque o CSV na pasta e passe o caminho como argumento

## O que apresentar ao usuário

Após rodar, responda com:

1. **Decisão:** qual variante escalar para 100% do tráfego
2. **Por quê:** receita líquida, margem, trade-offs de volume
3. **Confiança:** nível estatístico (alta/média)
4. **Alertas:** problemas de qualidade nos dados (SRM, outliers, etc.)
5. **Onde está o relatório:** caminho do arquivo em `reports/`

## Pergunta central

> Dado esse teste A/B, qual variante de cashback devemos escalar para 100% do tráfego?

**Critério:** receita líquida (comissão − cashback) é a métrica primária.

## Schema do CSV

| Coluna | Descrição |
|---|---|
| Data | YYYY-MM-DD |
| Grupos de usuários | Variante (Grupo 1, Grupo 2, ...) |
| Parceiro | Nome do parceiro |
| compradores | Usuários únicos que compraram |
| comissão | R$ pago pelo parceiro ao Méliuz |
| cashback | R$ distribuído aos usuários |
| vendas totais | GMV em R$ |

## Exemplos de prompts do usuário

- "Analise o dataset_01_parceiroA.csv"
- "Qual variante escalar no teste do parceiro B?"
- "Rode todos os testes e me dê um resumo"
- "Analise o arquivo data/novo_teste.csv"
