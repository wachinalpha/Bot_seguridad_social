#!/usr/bin/env python3
"""
RAG Eval Report Visualizer
==========================
Generates a chart from an eval report JSON file.

Usage:
    .venv/bin/python3 tests/eval/plot_report.py                          # latest report
    .venv/bin/python3 tests/eval/plot_report.py tests/eval/reports/2026-02-21_17-45-30.json
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless — no display required
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

REPORTS_DIR = Path(__file__).parent / "reports"


def load_report(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_latest_report() -> Path:
    reports = sorted(REPORTS_DIR.glob("*.json"))
    if not reports:
        print("No reports found in tests/eval/reports/")
        sys.exit(1)
    return reports[-1]


def plot_report(report: dict, report_path: Path) -> Path:
    results = report["results"]
    ts = report.get("timestamp", report_path.stem)

    case_ids = [r["id"].replace("q", "Q").replace("_", "\n", 1) for r in results]
    n = len(results)

    # ── metrics per case (0-1 scale)
    hit_rate      = [r["hit_rate"] for r in results]
    precision     = [r["precision_at_k"] for r in results]
    ndcg          = [r["ndcg_at_k"] for r in results]
    kw_coverage   = [r["keyword_coverage"] for r in results]
    citation_ok   = [1.0 if r["citation_present"] else 0.0 for r in results]
    refusal_ok    = [1.0 if r["refusal_accurate"] else 0.0 for r in results]
    latency_ms    = [r["latency_ms"] / 1000 for r in results]   # → seconds

    # ── aggregate
    agg_labels = ["Hit Rate", "Precision@k", "NDCG@k", "Citation\nPresence", "Kw\nCoverage", "Refusal\nAccuracy"]
    agg_values = [
        np.mean(hit_rate),
        np.mean(precision),
        np.mean(ndcg),
        np.mean(citation_ok),
        np.mean(kw_coverage),
        np.mean(refusal_ok),
    ]

    # ── layout: 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    fig.suptitle(f"RAG Eval Report — {ts}", fontsize=13, fontweight="bold", y=1.01)

    colors = plt.cm.tab10.colors
    bar_width = 0.15
    x = np.arange(n)

    # ────────────────────────────────────────────
    # Panel 1: Per-case retrieval + citation bars
    # ────────────────────────────────────────────
    ax1 = axes[0]
    metrics_per_case = {
        "Hit Rate":    hit_rate,
        "Prec@k":     precision,
        "NDCG@k":     ndcg,
        "Citation":   citation_ok,
        "Kw Cov":     kw_coverage,
    }
    offsets = np.linspace(-(len(metrics_per_case)-1)/2, (len(metrics_per_case)-1)/2, len(metrics_per_case))

    for idx, (label, values) in enumerate(metrics_per_case.items()):
        ax1.bar(x + offsets[idx] * bar_width, values, bar_width,
                label=label, color=colors[idx], alpha=0.85)

    ax1.set_xticks(x)
    ax1.set_xticklabels(case_ids, fontsize=8)
    ax1.set_ylim(0, 1.15)
    ax1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax1.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax1.set_title("Per-Case Metrics", fontweight="bold")
    ax1.legend(fontsize=7, loc="upper right")
    ax1.axhline(1.0, color="gray", linewidth=0.5, linestyle="--")
    ax1.set_ylabel("Score")

    # ────────────────────────────────────────────
    # Panel 2: Aggregate radar / horizontal bar
    # ────────────────────────────────────────────
    ax2 = axes[1]
    bar_colors = [
        "seagreen" if v >= 0.75 else "goldenrod" if v >= 0.5 else "tomato"
        for v in agg_values
    ]
    bars = ax2.barh(agg_labels, agg_values, color=bar_colors, alpha=0.85, height=0.55)
    ax2.set_xlim(0, 1.15)
    ax2.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax2.set_title("Aggregate Scores", fontweight="bold")
    ax2.axvline(0.75, color="gray", linewidth=0.8, linestyle="--", alpha=0.6)

    for bar, val in zip(bars, agg_values):
        ax2.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                 f"{val*100:.0f}%", va="center", fontsize=9, fontweight="bold")

    legend_patches = [
        mpatches.Patch(color="seagreen",  label="≥ 75% (good)"),
        mpatches.Patch(color="goldenrod", label="≥ 50% (ok)"),
        mpatches.Patch(color="tomato",    label="< 50% (needs work)"),
    ]
    ax2.legend(handles=legend_patches, fontsize=7, loc="lower right")

    # ────────────────────────────────────────────
    # Panel 3: Latency per case
    # ────────────────────────────────────────────
    ax3 = axes[2]
    bar_lat_colors = [
        "seagreen" if s <= 5 else "goldenrod" if s <= 10 else "tomato"
        for s in latency_ms
    ]
    ax3.bar(x, latency_ms, color=bar_lat_colors, alpha=0.85)
    ax3.set_xticks(x)
    ax3.set_xticklabels(case_ids, fontsize=8)
    ax3.set_ylabel("Seconds")
    ax3.set_title("Latency per Case", fontweight="bold")
    avg_lat = np.mean(latency_ms)
    ax3.axhline(avg_lat, color="navy", linewidth=1.2, linestyle="--",
                label=f"avg {avg_lat:.1f}s")
    ax3.legend(fontsize=8)

    for i, val in enumerate(latency_ms):
        ax3.text(i, val + 0.1, f"{val:.1f}s", ha="center", fontsize=8)

    plt.tight_layout()

    # ── save next to report
    out_path = report_path.with_suffix(".png")
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main():
    if len(sys.argv) > 1:
        report_path = Path(sys.argv[1])
    else:
        report_path = find_latest_report()
        print(f"Using latest report: {report_path.name}")

    report = load_report(report_path)
    out = plot_report(report, report_path)
    print(f"Chart saved → {out}")


if __name__ == "__main__":
    main()
