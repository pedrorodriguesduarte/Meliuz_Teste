# Checklist de Entrega — Teste Técnico Méliuz

Use este arquivo como guia final antes de enviar o email no Gupy.

## O que foi entregue neste repositório

| Item solicitado | Status | Onde encontrar |
|---|---|---|
| Solução reutilizável | ✅ | `analyze_ab_test.py` + `AGENTS.md` |
| README de como rodar | ✅ | `README.md` |
| Relatório Parceiro A | ✅ | `reports/relatorio_01_parceiroA.md` |
| Relatório Parceiro B | ✅ | `reports/relatorio_02_parceiroB.md` |
| Relatório Parceiro C | ✅ | `reports/relatorio_03_parceiroC.md` |
| Planilha de acompanhamento | ✅ | `tracking_sheet.csv` |
| Google Sheets (diferencial) | ⏳ | Importar CSV manualmente ou usar `scripts/upload_to_sheets.py` |

## Decisões finais

| Parceiro | Escalar | Motivo principal |
|---|---|---|
| A | **Grupo 1** | Maior receita líquida (R$ 404.711); Grupo 3 gera volume mas sacrifica 35% de margem |
| B | **Grupo 1** | Vence em receita, GMV e compradores; cashback de 4% é o nível ótimo |
| C | **Grupo 1** | Grupo 2 zera margem sem ganho de volume |

## Passos finais (você precisa fazer)

### 1. Publicar no GitHub

```bash
cd /caminho/para/o/projeto
git init
git add .
git commit -m "Solução completa: analisador de testes A/B de cashback Méliuz"
gh repo create meliuz-ab-analyzer --public --source=. --push
```

Ou crie o repositório manualmente em github.com e faça push.

### 2. Criar planilha no Google Sheets

1. Abra [sheets.google.com](https://sheets.google.com)
2. Importe `tracking_sheet.csv`
3. Compartilhe com "Qualquer pessoa com o link" (Leitor)
4. Copie o link

### 3. Testar em janela anônima

Abra o link do GitHub em aba anônima e confirme que está público.

### 4. Enviar email no Gupy

**Assunto sugerido:** Teste Técnico — Growth AI-Native — [Seu Nome]

**Corpo sugerido:**

```
Olá,

Segue minha entrega do teste técnico de Growth AI-Native:

📁 Repositório: [LINK DO GITHUB]
📊 Planilha de acompanhamento: [LINK DO GOOGLE SHEETS]

Resumo das decisões:
• Parceiro A → Escalar Grupo 1 (maior receita líquida, R$ 404.711)
• Parceiro B → Escalar Grupo 1 (vence em todas as métricas)
• Parceiro C → Escalar Grupo 1 (Grupo 2 zera margem sem ganho de volume)

Para rodar: clone o repo, ative o venv e execute ./run_all.sh

Att,
[Seu Nome]
```
