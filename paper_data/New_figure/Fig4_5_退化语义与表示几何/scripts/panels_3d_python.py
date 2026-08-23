"""
Fig4-5 (退化语义与表示几何) 3D panels C (stage-probability surface) and D (confidence surface over
q_hat), Python/matplotlib first attempt -- ported closely from 代码/8.2图17.py's
plot_stage_probability_surface / plot_confidence_surface (turbo colormap, ridge lines, camera
angle, polished pane/grid styling), substituting the current frozen 304-run lifecycle_semantics.csv
in place of the legacy data file.

IMPORTANT (display-only construction, documented per this round's requirement):
- The three ridge lines (p_E, p_M, p_L in panel C; the black max-probability ridge in panel D) are
  REAL per-run model outputs, one point per real observation, plotted directly.
- The colored SURFACE in panel C is a visual interpolation strictly BETWEEN the three real ridges
  along the stage axis (E=0, M=1, L=2) -- there is no fourth, fifth, ... real stage-probability
  observation between them; the surface exists only to give the ridges a continuous visual body,
  exactly as in 代码/8.2图17.py's own construction.
- The colored surface in panel D is a synthetic "confidence envelope" around the real
  (run_id, q_hat, max_prob) trajectory -- a Gaussian-attenuation band added purely for visual
  width, not a second measured dimension. Ported unchanged from 代码/8.2图17.py's own
  `plot_confidence_surface`, which already documents this as a stylistic choice.
Both facts are restated in the panel captions and in README.md, per the no-fake-data-presented-
as-measured requirement.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
import style as st  # noqa: E402

HERE = os.path.dirname(__file__)
FIG_DIR = os.path.normpath(os.path.join(HERE, ".."))
DERIVED_DIR = os.path.join(FIG_DIR, "derived")
PREVIEW_DIR = os.path.join(FIG_DIR, "outputs")

st.apply_style()

COLOR_E, COLOR_M, COLOR_L = st.STAGE_COLORS["early"], st.STAGE_COLORS["middle"], st.STAGE_COLORS["late"]
COLOR_BLACK, COLOR_GRAY = "#222222", "#777777"


def polish_3d_axis(ax):
    ax.set_facecolor("white")
    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
        axis.pane.set_facecolor((1, 1, 1, 0.0))
        axis.pane.set_edgecolor((0.86, 0.86, 0.86, 0.5))
        axis._axinfo["grid"]["color"] = (0.76, 0.76, 0.76, 0.25)
        axis._axinfo["grid"]["linewidth"] = 0.5
        axis._axinfo["axisline"]["color"] = (0.18, 0.18, 0.18, 1.0)
    ax.tick_params(axis="x", labelsize=6.2, pad=0)
    ax.tick_params(axis="y", labelsize=6.2, pad=1)
    ax.tick_params(axis="z", labelsize=6.2, pad=1)


def panel_c(ax, df):
    df = df.sort_values("run_id")
    x = df["run_id"].values.astype(float)
    probs = np.vstack([df["prob_early"].values, df["prob_middle"].values, df["prob_late"].values])
    y_dense = np.linspace(0, 2, 90)
    X, Y = np.meshgrid(x, y_dense)
    Z = np.zeros_like(X)
    for i in range(len(x)):
        Z[:, i] = np.interp(y_dense, [0, 1, 2], probs[:, i])

    surf = ax.plot_surface(X, Y, Z, cmap=cm.turbo, linewidth=0, antialiased=True, alpha=0.90,
                            rstride=1, cstride=4, shade=True)
    for y0, z, color in [(0, probs[0], COLOR_E), (1, probs[1], COLOR_M), (2, probs[2], COLOR_L)]:
        ax.plot(x, np.full_like(x, y0), z, color=color, linewidth=2.2, zorder=8)

    ax.set_xlabel("Run index", labelpad=3, fontsize=6.8)
    ax.set_ylabel("Stage axis", labelpad=3, fontsize=6.8)
    ax.set_zlabel("Stage probability", labelpad=3, fontsize=6.8)
    ax.set_xlim(x.min(), x.max()); ax.set_ylim(-0.05, 2.05); ax.set_zlim(0, 1.05)
    ax.set_yticks([0, 1, 2]); ax.set_yticklabels(["E", "M", "L"])
    ax.view_init(elev=26, azim=-58)
    ax.set_box_aspect((2.3, 1.0, 1.05))
    polish_3d_axis(ax)

    handles = [Line2D([0], [0], color=COLOR_E, lw=2.2, label="$p_E$ ridge (real)"),
               Line2D([0], [0], color=COLOR_M, lw=2.2, label="$p_M$ ridge (real)"),
               Line2D([0], [0], color=COLOR_L, lw=2.2, label="$p_L$ ridge (real)"),
               Patch(facecolor=cm.turbo(0.72), alpha=0.75, label="Interpolated surface")]
    leg = ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.70, 0.92), fontsize=5.6,
                     borderpad=0.35, labelspacing=0.28, handlelength=1.6, frameon=True)
    leg.get_frame().set_facecolor("white"); leg.get_frame().set_edgecolor("#BDBDBD")
    leg.get_frame().set_linewidth(0.6); leg.get_frame().set_alpha(0.92)
    return surf


def panel_d(ax, df):
    df = df.sort_values("run_id")
    x = df["run_id"].values.astype(float)
    q = df["q_pred_norm"].values.astype(float)  # display-only normalized q_pred (Q_DEFINITIONS.md
    # marks this display_only_not_q_agreement_metrics -- legal for a visual axis position, never
    # used for agreement statistics, which live in panel e1 using raw q_pred)
    z0 = df["max_prob"].values.astype(float)

    band = np.linspace(-0.075, 0.075, 36)
    X = np.tile(x, (len(band), 1))
    Y = np.clip(q[None, :] + band[:, None], 0, 1)
    attenuation = np.exp(-0.5 * (band[:, None] / 0.045) ** 2)
    Z = z0[None, :] * (0.72 + 0.28 * attenuation)

    surf = ax.plot_surface(X, Y, Z, cmap=cm.turbo, linewidth=0, antialiased=True, alpha=0.90,
                            rstride=1, cstride=4, shade=True)
    ax.plot(x, q, z0, color=COLOR_BLACK, linewidth=2.0, zorder=8)
    ax.plot(x, q, np.zeros_like(z0), color=COLOR_GRAY, linewidth=1.3, linestyle="--", alpha=0.75, zorder=8)

    ax.set_xlabel("Run index", labelpad=3, fontsize=6.8)
    ax.set_ylabel(r"$\hat{q}$ (display-norm.)", labelpad=3, fontsize=6.8)
    ax.set_zlabel("Max probability", labelpad=3, fontsize=6.8)
    ax.set_xlim(x.min(), x.max()); ax.set_ylim(0, 1.02); ax.set_zlim(0, 1.05)
    ax.view_init(elev=26, azim=-62)
    ax.set_box_aspect((2.3, 1.0, 1.05))
    polish_3d_axis(ax)

    handles = [Patch(facecolor=cm.turbo(0.72), alpha=0.75, label="Confidence envelope"),
               Line2D([0], [0], color=COLOR_BLACK, lw=2.0, label="Max-prob. ridge (real)"),
               Line2D([0], [0], color=COLOR_GRAY, lw=1.3, linestyle="--", label="$\\hat{q}$ projection (real)")]
    leg = ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.55, 0.92), fontsize=5.6,
                     borderpad=0.35, labelspacing=0.28, handlelength=1.6, frameon=True)
    leg.get_frame().set_facecolor("white"); leg.get_frame().set_edgecolor("#BDBDBD")
    leg.get_frame().set_linewidth(0.6); leg.get_frame().set_alpha(0.92)
    return surf


def render_previews():
    lifecycle = pd.read_csv(os.path.join(DERIVED_DIR, "lifecycle_semantics.csv"), encoding="utf-8")

    fig = plt.figure(figsize=(3.6, 3.0))
    ax = fig.add_subplot(111, projection="3d")
    surf = panel_c(ax, lifecycle)
    cax = fig.add_axes([0.90, 0.25, 0.02, 0.5])
    fig.colorbar(surf, cax=cax).ax.tick_params(labelsize=5.6)
    fig.text(0.42, 0.03, "(c) Stage-probability surface (Python/matplotlib)",
             ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=st.AXIS_COLOR)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_c_preview.png"), dpi=220, bbox_inches="tight"); plt.close(fig)

    fig = plt.figure(figsize=(3.6, 3.0))
    ax = fig.add_subplot(111, projection="3d")
    surf = panel_d(ax, lifecycle)
    cax = fig.add_axes([0.90, 0.25, 0.02, 0.5])
    fig.colorbar(surf, cax=cax).ax.tick_params(labelsize=5.6)
    fig.text(0.42, 0.03, "(d) Confidence surface over $\\hat{q}$ (Python/matplotlib)",
             ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=st.AXIS_COLOR)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_d_preview.png"), dpi=220, bbox_inches="tight"); plt.close(fig)

    print("Wrote panel_c/d (Python 3D attempt) previews to", PREVIEW_DIR)


if __name__ == "__main__":
    render_previews()
