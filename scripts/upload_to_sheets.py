#!/usr/bin/env python3
"""
Upload opcional da planilha de acompanhamento para o Google Sheets.

Pré-requisitos:
  1. pip install gspread google-auth
  2. Criar projeto no Google Cloud Console
  3. Ativar Google Sheets API + Google Drive API
  4. Criar Service Account e baixar credentials.json
  5. Compartilhar a planilha com o e-mail da service account

Uso:
  python scripts/upload_to_sheets.py --credentials credentials.json --sheet-id SEU_ID
  python scripts/upload_to_sheets.py --credentials credentials.json --create "Méliuz AB Tests"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print(
        "Dependências ausentes. Instale com:\n"
        "  pip install gspread google-auth",
        file=sys.stderr,
    )
    raise SystemExit(1)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TRACKING_PATH = Path("tracking_sheet.csv")


def upload(credentials_path: Path, sheet_id: str | None, create_title: str | None) -> str:
    if not TRACKING_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {TRACKING_PATH}. Rode run_all.sh antes.")

    creds = Credentials.from_service_account_file(str(credentials_path), scopes=SCOPES)
    client = gspread.authorize(creds)
    df = pd.read_csv(TRACKING_PATH)

    if create_title:
        spreadsheet = client.create(create_title)
        worksheet = spreadsheet.sheet1
        spreadsheet.share("", perm_type="anyone", role="reader")
        url = spreadsheet.url
    elif sheet_id:
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1
        url = spreadsheet.url
    else:
        raise ValueError("Informe --sheet-id ou --create")

    worksheet.clear()
    worksheet.update([df.columns.tolist()] + df.values.tolist())
    return url


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload tracking_sheet.csv para Google Sheets")
    parser.add_argument("--credentials", type=Path, required=True, help="credentials.json da Service Account")
    parser.add_argument("--sheet-id", help="ID da planilha existente")
    parser.add_argument("--create", help="Criar nova planilha com este título")
    args = parser.parse_args()

    url = upload(args.credentials, args.sheet_id, args.create)
    print(f"Planilha atualizada: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
