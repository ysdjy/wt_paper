"""
Fig4-3 (鲁棒性) final composite assembly -- refinement round (borders removed, matching Fig4-2's
round-4 treatment): (a) task-landscape heatmap row on top, (b) paired-change bars + (c1)/(c2)
external task-level dumbbell profiles side by side below. No figure-level title; every panel
caption centered below its own panel. No outer border, no inner block borders -- grouping is
conveyed by whitespace/proportion only, per explicit user instruction (framing added separately
later). GridSpec margins set on construction, never adjusted after panels are drawn.
"""
import os
import sys
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
import style as st  # noqa: E402
import panels as pn  # noqa: E402

HERE = os.path.dirname(__file__)
FIG_DIR = os.path.normpath(os.path.join(HERE, ".."))
OUT_DIR = os.path.join(FIG_DIR, "outputs")

st.apply_style()

MM_PER_IN = 25.4
WIDTH_MM = 178
HEIGHT_MM = 128  # reduced from 132mm now that the real cause of the huge a<->b/c gap is fixed
# (see hspace note below), not just margins

# IMPORTANT lesson from user-reported feedback this round: `hspace` in a 3-row GridSpec applies to
# BOTH inter-row gaps (row0-spacer and spacer-row2), scaled by the AVERAGE of all three row
# heights -- with row0/row2 at ~1.0-1.05 and hspace=0.55, that alone added ~0.79 height-ratio-units
# of gap on top of the explicit 0.10-unit spacer, i.e. a gap almost as tall as row1 itself. Cutting
# the explicit spacer (0.14->0.10) barely changed the VISIBLE gap because hspace, not the spacer,
# was the dominant term -- exactly opposite of what was assumed when "hspace was left unchanged as
# the proven-safe value" last round. Fixed properly this time: hspace cut to 0.15 (the real lever),
# spacer restored to a normal 0.14 (now doing the actual, controllable, intentional-gap job).


def build():
    taskwise, panel_b_df, panel_c_df = pn.load_all()

    fig = plt.figure(figsize=(WIDTH_MM / MM_PER_IN, HEIGHT_MM / MM_PER_IN))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.05, 0.14, 1.0],
                            left=0.072, right=0.968, top=0.972, bottom=0.048, hspace=0.32)

    # Row 1: (a) 3 mini-heatmaps + shared colorbar
    row1 = gs[0].subgridspec(1, 4, width_ratios=[1, 1, 1, 0.07], wspace=0.18)
    axes_a = [fig.add_subplot(row1[i]) for i in range(3)]
    im = None
    for i, task in enumerate(pn.TASKS):
        im = pn.panel_a_task(axes_a[i], taskwise, task, show_yticks=(i == 0))
    cax = fig.add_subplot(row1[3])
    cb = fig.colorbar(im, cax=cax)
    cb.ax.tick_params(labelsize=6.0)
    cb.set_label("Direction-corrected\nscore", fontsize=6.0, labelpad=3)
    # Group caption placed BELOW the per-heatmap "D1"/"D2"/"D3" sub-captions (axes-fraction
    # y=-0.10), computed from their real rendered position -- not a flat guessed offset from the
    # axes bottom, which is exactly the bug found and fixed on Fig4-2's panel (d) this round.
    a_caption_top = min(st.caption_bottom_fig_frac(a, -0.16) for a in axes_a)
    fig.text(0.5, a_caption_top - 0.026,
              "(a) Task-level 9-method landscape (D1/D2/D3; color = direction-corrected score, cell = raw value)",
              ha="center", va="top", fontsize=8.0, fontweight="bold", color=st.AXIS_COLOR)

    # Row 2: (b) | (c1, c2)  [gs[1] is the thin spacer row]
    row2 = gs[2].subgridspec(1, 2, width_ratios=[0.85, 1.15], wspace=0.42)
    ax_b = fig.add_subplot(row2[0])
    pn.panel_b(ax_b, panel_b_df)

    row2c = row2[1].subgridspec(1, 2, wspace=0.85)
    ax_c1 = fig.add_subplot(row2c[0])
    ax_c2 = fig.add_subplot(row2c[1])
    pn.panel_c((ax_c1, ax_c2), panel_c_df)

    # No border of any kind this round (outer or inner) -- user will add framing separately.

    return fig


def main():
    fig = build()
    paths = st.save_all(fig, OUT_DIR, "Fig4_3_robustness")
    fixed = st.save_fixed_name(fig, "fig4_3_robustness",
                                os.path.normpath(os.path.join(FIG_DIR, "..")))
    plt.close(fig)
    for k, v in paths.items():
        print(f"Wrote {k}: {v}")
    for k, v in fixed.items():
        print(f"Wrote fixed-name {k}: {v}")


if __name__ == "__main__":
    main()
