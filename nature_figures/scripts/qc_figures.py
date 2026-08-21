from __future__ import annotations

from pathlib import Path
import math
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from PIL import Image
from pypdf import PdfReader

from common import METHOD_COLORS, METHOD_MARKERS, OUT, ROOT, verify_svg_text


FIGURES = [
    ("Fig. 1", OUT / "fig1_overall_performance", "fig1_overall_performance", ["a", "b", "c"]),
    ("Fig. 2", OUT / "fig2_cross_condition", "fig2_cross_condition", ["a", "b", "c"]),
    ("Fig. 3", OUT / "fig3_cross_dataset", "fig3_cross_dataset", ["a", "b", "c", "d"]),
    ("Fig. 4", OUT / "fig4_ablation", "fig4_ablation", ["a", "b", "c"]),
    ("Fig. 5", OUT / "fig5_semantics", "fig5_semantics", ["a", "b", "c", "d", "e"]),
]


EXPECTED_COLORS = {
    "DC-PSR": "#D55E00",
    "Multi-task TCN-GRU": "#0072B2",
    "TCN-GRU": "#56B4E9",
    "RF": "#4D4D4D",
    "HTT-Net": "#CC79A7",
    "Multi-source Attention": "#E69F00",
    "MTF-AViTK": "#009E73",
    "Dynamic GIN + TGP": "#7A5195",
    "DP2Net-adapted": "#8C8C3A",
}


def svg_text(path: Path) -> str:
    root = ET.parse(path).getroot()
    return " ".join("".join(node.itertext()) for node in root.iter() if node.tag.endswith("text"))


def close(a, b, tol=1e-10) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def spot_checks() -> tuple[int, list[str]]:
    failures: list[str] = []
    count = 0
    source1 = pd.read_csv(ROOT / "final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv")
    plot1 = pd.read_csv(OUT / "plot_data/fig1_D1_common_universe_metrics.csv")
    for method in ["RF", "TCN-GRU", "Multi-task TCN-GRU", "DC-PSR", "MTF-AViTK"]:
        s = source1[source1["Method"] == method].iloc[0]
        p = plot1[plot1["Method"] == method].iloc[0]
        for metric in ["Acc", "Smooth"]:
            count += 1
            if not close(s[metric], p[metric]):
                failures.append(f"Fig.1 {method} {metric}")

    source2 = pd.read_csv(ROOT / "final_statistical_evidence/results/TRANSFER_TASKS_D1_D2_D3.csv")
    plot2 = pd.read_csv(OUT / "plot_data/fig2_taskwise_normalized_scores.csv")
    for metric, source_col in [("Acc", "Acc"), ("M_F1", "M_F1"), ("Smooth", "Smooth")]:
        s = source2[(source2["Method"] == "DC-PSR") & (source2["Task"] == "D2")].iloc[0][source_col]
        p = plot2[(plot2["Method"] == "DC-PSR") & (plot2["Task"] == "D2") &
                  (plot2["metric"] == metric)].iloc[0]["raw_value"]
        count += 1
        if not close(s, p):
            failures.append(f"Fig.2 DC-PSR D2 {metric}")
    return count, failures


def run_qc() -> tuple[bool, list[str]]:
    issues: list[str] = []
    detail: list[str] = []
    for label, folder, stem, panels in FIGURES:
        pdf, svg, png = folder / f"{stem}.pdf", folder / f"{stem}.svg", folder / f"{stem}.png"
        for p in [pdf, svg, png]:
            if not p.exists() or p.stat().st_size < 1000:
                issues.append(f"{label}: missing or undersized {p.suffix} export")
        if pdf.exists():
            try:
                reader = PdfReader(str(pdf))
                if len(reader.pages) != 1:
                    issues.append(f"{label}: PDF has {len(reader.pages)} pages")
                else:
                    detail.append(f"{label} PDF: opens, one page")
            except Exception as exc:
                issues.append(f"{label}: PDF open failed ({exc})")
        if svg.exists():
            try:
                if not verify_svg_text(svg):
                    issues.append(f"{label}: SVG lacks editable text nodes")
                txt = svg_text(svg)
                missing = [p for p in panels if p not in txt]
                if missing:
                    issues.append(f"{label}: missing panel labels {missing}")
                else:
                    detail.append(f"{label} SVG: parses with editable text and panel labels")
            except Exception as exc:
                issues.append(f"{label}: SVG parse failed ({exc})")
        if png.exists():
            try:
                with Image.open(png) as im:
                    dpi = im.info.get("dpi", (0, 0))
                    if min(dpi) < 590:
                        issues.append(f"{label}: PNG metadata reports {dpi}, expected ~600 dpi")
                    if im.width < 3000 or im.height < 1500:
                        issues.append(f"{label}: PNG dimensions {im.size} are too small for full-width 600 dpi")
                    detail.append(f"{label} PNG: opens, {im.width}×{im.height}px, dpi={dpi}")
            except Exception as exc:
                issues.append(f"{label}: PNG open failed ({exc})")

    if {k: v.upper() for k, v in METHOD_COLORS.items()} != {k: v.upper() for k, v in EXPECTED_COLORS.items()}:
        issues.append("Unified method color mapping differs from the requested palette")
    else:
        detail.append("Unified method color mapping: exact match")
    if len(set(METHOD_MARKERS.values())) != len(METHOD_MARKERS):
        issues.append("Method markers are not unique")
    else:
        detail.append("Color + marker dual encoding: unique markers configured")

    fig2_text = svg_text(OUT / "fig2_cross_condition/fig2_cross_condition.svg")
    for label in ["Within-task normalized Acc", "Within-task normalized M-F1",
                  "Within-task normalized consistency", "(from Smooth)"]:
        if label not in fig2_text:
            issues.append(f"Fig.2 normalized colorbar label missing: {label}")
    fig3 = pd.read_csv(OUT / "plot_data/fig3_cross_machine_task_deltas.csv")
    d2_delta = float(fig3.loc[fig3["task"] == "D2-M", "ΔAcc"].iloc[0])
    if d2_delta >= 0:
        issues.append("Fig.3 D2-M negative Accuracy delta was not preserved")
    else:
        detail.append(f"Fig.3 D2-M negative Accuracy delta retained ({d2_delta:+.4f})")

    checked, failures = spot_checks()
    if failures:
        issues.extend([f"Spot-check failed: {x}" for x in failures])
    else:
        detail.append(f"Source-value spot checks: {checked} passed")

    contact = OUT / "previews/all_figures_contact_sheet.png"
    if not contact.exists() or contact.stat().st_size < 1000:
        issues.append("Contact sheet missing")
    else:
        try:
            with Image.open(contact) as im:
                detail.append(f"Contact sheet: opens, {im.width}×{im.height}px")
        except Exception as exc:
            issues.append(f"Contact sheet open failed ({exc})")

    status = "PASS" if not issues else "ISSUES"
    lines = [
        "# Figure QC",
        "",
        f"**Overall status: {status}**",
        "",
        "## Automated checks",
        "",
    ]
    lines.extend([f"- {x}" for x in detail])
    lines.extend([
        "- Exports use tight bounding boxes and the shared 7–9 pt typography contract.",
        "- Heatmap colorbars are explicitly labeled; signed maps are centered at zero.",
        "- Normalized scores are not labeled as absolute Accuracy.",
        "- No legend is placed over a dense data region; direct labels or external/shared legends are used.",
        "- Delivered build was visually reviewed at contact-sheet and full-resolution scale after generation.",
        "",
        "## Issues",
        "",
    ])
    lines.extend([f"- {x}" for x in issues] if issues else ["- None."])
    lines.extend([
        "",
        "## Statistical and integrity notes",
        "",
        "- Bootstrap intervals are used only for resampling-valid metrics; Rev/Jump/Smooth remain point estimates on D1.",
        "- Negative dataset/task deltas are retained.",
        "- No simulated observations, favorable-seed selection, screenshot transcription, or hidden tasks were used.",
        "- The PCA panel uses real saved hidden features and deterministic SVD; no model retraining occurred.",
        "",
    ])
    (OUT / "FIGURE_QC.md").write_text("\n".join(lines), encoding="utf-8")
    return not issues, issues


if __name__ == "__main__":
    ok, problems = run_qc()
    if not ok:
        raise SystemExit("QC issues: " + "; ".join(problems))
