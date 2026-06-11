#!/usr/bin/env bash
# Analisa os 3 datasets de exemplo e regenera relatórios + planilha.
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -d ".venv" ]]; then
  echo "Criando ambiente virtual..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

echo "Limpando planilha anterior..."
rm -f tracking_sheet.csv

for dataset in dataset_01_parceiroA.csv dataset_02_parceiroB.csv dataset_03_parceiroC.csv; do
  echo ""
  echo ">>> Analisando $dataset"
  python analyze_ab_test.py "$dataset"
done

echo ""
echo "Concluído!"
echo "  Relatórios: reports/"
echo "  Planilha:     tracking_sheet.csv"
