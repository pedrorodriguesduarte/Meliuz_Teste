# Analisador de Testes A/B de Cashback — Méliuz Growth

Solução reutilizável para o teste técnico de **Estágio de Growth AI-Native** do Méliuz.

Responde a pergunta central de todo teste:

> **Dado esse teste A/B, qual variante de cashback devemos escalar para 100% do tráfego?**

---

## Índice

1. [Visão geral](#visão-geral)
2. [Arquitetura da solução](#arquitetura-da-solução)
3. [Pré-requisitos](#pré-requisitos)
4. [Instalação passo a passo](#instalação-passo-a-passo)
5. [Como rodar](#como-rodar)
6. [Uso com IA (Cursor / Claude Code)](#uso-com-ia-cursor--claude-code)
7. [O que a solução entrega](#o-que-a-solução-entrega)
8. [Critério de decisão](#critério-de-decisão)
9. [Resultados dos 3 testes](#resultados-dos-3-testes)
10. [Planilha de acompanhamento](#planilha-de-acompanhamento)
11. [Como entregar o teste técnico](#como-entregar-o-teste-técnico)
12. [Estrutura do projeto](#estrutura-do-projeto)
13. [Troubleshooting](#troubleshooting)

---

## Visão geral

O time de Growth do Méliuz roda dezenas de testes A/B por mês. Hoje cada análise leva 2–4 horas e depende de quem está olhando. Esta solução automatiza o processo:

- **Uma pessoa** abre Cursor, Claude Code ou outro agente de IA
- **Indica o arquivo** do dataset em linguagem natural
- **Recebe** relatório completo + decisão acionável + registro na planilha

O mesmo script processa qualquer teste novo — **sem alterar código**, apenas passando o caminho do CSV.

---

## Arquitetura da solução

```
┌─────────────────────────────────────────────────────────────┐
│  Usuário (Growth)                                           │
│  "Analise o teste dataset_02_parceiroB.csv"                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENTS.md — instruções para o agente de IA                 │
│  (quando rodar, o que apresentar, regras)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  analyze_ab_test.py                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Validação   │→ │ Métricas +   │→ │ Decisão +          │  │
│  │ e parsing   │  │ Estatística  │  │ Relatório + Sheet  │  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
     reports/relatorio_*.md     tracking_sheet.csv
     (relatório p/ gestor)      (histórico de testes)
```

**Por que essa arquitetura?**

| Camada | Função |
|---|---|
| `AGENTS.md` | Permite acionar via linguagem natural em qualquer ferramenta de IA |
| `analyze_ab_test.py` | Lógica determinística, testável e independente de IA |
| `reports/` | Saída apresentável para gestores |
| `tracking_sheet.csv` | Histórico centralizado de todos os testes rodados |

A IA **orquestra**; o script **decide** com regras fixas e reproduzíveis.

---

## Pré-requisitos

- **Python 3.10+** (testado com 3.13)
- **macOS, Linux ou Windows** com terminal
- **Git** (para publicar no GitHub)
- **Conta Google** (opcional, para planilha no Sheets)

---

## Instalação passo a passo

### 1. Clone ou baixe o repositório

```bash
git clone https://github.com/SEU_USUARIO/meliuz-ab-analyzer.git
cd meliuz-ab-analyzer
```

### 2. Crie o ambiente virtual

```bash
python3 -m venv .venv
```

### 3. Ative o ambiente

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

Você deve ver `(venv)` ou `(.venv)` no início do prompt do terminal.

---

## Como rodar

### Analisar um teste específico

```bash
python analyze_ab_test.py dataset_01_parceiroA.csv
```

Substitua o nome do arquivo por qualquer CSV com o mesmo schema.

### Analisar os 3 testes de exemplo de uma vez

```bash
chmod +x run_all.sh
./run_all.sh
```

O script cria o ambiente (se necessário), roda os 3 datasets e gera tudo em `reports/` + `tracking_sheet.csv`.

### Opções avançadas

```bash
python analyze_ab_test.py dataset_02_parceiroB.csv \
  --output-dir reports \
  --tracking minha_planilha.csv
```

| Flag | Padrão | Descrição |
|---|---|---|
| `dataset` | (obrigatório) | Caminho para o CSV do teste |
| `--output-dir` | `reports/` | Pasta dos relatórios Markdown |
| `--tracking` | `tracking_sheet.csv` | Planilha de acompanhamento |

### Saída esperada no terminal

```
============================================================
  Teste Cashback — Parceiro A
============================================================
  Decisão: escalar Grupo 1 para 100% do tráfego
  Confiança: alta — melhor receita líquida e baseline de referência
  Alertas: 3

  Relatório: reports/relatorio_01_parceiroA.md
  Planilha:  tracking_sheet.csv
```

---

## Uso com IA (Cursor / Claude Code)

### Passo 1 — Abra o projeto no Cursor

Abra esta pasta como workspace. O arquivo `AGENTS.md` já contém as instruções que o agente segue automaticamente.

### Passo 2 — Peça em linguagem natural

Exemplos de prompts:

```
Analise o teste A/B do arquivo dataset_02_parceiroB.csv
```

```
Rode a análise do parceiro C e me explique a decisão
```

```
Tenho um teste novo em data/parceiroD_jan2026.csv — analise e registre na planilha
```

### Passo 3 — O agente executa

1. Ativa o `.venv`
2. Roda `python analyze_ab_test.py <arquivo>`
3. Lê o relatório gerado
4. Apresenta decisão, trade-offs e alertas de qualidade

**Regra importante:** o agente não deve alterar código para cada teste novo — o script já é parametrizado.

---

## O que a solução entrega

Para **cada** teste analisado:

| Entrega | Onde | Conteúdo |
|---|---|---|
| Relatório executivo | `reports/relatorio_*.md` | Métricas, testes estatísticos, alertas, decisão |
| Registro na planilha | `tracking_sheet.csv` | Nome, descrição, resultado, decisão, confiança |
| Decisão no terminal | stdout | Variante a escalar + nível de confiança |

### Schema do CSV de entrada

| Coluna | Tipo | Descrição |
|---|---|---|
| `Data` | YYYY-MM-DD | Data da observação |
| `Grupos de usuários` | string | Variante (Grupo 1, Grupo 2, ...) |
| `Parceiro` | string | Parceiro do teste |
| `compradores` | int | Usuários únicos que compraram no dia |
| `comissão` | string (R$) | Comissão paga pelo parceiro ao Méliuz |
| `cashback` | string (R$) | Cashback distribuído aos usuários |
| `vendas totais` | string (R$) | GMV (valor total das vendas) |

### Colunas da planilha de acompanhamento

| Coluna | Descrição |
|---|---|
| `data_analise` | Quando a análise foi rodada |
| `nome_teste` | Nome identificável do teste |
| `parceiro` | Parceiro analisado |
| `periodo` | Intervalo de datas do teste |
| `variantes` | Grupos comparados |
| `resultado` | Resumo do que aconteceu |
| `decisao` | Recomendação acionável |
| `variante_escalar` | Grupo vencedor |
| `confianca` | Nível de confiança estatística |
| `alertas` | Problemas detectados nos dados |

---

## Critério de decisão

A lógica prioriza o que o Méliuz **efetivamente retém**:

```
Receita líquida = comissão − cashback
```

| Prioridade | Métrica | Por quê |
|:---:|---|---|
| **1** | Receita líquida total | Valor que fica com o Méliuz |
| **2** | GMV | Desempate quando margens diferem < 3% |
| **3** | Volume (compradores) | Contexto — nunca sacrifica margem material |

**Validação estatística:** teste t pareado nas métricas diárias (p < 0,05 = significativo).

**Regra de segurança:** nunca escala variante com margem ≤ 0, exceto se todas forem ≤ 0.

### Alertas automáticos de qualidade

O script detecta e reporta:

- Valores nulos ou monetários inválidos
- Datas desalinhadas entre variantes
- Outliers de volume diário (método IQR)
- Possível desbalanceamento de tráfego (SRM)
- Cashback escalonado em degraus fixos
- Variantes com receita líquida negativa

---

## Resultados dos 3 testes

### Parceiro A → Escalar **Grupo 1**

| Variante | Cashback % | Receita líquida | GMV | Compradores |
|---|---:|---:|---:|---:|
| **Grupo 1** | 4,16% | **R$ 404.711** | R$ 5,6M | 9.633 |
| Grupo 2 | 5,77% | R$ 357.519 | R$ 6,4M | 10.814 |
| Grupo 3 | 7,42% | R$ 264.287 | R$ 6,8M | 11.410 |

**Leitura:** mais cashback gera +18% de compradores (Grupo 3), mas a receita líquida cai 35%. Grupo 1 retém 7,2% do GMV vs. 3,9% do Grupo 3.

Relatório completo: [`reports/relatorio_01_parceiroA.md`](reports/relatorio_01_parceiroA.md)

---

### Parceiro B → Escalar **Grupo 1**

| Variante | Cashback % | Receita líquida | GMV | Compradores |
|---|---:|---:|---:|---:|
| **Grupo 1** | 4,00% | **R$ 286.570** | R$ 4,1M | 7.990 |
| Grupo 2 | 6,00% | R$ 143.157 | R$ 2,9M | 5.452 |
| Grupo 3 | 9,00% | R$ 52.593 | R$ 2,6M | 5.029 |

**Leitura:** Grupo 1 vence em todas as métricas. Alerta de possível desbalanceamento de tráfego — Grupo 1 recebeu ~60% mais volume diário que os demais.

Relatório completo: [`reports/relatorio_02_parceiroB.md`](reports/relatorio_02_parceiroB.md)

---

### Parceiro C → Escalar **Grupo 1**

| Variante | Cashback % | Receita líquida | GMV | Compradores |
|---|---:|---:|---:|---:|
| **Grupo 1** | 5,00% | **R$ 34.769** | R$ 1,7M | 4.549 |
| Grupo 2 | 7,00% | R$ 0 | R$ 1,7M | 4.522 |

**Leitura:** Grupo 2 distribui 100% da comissão como cashback (margem zero) sem ganho de volume estatisticamente significativo (p = 0,91). Decisão clara.

Relatório completo: [`reports/relatorio_03_parceiroC.md`](reports/relatorio_03_parceiroC.md)

---

## Planilha de acompanhamento

### Opção A — CSV (mínimo aceito, já incluído)

O arquivo [`tracking_sheet.csv`](tracking_sheet.csv) já contém os 3 testes analisados.

### Opção B — Google Sheets (diferencial)

#### Método rápido (manual, 2 minutos)

1. Acesse [sheets.google.com](https://sheets.google.com)
2. **Arquivo → Importar → Upload** → selecione `tracking_sheet.csv`
3. **Compartilhar** → "Qualquer pessoa com o link" → **Leitor**
4. Copie o link para incluir na entrega

#### Método automatizado (com Service Account)

```bash
pip install gspread google-auth

python scripts/upload_to_sheets.py \
  --credentials credentials.json \
  --create "Méliuz — Testes A/B Cashback"
```

O script cria a planilha, preenche com os dados e configura acesso público de leitura.

**Configurar Service Account:**

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um projeto → ative **Google Sheets API** e **Google Drive API**
3. **IAM → Service Accounts → Criar** → baixe o JSON como `credentials.json`
4. Coloque `credentials.json` na raiz do projeto (já está no `.gitignore`)

---

## Como entregar o teste técnico

Checklist completo do que o Méliuz pede:

- [ ] Repositório **público** no GitHub com a solução
- [ ] `README.md` com instruções de como rodar
- [ ] Relatórios dos 3 testes em `reports/`
- [ ] Planilha preenchida (`tracking_sheet.csv` ou link do Google Sheets)
- [ ] Testar repo em janela anônima antes de enviar

### Publicar no GitHub

```bash
# Na pasta do projeto
git init
git add .
git commit -m "Solução completa: analisador de testes A/B de cashback Méliuz"

# Crie o repo no GitHub (site ou CLI)
gh repo create meliuz-ab-analyzer --public --source=. --push
```

### Enviar por email (Gupy)

Inclua no email:

1. **Link do repositório GitHub** (público)
2. **Link da planilha** (Google Sheets ou indique que está no repo como `tracking_sheet.csv`)
3. Breve resumo: os 3 testes recomendam escalar **Grupo 1** em todos os parceiros

---

## Estrutura do projeto

```
meliuz-ab-analyzer/
├── analyze_ab_test.py          # Script principal — analisa qualquer CSV
├── AGENTS.md                   # Instruções para agentes de IA
├── README.md                   # Este arquivo
├── requirements.txt            # Dependências Python
├── run_all.sh                  # Roda os 3 datasets de exemplo
├── tracking_sheet.csv          # Planilha de acompanhamento (gerada)
├── dataset_01_parceiroA.csv    # Dataset de exemplo — Parceiro A
├── dataset_02_parceiroB.csv    # Dataset de exemplo — Parceiro B
├── dataset_03_parceiroC.csv    # Dataset de exemplo — Parceiro C
├── reports/
│   ├── relatorio_01_parceiroA.md
│   ├── relatorio_02_parceiroB.md
│   └── relatorio_03_parceiroC.md
└── scripts/
    └── upload_to_sheets.py     # Upload opcional para Google Sheets
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'pandas'`

O ambiente virtual não está ativo ou as dependências não foram instaladas:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### `Erro: arquivo não encontrado`

Verifique se o caminho do CSV está correto e se você está na pasta do projeto:

```bash
ls *.csv
python analyze_ab_test.py dataset_01_parceiroA.csv
```

### `Colunas ausentes no dataset`

O CSV precisa ter exatamente as colunas do schema (ver seção [Schema do CSV de entrada](#schema-do-csv-de-entrada)). Não renomeie colunas.

### `externally-managed-environment` (pip)

Use ambiente virtual — não instale pacotes no Python do sistema:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Planilha duplicando linhas

Cada execução **adiciona** uma linha. Para recomeçar do zero:

```bash
rm tracking_sheet.csv
./run_all.sh
```

---

## Licença

Projeto criado para o processo seletivo do Méliuz. Uso livre para avaliação.
