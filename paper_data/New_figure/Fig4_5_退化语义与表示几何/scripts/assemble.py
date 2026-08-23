"""
Fig4-5 (退化语义与表示几何) final composite assembly -- refinement round (borders removed entirely,
matching Fig4-2/4-3/4-4's treatment):
  Block 1 -- (A) raw-feature representation geometry (a/b/c)
  Block 2 -- (B) shared latent representation geometry (d/e/f)
  Block 3 -- (C)+(D) probability-state geometry, the two 3D surfaces
  Block 4 -- (e1)/(e2) semantic anchors
No figure-level title; every panel/block caption centered below it. No outer border, no inner block
borders -- grouping conveyed by whitespace/proportion only, per explicit user instruction (framing
added separately later).

Bug class fixed proactively this round (found repeatedly on Fig4-2/4-4): a group caption placed at
a flat guessed offset from the axes bottom, without accounting for the per-panel sub-captions
already sitting there, ends up overlapping them. Blocks A/B's group captions are now computed from
the real rendered bottom of their sub-captions (`caption_bottom_fig_frac`), not a guessed constant.
"""
import os
import sys
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
import style as st  # noqa: E402
import panels as pn  # noqa: E402
import panels_3d_python as p3d  # noqa: E402

HERE = os.path.dirname(__file__)
FIG_DIR = os.path.normpath(os.path.join(HERE, ".."))
DERIVED_DIR = os.path.join(FIG_DIR, "derived")
OUT_DIR = os.path.join(FIG_DIR, "outputs")

st.apply_style()

MM_PER_IN = 25.4
WIDTH_MM = 178
HEIGHT_MM = 222  # reduced from 240mm -- no border to clear; spacer rows retuned individually


def build():
    raw_pca, hidden_pca, lifecycle, q_df, wear_df = pn.load_all()

    fig = plt.figure(figsize=(WIDTH_MM / MM_PER_IN, HEIGHT_MM / MM_PER_IN))
    # hspace kept small -- explicit spacer rows (index 1, 3, 5) carry the real, controllable gap
    # between blocks (lesson from Fig4-3/4-4's regressions this round).
    # Spacer1 (A<->B) widened 0.20->0.34 -- the (A) group caption (computed to clear its own
    # sub-captions) still collided with row B's panels above it, found by opening the PNG: the
    # gap wasn't big enough to hold both the caption AND clearance before block B begins.
    gs = fig.add_gridspec(7, 1, height_ratios=[0.85, 0.34, 0.85, 0.20, 1.25, 0.20, 1.05],
                            left=0.058, right=0.958, top=0.975, bottom=0.024, hspace=0.10)

    # Block 1 (A): raw-feature geometry
    rowA = gs[0].subgridspec(1, 3, wspace=0.42)
    axesA = [fig.add_subplot(rowA[i]) for i in range(3)]
    pn.geometry_row(axesA, raw_pca, "Raw features", show_lifecycle_path=False, letters="abc")
    # Group caption computed from the REAL bottom of the per-panel sub-captions (y=-0.20), not a
    # guessed flat offset -- the latter was found to nearly collide with the sub-captions here
    # (same bug class as Fig4-2 panel (d) / Fig4-4 panel (c)), fixed proactively this round.
    a_caption_top = min(st.caption_bottom_fig_frac(a, -0.20) for a in axesA)
    fig.text(0.5, a_caption_top - 0.010,
              "(A) Raw-feature representation geometry (n = 780; C1/C4/C6 conditions, markers o/^/s)",
              ha="center", va="top", fontsize=8.0, fontweight="bold", color=st.AXIS_COLOR)

    # Block 2 (B): shared latent geometry (gs[1] spacer)
    rowB = gs[2].subgridspec(1, 3, wspace=0.42)
    axesB = [fig.add_subplot(rowB[i]) for i in range(3)]
    pn.geometry_row(axesB, hidden_pca, "Shared $h_{c,t}$", show_lifecycle_path=True, letters="def")
    b_caption_top = min(st.caption_bottom_fig_frac(a, -0.20) for a in axesB)
    fig.text(0.5, b_caption_top - 0.010,
              "(B) Shared latent representation geometry (same PCA pipeline, same 780 samples)",
              ha="center", va="top", fontsize=8.0, fontweight="bold", color=st.AXIS_COLOR)

    # Block 3 (C+D): 3D surfaces (gs[3] spacer)
    rowCD = gs[4].subgridspec(1, 2, wspace=0.08)
    ax_c = fig.add_subplot(rowCD[0], projection="3d")
    p3d.panel_c(ax_c, lifecycle)
    ax_d = fig.add_subplot(rowCD[1], projection="3d")
    p3d.panel_d(ax_d, lifecycle)
    pos_c, pos_d = ax_c.get_position(), ax_d.get_position()
    cd_bottom = min(pos_c.y0, pos_d.y0)
    fig.text((pos_c.x0 + pos_c.x1) / 2, cd_bottom - 0.010, "(C) Stage-probability surface over the C6 lifecycle",
              ha="center", va="top", fontsize=8.0, fontweight="bold", color=st.AXIS_COLOR)
    fig.text((pos_d.x0 + pos_d.x1) / 2, cd_bottom - 0.010, "(D) Confidence surface over $\\hat{q}$",
              ha="center", va="top", fontsize=8.0, fontweight="bold", color=st.AXIS_COLOR)

    # Block 4 (E): semantic evidence (gs[5] spacer)
    rowE = gs[6].subgridspec(1, 2, wspace=0.36)
    ax_e1 = fig.add_subplot(rowE[0]); pn.panel_e1(ax_e1, q_df)
    ax_e2 = fig.add_subplot(rowE[1]); pn.panel_e2(ax_e2, lifecycle, wear_df)

    # No border of any kind this round (outer or inner) -- user will add framing separately.

    return fig


def main():
    fig = build()
    paths = st.save_all(fig, OUT_DIR, "fig4_5_degradation_representation")
    fixed = st.save_fixed_name(fig, "fig4_5_degradation_representation",
                                os.path.normpath(os.path.join(FIG_DIR, "..")))
    plt.close(fig)
    for k, v in paths.items():
        print(f"Wrote {k}: {v}")
    for k, v in fixed.items():
        print(f"Wrote fixed-name {k}: {v}")


if __name__ == "__main__":
    main()
