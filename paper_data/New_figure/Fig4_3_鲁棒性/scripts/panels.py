"""
Fig4-3 (鲁棒性) panel-first rendering. See Fig4_2's panels.py for the established pattern this
follows: each panel(ax, ...) function is independently testable; render_previews() saves one
standalone PNG per panel for visual review before assembly.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
import data_utils as du  # noqa: E402
import style as st  # noqa: E402

HERE = os.path.dirname(__file__)
FIG_DIR = os.path.normpath(os.path.join(HERE, ".."))
DERIVED_DIR = os.path.join(FIG_DIR, "derived")
PREVIEW_DIR = os.path.join(FIG_DIR, "outputs", "panel_previews")
os.makedirs(PREVIEW_DIR, exist_ok=True)

st.apply_style()

TASKS = ["D1", "D2", "D3"]
HEATMAP_METRICS = [("Acc", "higher"), ("M_F1", "higher"), ("Smooth", "lower")]


def load_all():
    taskwise = pd.read_csv(os.path.join(DERIVED_DIR, "taskwise_absolute.csv"), encoding="utf-8")
    panel_b = pd.read_csv(os.path.join(DERIVED_DIR, "panel_b_deltas.csv"), encoding="utf-8")
    panel_c = pd.read_csv(os.path.join(DERIVED_DIR, "panel_c_tasklevel.csv"), encoding="utf-8")
    return taskwise, panel_b, panel_c


# ---------------------------------------------------------------------------
# (a) D1/D2/D3 x 9-method mini-heatmaps, Acc/M-F1/Smooth only
# ---------------------------------------------------------------------------
def panel_a_task(ax, taskwise, task, show_yticks=True, show_cbar_label=False):
    sub = taskwise[taskwise["Task"] == task].set_index("Method").loc[st.METHOD_ORDER]
    mat_raw = sub[["Acc", "M_F1", "Smooth"]].values.astype(float)
    mat_score = mat_raw.copy()
    # direction-corrected within-column normalization for color only; raw value always annotated
    for j, (_, direction) in enumerate(HEATMAP_METRICS):
        col = mat_raw[:, j]
        lo, hi = col.min(), col.max()
        norm = (col - lo) / (hi - lo) if hi > lo else np.zeros_like(col)
        mat_score[:, j] = norm if direction == "higher" else 1 - norm

    im = ax.imshow(mat_score, cmap=st.CONFUSION_CMAP, vmin=0, vmax=1, aspect="auto")
    for i in range(mat_raw.shape[0]):
        for j in range(mat_raw.shape[1]):
            val = mat_raw[i, j]
            txt = f"{val:.3f}" if j == 2 else f"{val:.3f}"
            color = "white" if mat_score[i, j] >= 0.6 else "#222222"
            ax.text(j, i, txt, ha="center", va="center", fontsize=5.6, color=color)

    ax.set_xticks(range(3))
    ax.set_xticklabels(["Acc↑", "M-F1↑", "Smooth↓"], fontsize=6.4)
    if show_yticks:
        ax.set_yticks(range(len(st.METHOD_ORDER)))
        ax.set_yticklabels(st.METHOD_ORDER, fontsize=6.2)
    else:
        ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    # DC-PSR row outline
    dc_i = st.METHOD_ORDER.index("DC-PSR")
    ax.add_patch(plt.Rectangle((-0.5, dc_i - 0.5), 3, 1, fill=False, edgecolor="#C44E52", linewidth=1.3, zorder=6))
    st.panel_caption_below(ax, task, y=-0.16, fontsize=8.0)
    return im


def panel_a(fig, gs_row, taskwise):
    axes = [fig.add_subplot(gs_row[i]) for i in range(3)]
    im = None
    for i, (ax, task) in enumerate(zip(axes, TASKS)):
        im = panel_a_task(ax, taskwise, task, show_yticks=(i == 0))
    return axes, im


# ---------------------------------------------------------------------------
# (b) Multi-task TCN-GRU -> DC-PSR paired change, PHM D1/D2/D3 + NASA + MTW-CM
# ---------------------------------------------------------------------------
def panel_b(ax, panel_b_df):
    groups = panel_b_df["group"].tolist()
    x = np.arange(len(groups))
    w = 0.20
    cols = [("delta_Acc_pp", "#0072B2", st.HATCHES["h1"], "ΔAcc (pp)"),
            ("delta_MF1_pp", "#009E73", st.HATCHES["h2"], "ΔM-F1 (pp)"),
            ("Smooth_benefit_pct", "#D55E00", st.HATCHES["h3"], "Smooth benefit (%)"),
            ("Jump_benefit_pct", "#8C564B", st.HATCHES["h4"], "Jump benefit (%)")]
    for k, (col, color, hatch, label) in enumerate(cols):
        off = (k - 1.5) * w
        st.hatched_bar(ax, x + off, panel_b_df[col].values, w, color, hatch, label=label)
    ax.axhline(0, color=st.AXIS_COLOR, linewidth=0.8, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=18, ha="right", fontsize=6.6)
    ax.set_ylabel("Change (positive = improvement)")
    st.style_axis(ax, add_arrows=True, show_x_arrow=False)
    ax.legend(loc="upper left", ncol=2, fontsize=6.0, bbox_to_anchor=(0.0, 1.18),
              handlelength=1.1, columnspacing=0.7)
    st.panel_caption_below(ax, "(b) Backbone → DC-PSR paired change across conditions/datasets", y=-0.34)


# ---------------------------------------------------------------------------
# (c) External task-level paired profiles: NASA N1-N4 + MTW-CM D1-M/D2-M/D3-M
# ---------------------------------------------------------------------------
def _dumbbell(ax, panel_c_df, metric, ylabel, higher_is_better):
    tasks = panel_c_df["dataset"] + " " + panel_c_df["task"]
    tasks = tasks.drop_duplicates().tolist()
    order = sorted(set(panel_c_df["task"]), key=lambda t: (t.startswith("D"), t))
    order = ["N1", "N2", "N3", "N4", "D1-M", "D2-M", "D3-M"]
    y = np.arange(len(order))[::-1]
    for yi, task in zip(y, order):
        sub = panel_c_df[panel_c_df["task"] == task]
        bb = sub[sub["Method"] == "Multi-task TCN-GRU"][metric].iloc[0]
        dc = sub[sub["Method"] == "DC-PSR"][metric].iloc[0]
        ax.plot([bb, dc], [yi, yi], color="#B0B4B8", linewidth=1.3, zorder=2)
        ax.scatter(bb, yi, marker="D", s=34, color=st.METHOD_COLORS["Multi-task TCN-GRU"],
                   edgecolor="white", linewidth=0.4, zorder=4)
        ax.scatter(dc, yi, marker="*", s=56, color=st.METHOD_COLORS["DC-PSR"],
                   edgecolor="white", linewidth=0.4, zorder=4)
    ax.set_yticks(y)
    ax.set_yticklabels(order, fontsize=6.6)
    ax.set_xlabel(ylabel)
    st.style_axis(ax, add_arrows=True)
    return y, order


def panel_c(axes, panel_c_df):
    ax1, ax2 = axes
    _dumbbell(ax1, panel_c_df, "M_F1", "M-F1 (↑ better)", True)
    st.panel_caption_below(ax1, "(c1) M-F1 by task\n(NASA + MTW-CM)", y=-0.26)
    handles = [plt.Line2D([0], [0], marker="D", color=st.METHOD_COLORS["Multi-task TCN-GRU"],
                          linestyle="", markersize=5, label="Multi-task TCN-GRU"),
               plt.Line2D([0], [0], marker="*", color=st.METHOD_COLORS["DC-PSR"],
                          linestyle="", markersize=7, label="DC-PSR")]
    ax1.legend(handles=handles, loc="upper left", fontsize=6.0, bbox_to_anchor=(0.0, 1.16), ncol=2,
               handlelength=1.0, columnspacing=0.7)

    _dumbbell(ax2, panel_c_df, "Smooth", "Smooth (↓ better)", False)
    st.panel_caption_below(ax2, "(c2) Smooth by task\n(NASA + MTW-CM)", y=-0.26)


def render_previews():
    taskwise, panel_b_df, panel_c_df = load_all()

    fig = plt.figure(figsize=(7.2, 2.6))
    gs = fig.add_gridspec(1, 3, wspace=0.15, left=0.16, right=0.90, top=0.90, bottom=0.20)
    axes, im = panel_a(fig, gs, taskwise)
    cax = fig.add_axes([0.92, 0.22, 0.014, 0.62])
    fig.colorbar(im, cax=cax).ax.tick_params(labelsize=6.0)
    fig.text(0.53, 0.99, "(a) Task-level 9-method landscape (direction-corrected color; raw value shown)",
              ha="center", va="top", fontsize=7.6, fontweight="bold")
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_a_preview.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(4.2, 2.8)); panel_b(ax, panel_b_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_b_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(5.4, 3.0))
    panel_c(axes, panel_c_df)
    fig.subplots_adjust(wspace=0.55, bottom=0.30, top=0.82)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_c_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    print("Wrote panel previews to", PREVIEW_DIR)


if __name__ == "__main__":
    render_previews()
