"""
Fig4-5 (退化语义与表示几何) panel-first rendering, 2D blocks (A: raw geometry, B: shared geometry)
and semantic block (E1/E2). 3D panels (C/D) live in panels_3d.py (separate module: 3D setup is
heavier and independently iterated/possibly MATLAB-swapped).
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
import data_utils as du  # noqa: E402
import style as st  # noqa: E402

HERE = os.path.dirname(__file__)
FIG_DIR = os.path.normpath(os.path.join(HERE, ".."))
DERIVED_DIR = os.path.join(FIG_DIR, "derived")
PREVIEW_DIR = os.path.join(FIG_DIR, "outputs")
os.makedirs(PREVIEW_DIR, exist_ok=True)

st.apply_style()

CONDITION_MARKERS = st.CONDITION_MARKERS  # C1:o, C4:^, C6:s


def load_all():
    raw_pca = pd.read_csv(os.path.join(DERIVED_DIR, "raw_pca_780.csv"), encoding="utf-8")
    hidden_pca = pd.read_csv(os.path.join(DERIVED_DIR, "hidden_pca_780.csv"), encoding="utf-8")
    lifecycle = pd.read_csv(os.path.join(DERIVED_DIR, "lifecycle_semantics.csv"), encoding="utf-8")
    q_df = pd.read_csv(os.path.join(DERIVED_DIR, "q_agreement.csv"), encoding="utf-8")
    wear_df = pd.read_csv(os.path.join(DERIVED_DIR, "wear_by_predicted_stage.csv"), encoding="utf-8")
    return raw_pca, hidden_pca, lifecycle, q_df, wear_df


# ---------------------------------------------------------------------------
# Shared scatter helper (condition-marker-encoded), ported in spirit from 代码/8.2图18.py
# ---------------------------------------------------------------------------
def _scatter_by_condition(ax, df, colors, cmap=None, vmin=None, vmax=None):
    last = None
    for c in ["C1", "C4", "C6"]:
        mask = (df["condition"] == c).values
        if not mask.any():
            continue
        if cmap is None:
            last = ax.scatter(df["PC1"].values[mask], df["PC2"].values[mask],
                              c=np.asarray(colors, dtype=object)[mask], marker=CONDITION_MARKERS[c],
                              s=10, alpha=0.85, edgecolor="#F7F7F7", linewidth=0.2, zorder=3)
        else:
            last = ax.scatter(df["PC1"].values[mask], df["PC2"].values[mask],
                              c=np.asarray(colors, dtype=float)[mask], cmap=cmap, vmin=vmin, vmax=vmax,
                              marker=CONDITION_MARKERS[c], s=10, alpha=0.85, edgecolor="#F7F7F7",
                              linewidth=0.2, zorder=3)
    return last


def _overlay_misclassified(ax, df):
    mis = (df["misclassified"].fillna(0).astype(int) > 0).values
    if mis.sum() == 0:
        return
    ax.scatter(df["PC1"].values[mis], df["PC2"].values[mis], s=32, facecolors="none",
               edgecolors="#1E1E1E", linewidth=0.9, marker="o", zorder=8)


def _lifecycle_path(ax, df, bins=12):
    q = df["q_true"].values.astype(float)
    emb = df[["PC1", "PC2"]].values
    edges = np.linspace(q.min(), q.max(), bins + 1)
    centers = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (q >= lo) & (q <= hi)
        if mask.sum() >= 3:
            centers.append(emb[mask].mean(axis=0))
    if len(centers) < 3:
        return
    centers = np.asarray(centers)
    ax.plot(centers[:, 0], centers[:, 1], linestyle=(0, (4, 2)), color="#4F4F4F",
            linewidth=1.0, alpha=0.75, zorder=6)
    ax.annotate("", xy=centers[-1], xytext=centers[-2],
                arrowprops=dict(arrowstyle="->", lw=1.0, color="#4F4F4F"), zorder=7)


def _set_same_limits(axes, dfs):
    all_xy = np.vstack([d[["PC1", "PC2"]].values for d in dfs])
    xmin, xmax = all_xy[:, 0].min(), all_xy[:, 0].max()
    ymin, ymax = all_xy[:, 1].min(), all_xy[:, 1].max()
    dx, dy = (xmax - xmin) * 0.08, (ymax - ymin) * 0.08
    for ax in axes:
        ax.set_xlim(xmin - dx, xmax + dx)
        ax.set_ylim(ymin - dy, ymax + dy)


def geometry_row(axes, df, row_label, show_lifecycle_path, letters):
    stage = df["true_stage"].astype(str).str.lower()
    stage_colors = stage.map(st.STAGE_COLORS).fillna("#999999").values
    q = df["q_true"].values.astype(float)
    u = df["uncertainty"].values.astype(float)

    ax = axes[0]
    _scatter_by_condition(ax, df, stage_colors)
    _overlay_misclassified(ax, df)
    if show_lifecycle_path:
        _lifecycle_path(ax, df)
    ax.set_xlabel("PC1", fontsize=6.8); ax.set_ylabel("PC2", fontsize=6.8)
    st.style_axis(ax, add_arrows=False, grid_axis=None)
    st.panel_caption_below(ax, f"({letters[0]}) {row_label} / true stage", y=-0.20, fontsize=6.8, fontweight="normal")

    ax = axes[1]
    m1 = _scatter_by_condition(ax, df, q, cmap=st.Q_CMAP, vmin=q.min(), vmax=q.max())
    if show_lifecycle_path:
        _lifecycle_path(ax, df)
    ax.set_xlabel("PC1", fontsize=6.8); ax.set_ylabel("PC2", fontsize=6.8)
    st.style_axis(ax, add_arrows=False, grid_axis=None)
    st.panel_caption_below(ax, f"({letters[1]}) {row_label} / q", y=-0.20, fontsize=6.8, fontweight="normal")
    cb1 = ax.figure.colorbar(m1, ax=ax, fraction=0.046, pad=0.03)
    cb1.ax.tick_params(labelsize=5.4); cb1.set_label("$q_{true}$", fontsize=6.0, labelpad=2)

    ax = axes[2]
    m2 = _scatter_by_condition(ax, df, u, cmap=st.U_CMAP, vmin=0, vmax=max(u.max(), 1e-6))
    ax.set_xlabel("PC1", fontsize=6.8); ax.set_ylabel("PC2", fontsize=6.8)
    st.style_axis(ax, add_arrows=False, grid_axis=None)
    st.panel_caption_below(ax, f"({letters[2]}) {row_label} / uncertainty", y=-0.20, fontsize=6.8, fontweight="normal")
    cb2 = ax.figure.colorbar(m2, ax=ax, fraction=0.046, pad=0.03)
    cb2.ax.tick_params(labelsize=5.4); cb2.set_label("Uncertainty", fontsize=6.0, labelpad=2)

    # PC1/PC2 axis limits must be set from panel (0)'s data-driven range BEFORE the colorbars above
    # steal horizontal space from axes (1)/(2) -- fraction/pad-based colorbars shrink an axes'
    # box after the fact, so limits are applied last here to stay correct post-shrink.
    _set_same_limits(axes, [df])
    return m1, m2


# ---------------------------------------------------------------------------
# (E1) q_true vs q_pred agreement
# ---------------------------------------------------------------------------
def panel_e1(ax, q_df):
    x = q_df["q_true"].values
    y = q_df["q_pred"].values
    stage = q_df["true_stage"].astype(str).str.lower().map(st.STAGE_COLORS).fillna("#999999")
    ax.scatter(x, y, s=10, c=stage, alpha=0.7, edgecolor="none", zorder=3)
    lims = [0, 1]
    ax.plot(lims, lims, color="#8A8D8F", linewidth=1.0, linestyle="--", zorder=2, label="y = x")
    r2 = du.r2_coefficient_of_determination(x, y)
    rho = pd.Series(x).corr(pd.Series(y), method="spearman")
    mae = float(np.mean(np.abs(x - y)))
    ax.text(0.03, 0.97, f"$R^2$={r2:.3f}\n$\\rho$={rho:.3f}\nMAE={mae:.3f}", transform=ax.transAxes,
            fontsize=6.4, ha="left", va="top",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#BDBDBD", linewidth=0.6))
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("$q_{true}$"); ax.set_ylabel("$q_{pred}$ (raw)")
    st.style_axis(ax, add_arrows=True)
    st.panel_caption_below(ax, "(e1) Degradation-position agreement", y=-0.24)


# ---------------------------------------------------------------------------
# (E2) VB by predicted stage
# ---------------------------------------------------------------------------
def panel_e2(ax, lifecycle_df, wear_df):
    order = ["early", "middle", "late"]
    data = [lifecycle_df.loc[lifecycle_df["pred_stage"] == s, "VB_true"].values for s in order]
    positions = np.arange(1, 4)
    parts = ax.violinplot(data, positions=positions, widths=0.7, showextrema=False)
    for pc, s in zip(parts["bodies"], order):
        pc.set_facecolor(st.STAGE_COLORS[s]); pc.set_alpha(0.35); pc.set_edgecolor(st.STAGE_COLORS[s])
    bp = ax.boxplot(data, positions=positions, widths=0.16, showfliers=False, patch_artist=True,
                     medianprops=dict(color="#222222", linewidth=1.2))
    for patch, s in zip(bp["boxes"], order):
        patch.set_facecolor("white"); patch.set_edgecolor(st.STAGE_COLORS[s]); patch.set_linewidth(1.2)
    rng = np.random.RandomState(0)
    for i, (s, vals) in enumerate(zip(order, data)):
        jitter = rng.normal(0, 0.05, size=len(vals))
        ax.scatter(positions[i] + jitter, vals, s=5, color=st.STAGE_COLORS[s], alpha=0.45, zorder=4)
    means = wear_df.set_index("predicted_stage").loc[order, "VB_mean"].values
    for i, m in enumerate(means):
        ax.scatter(positions[i], m, marker="D", s=32, color="#222222", zorder=6)
        ax.annotate(f"{m:.1f}", (positions[i], m), fontsize=6.2, xytext=(9, 0),
                    textcoords="offset points", va="center")
    ax.set_xticks(positions); ax.set_xticklabels(["Early", "Middle", "Late"])
    ax.set_ylabel("VB (μm)")
    st.style_axis(ax, add_arrows=True)
    st.panel_caption_below(ax, "(e2) Physical wear (VB) by predicted stage", y=-0.20)


def render_previews():
    raw_pca, hidden_pca, lifecycle, q_df, wear_df = load_all()

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5))
    m1, m2 = geometry_row(axes, raw_pca, "Raw features", show_lifecycle_path=False, letters="abc")
    fig.subplots_adjust(wspace=0.42, bottom=0.28, top=0.90)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_a_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5))
    m1, m2 = geometry_row(axes, hidden_pca, "Shared $h_{c,t}$", show_lifecycle_path=True, letters="def")
    fig.subplots_adjust(wspace=0.42, bottom=0.28, top=0.90)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_b_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.2, 2.8)); panel_e1(ax, q_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_e1_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.2, 2.8)); panel_e2(ax, lifecycle, wear_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_e2_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    print("Wrote panel previews (a, b, e1, e2) to", PREVIEW_DIR)


if __name__ == "__main__":
    render_previews()
