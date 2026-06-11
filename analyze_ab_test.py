#!/usr/bin/env python3
"""
Analisador reutilizável de testes A/B de cashback — Méliuz Growth.

Uso:
    python analyze_ab_test.py dataset_01_parceiroA.csv
    python analyze_ab_test.py dataset_02_parceiroB.csv --output-dir reports
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Constantes e tipos
# ---------------------------------------------------------------------------

MONETARY_COLS = ("comissão", "cashback", "vendas totais")
REQUIRED_COLS = ("Data", "Grupos de usuários", "Parceiro", "compradores", *MONETARY_COLS)
TRACKING_COLUMNS = (
    "data_analise",
    "nome_teste",
    "parceiro",
    "periodo",
    "variantes",
    "resultado",
    "decisao",
    "variante_escalar",
    "confianca",
    "alertas",
)


@dataclass
class GroupMetrics:
    grupo: str
    dias: int
    compradores: int
    gmv: float
    comissao: float
    cashback: float
    net: float
    avg_daily_buyers: float
    avg_ticket: float
    cashback_pct: float
    net_pct: float


@dataclass
class PairwiseComparison:
    grupo_a: str
    grupo_b: str
    metric: str
    lift_pct: float
    p_value: float
    significant: bool


@dataclass
class AnalysisResult:
    file_path: str
    partner: str
    period_start: str
    period_end: str
    groups: list[GroupMetrics]
    comparisons: list[PairwiseComparison]
    data_issues: list[str]
    winner: str
    decision: str
    confidence: str
    test_name: str
    description: str


# ---------------------------------------------------------------------------
# Parsing e validação
# ---------------------------------------------------------------------------


def parse_brl(value: Any) -> float:
    """Converte valores monetários brasileiros (R$ 1.234,56) para float."""
    if pd.isna(value):
        raise ValueError(f"Valor monetário nulo: {value}")
    text = str(value).replace("R$", "").strip()
    text = text.replace(".", "").replace(",", ".")
    return float(text)


def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    missing = set(REQUIRED_COLS) - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes no dataset: {sorted(missing)}")

    for col in MONETARY_COLS:
        df[f"{col}_num"] = df[col].apply(parse_brl)

    df["net"] = df["comissão_num"] - df["cashback_num"]
    df["ticket"] = df["vendas totais_num"] / df["compradores"].replace(0, pd.NA)
    df["cashback_pct"] = df["cashback_num"] / df["vendas totais_num"] * 100
    df["net_pct"] = df["net"] / df["vendas totais_num"] * 100

    return df


def detect_data_issues(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []

    if df.isnull().any().any():
        issues.append("Existem valores nulos no dataset.")

    for col in ("comissão_num", "cashback_num", "vendas totais_num"):
        bad = (df[col] <= 0).sum()
        if bad:
            issues.append(f"{bad} registro(s) com {col} ≤ 0.")

    loss_days = (df["net"] < 0).sum()
    if loss_days:
        issues.append(f"{loss_days} dia(s) com receita líquida negativa (cashback > comissão).")

    groups = sorted(df["Grupos de usuários"].unique())
    date_sets = {g: set(df.loc[df["Grupos de usuários"] == g, "Data"]) for g in groups}
    common = set.intersection(*date_sets.values()) if date_sets else set()
    max_days = max(len(s) for s in date_sets.values()) if date_sets else 0
    if len(common) < max_days:
        issues.append(
            f"Cobertura de datas desalinhada entre variantes "
            f"({len(common)} dias em comum de {max_days})."
        )

    daily_buyers = df.groupby("Grupos de usuários")["compradores"].mean()
    if len(daily_buyers) > 1:
        ratio = daily_buyers.max() / daily_buyers.min()
        if ratio > 1.25:
            issues.append(
                "Possível desbalanceamento de tráfego (SRM): média diária de compradores "
                f"varia {ratio:.0%} entre a variante com mais e com menos tráfego. "
                "Interpretar lifts de volume com cautela."
            )

    for grupo in groups:
        sub = df.loc[df["Grupos de usuários"] == grupo, "compradores"]
        q1, q3 = sub.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr > 0:
            outliers = sub[(sub > q3 + 1.5 * iqr) | (sub < q1 - 1.5 * iqr)]
            if len(outliers) > 0:
                top = sub.idxmax()
                issues.append(
                    f"Outliers de volume em {grupo}: {len(outliers)} dia(s) "
                    f"(pico em {df.loc[top, 'Data']} com {df.loc[top, 'compradores']} compradores)."
                )

    cashback_rates = df.groupby("Grupos de usuários").apply(
        lambda g: g["cashback_num"].sum() / g["vendas totais_num"].sum() * 100,
        include_groups=False,
    )
    if len(cashback_rates) > 1:
        rates_list = sorted(cashback_rates.tolist())
        diffs = [round(rates_list[i + 1] - rates_list[i], 2) for i in range(len(rates_list) - 1)]
        if diffs and len(set(diffs)) == 1 and diffs[0] > 0:
            issues.append(
                f"Cashback escalonado em degraus fixos ({', '.join(f'{r:.1f}%' for r in rates_list)}). "
                "Confirmar se as variantes representam níveis de cashback distintos."
            )

    return issues


# ---------------------------------------------------------------------------
# Métricas e estatística
# ---------------------------------------------------------------------------


def compute_group_metrics(df: pd.DataFrame) -> list[GroupMetrics]:
    metrics: list[GroupMetrics] = []
    for grupo in sorted(df["Grupos de usuários"].unique()):
        sub = df[df["Grupos de usuários"] == grupo]
        gmv = sub["vendas totais_num"].sum()
        metrics.append(
            GroupMetrics(
                grupo=grupo,
                dias=len(sub),
                compradores=int(sub["compradores"].sum()),
                gmv=gmv,
                comissao=sub["comissão_num"].sum(),
                cashback=sub["cashback_num"].sum(),
                net=sub["net"].sum(),
                avg_daily_buyers=sub["compradores"].mean(),
                avg_ticket=sub["ticket"].mean(),
                cashback_pct=sub["cashback_num"].sum() / gmv * 100 if gmv else 0,
                net_pct=sub["net"].sum() / gmv * 100 if gmv else 0,
            )
        )
    return metrics


def pairwise_tests(df: pd.DataFrame, metric_col: str, metric_label: str) -> list[PairwiseComparison]:
    daily = df.groupby(["Data", "Grupos de usuários"])[metric_col].sum().unstack()
    groups = sorted(daily.columns)
    ref = groups[0]
    results: list[PairwiseComparison] = []

    for grupo in groups[1:]:
        a = daily[ref].dropna()
        b = daily[grupo].dropna()
        aligned = pd.concat([a, b], axis=1, join="inner").dropna()
        if len(aligned) < 2:
            continue
        t_stat, p_value = stats.ttest_rel(aligned.iloc[:, 0], aligned.iloc[:, 1])
        ref_mean = aligned.iloc[:, 0].mean()
        lift = (aligned.iloc[:, 1].mean() - ref_mean) / ref_mean * 100 if ref_mean else 0
        results.append(
            PairwiseComparison(
                grupo_a=ref,
                grupo_b=grupo,
                metric=metric_label,
                lift_pct=lift,
                p_value=p_value,
                significant=p_value < 0.05,
            )
        )
    return results


def choose_winner(
    metrics: list[GroupMetrics],
    comparisons: list[PairwiseComparison],
    issues: list[str],
) -> tuple[str, str, str]:
    """
    Critério de decisão:
    1. Maximizar receita líquida total (comissão − cashback) — o que o Méliuz retém.
    2. Em empate de net (<3%), preferir maior GMV.
    3. Nunca escalar variante com net ≤ 0, salvo se todas forem ≤ 0.
    """
    viable = [m for m in metrics if m.net > 0]
    pool = viable if viable else metrics

    pool_sorted = sorted(pool, key=lambda m: m.net, reverse=True)
    best = pool_sorted[0]

    if len(pool_sorted) > 1:
        second = pool_sorted[1]
        net_gap = (best.net - second.net) / abs(second.net) * 100 if second.net else 100
        if abs(net_gap) < 3:
            gmv_best = max(pool, key=lambda m: m.gmv)
            if gmv_best.grupo != best.grupo:
                best = gmv_best

    net_comps = [c for c in comparisons if c.metric == "receita líquida diária" and c.grupo_b == best.grupo]
    ref = metrics[0].grupo
    if best.grupo == ref:
        confidence = "alta — melhor receita líquida e baseline de referência"
    elif net_comps and net_comps[0].significant:
        confidence = "alta — diferença estatisticamente significativa (p < 0,05)"
    elif net_comps:
        confidence = "média — melhor receita líquida, mas diferença não significativa"
    else:
        confidence = "média"

    if any("SRM" in i or "desbalanceamento" in i for i in issues):
        confidence = "média — possível desbalanceamento de tráfego nos dados"

    runner = sorted(metrics, key=lambda m: m.net, reverse=True)[1] if len(metrics) > 1 else None
    gmv_leader = max(metrics, key=lambda m: m.gmv)

    decision_parts = [
        f"Escalar **{best.grupo}** para 100% do tráfego.",
        f"Receita líquida total: R$ {best.net:,.0f} ({best.net_pct:.2f}% do GMV).",
        f"Cashback efetivo: {best.cashback_pct:.2f}% do GMV.",
    ]

    if runner and gmv_leader.grupo != best.grupo:
        vol_lift_comps = [c for c in comparisons if c.metric == "compradores diários" and c.grupo_b == gmv_leader.grupo]
        if vol_lift_comps and vol_lift_comps[0].lift_pct > 5 and vol_lift_comps[0].significant:
            decision_parts.append(
                f"Nota: {gmv_leader.grupo} gera +{vol_lift_comps[0].lift_pct:.1f}% de compradores "
                f"e R$ {gmv_leader.gmv:,.0f} de GMV, mas com R$ {gmv_leader.net:,.0f} de receita líquida "
                f"({gmv_leader.net - best.net:+,.0f} vs. {best.grupo}). "
                "Só faz sentido priorizar volume se a estratégia for crescimento a curto prazo "
                "com margem sacrificada."
            )

    if best.net_pct <= 0:
        decision_parts.append("ALERTA: variante vencedora tem margem líquida ≤ 0. Revisar estrutura de comissão.")

    return best.grupo, " ".join(decision_parts), confidence


def infer_test_name(path: Path, partner: str) -> str:
    stem = path.stem
    match = re.search(r"parceiro([ABC])", stem, re.I)
    letter = match.group(1).upper() if match else partner.split()[-1]
    return f"Teste Cashback — Parceiro {letter}"


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------


def format_brl(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def generate_report(result: AnalysisResult) -> str:
    lines: list[str] = []
    lines.append(f"# {result.test_name}")
    lines.append("")
    lines.append(f"**Parceiro:** {result.partner}  ")
    lines.append(f"**Período:** {result.period_start} a {result.period_end}  ")
    lines.append(f"**Arquivo:** `{result.file_path}`  ")
    lines.append(f"**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## Resumo executivo")
    lines.append("")
    lines.append(f"**Decisão:** {result.decision}")
    lines.append("")
    lines.append(f"**Confiança:** {result.confidence}")
    lines.append("")
    lines.append(f"**Variante a escalar:** {result.winner}")
    lines.append("")
    lines.append("## Métricas por variante")
    lines.append("")
    lines.append(
        "| Variante | Dias | Compradores | GMV | Comissão | Cashback | "
        "Receita líquida | Cashback % | Margem líquida % | Ticket médio |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for m in result.groups:
        lines.append(
            f"| {m.grupo} | {m.dias} | {m.compradores:,} | {format_brl(m.gmv)} | "
            f"{format_brl(m.comissao)} | {format_brl(m.cashback)} | **{format_brl(m.net)}** | "
            f"{m.cashback_pct:.2f}% | {m.net_pct:.2f}% | {format_brl(m.avg_ticket)} |"
        )
    lines.append("")
    lines.append("## Testes estatísticos (pareado por dia)")
    lines.append("")
    lines.append("| Comparação | Métrica | Lift | p-value | Significativo? |")
    lines.append("|---|---|---:|---:|:---:|")
    for c in result.comparisons:
        sig = "Sim" if c.significant else "Não"
        lines.append(
            f"| {c.grupo_b} vs {c.grupo_a} | {c.metric} | {c.lift_pct:+.1f}% | "
            f"{c.p_value:.4f} | {sig} |"
        )
    lines.append("")
    lines.append("## Qualidade dos dados")
    lines.append("")
    if result.data_issues:
        for issue in result.data_issues:
            lines.append(f"- ⚠️ {issue}")
    else:
        lines.append("- Nenhum alerta crítico identificado.")
    lines.append("")
    lines.append("## Metodologia")
    lines.append("")
    lines.append(
        "A receita líquida (comissão − cashback) é a métrica primária de decisão — "
        "representa o valor que o Méliuz retém em cada venda. Testes t pareados comparam "
        "métricas diárias entre variantes no mesmo período. Lifts de volume são considerados "
        "como contexto, mas não substituem margem quando a diferença de receita líquida é material."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


def analyze(path: Path) -> AnalysisResult:
    df = load_dataset(path)
    issues = detect_data_issues(df)
    metrics = compute_group_metrics(df)

    comparisons: list[PairwiseComparison] = []
    comparisons.extend(pairwise_tests(df, "net", "receita líquida diária"))
    comparisons.extend(pairwise_tests(df, "compradores", "compradores diários"))
    comparisons.extend(pairwise_tests(df, "vendas totais_num", "GMV diário"))

    winner, decision, confidence = choose_winner(metrics, comparisons, issues)
    partner = df["Parceiro"].iloc[0]

    best = next(m for m in metrics if m.grupo == winner)
    runner = sorted(metrics, key=lambda m: m.net, reverse=True)[1] if len(metrics) > 1 else best

    description = (
        f"Teste de cashback com {len(metrics)} variantes durante "
        f"{metrics[0].dias} dias. "
        f"Cashback efetivo varia de {min(m.cashback_pct for m in metrics):.1f}% "
        f"a {max(m.cashback_pct for m in metrics):.1f}% do GMV. "
        f"Receita líquida de {winner}: {format_brl(best.net)} vs. "
        f"{runner.grupo}: {format_brl(runner.net)}."
    )

    return AnalysisResult(
        file_path=str(path),
        partner=partner,
        period_start=str(df["Data"].min()),
        period_end=str(df["Data"].max()),
        groups=metrics,
        comparisons=comparisons,
        data_issues=issues,
        winner=winner,
        decision=decision,
        confidence=confidence,
        test_name=infer_test_name(path, partner),
        description=description,
    )


def result_to_tracking_row(result: AnalysisResult) -> dict[str, str]:
    return {
        "data_analise": datetime.now().strftime("%Y-%m-%d"),
        "nome_teste": result.test_name,
        "parceiro": result.partner,
        "periodo": f"{result.period_start} a {result.period_end}",
        "variantes": ", ".join(m.grupo for m in result.groups),
        "resultado": result.description,
        "decisao": result.decision,
        "variante_escalar": result.winner,
        "confianca": result.confidence,
        "alertas": " | ".join(result.data_issues) if result.data_issues else "Nenhum",
    }


def update_tracking_sheet(row: dict[str, str], tracking_path: Path) -> None:
    tracking_path.parent.mkdir(parents=True, exist_ok=True)
    if tracking_path.exists():
        existing = pd.read_csv(tracking_path)
        updated = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
    else:
        updated = pd.DataFrame([row], columns=list(TRACKING_COLUMNS))
    updated.to_csv(tracking_path, index=False)


def run_analysis(
    dataset_path: Path,
    output_dir: Path,
    tracking_path: Path,
) -> AnalysisResult:
    result = analyze(dataset_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    slug = dataset_path.stem.replace("dataset_", "").replace(" ", "_")
    report_path = output_dir / f"relatorio_{slug}.md"
    report_path.write_text(generate_report(result), encoding="utf-8")

    update_tracking_sheet(result_to_tracking_row(result), tracking_path)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analisa teste A/B de cashback e gera relatório + registro na planilha."
    )
    parser.add_argument("dataset", type=Path, help="Caminho para o CSV do teste")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports"),
        help="Diretório para salvar relatórios (padrão: reports/)",
    )
    parser.add_argument(
        "--tracking",
        type=Path,
        default=Path("tracking_sheet.csv"),
        help="CSV de acompanhamento de testes (padrão: tracking_sheet.csv)",
    )
    args = parser.parse_args()

    if not args.dataset.exists():
        print(f"Erro: arquivo não encontrado: {args.dataset}", file=sys.stderr)
        return 1

    result = run_analysis(args.dataset, args.output_dir, args.tracking)

    print(f"\n{'='*60}")
    print(f"  {result.test_name}")
    print(f"{'='*60}")
    print(f"  Decisão: escalar {result.winner} para 100% do tráfego")
    print(f"  Confiança: {result.confidence}")
    if result.data_issues:
        print(f"  Alertas: {len(result.data_issues)}")
    print(f"\n  Relatório: {args.output_dir / ('relatorio_' + args.dataset.stem.replace('dataset_', '') + '.md')}")
    print(f"  Planilha:  {args.tracking}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
