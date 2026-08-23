"""
Fig4-4 (消融实验 / probability-state formation) final composite assembly -- refinement round
(borders removed entirely, matching Fig4-2/4-3's treatment):
  Block I   -- (a) hard-decision performance + (b) state-wise recognition profile
  Block II  -- (c) probability-state formation, 4 representative-config small multiples
  Block III -- (d1)/(d2) variation diagnostics + (e) mechanism strip, tied together (small internal
               gap, not floating rows)
No figure-level title; every panel caption centered below its own panel. No outer border, no inner
block borders -- grouping conveyed by whitespace/proportion only, per explicit user instruction.

Spacing lesson carried over from Fig4-3's user-reported regression: in a GridSpec with an explicit
thin spacer row, `hspace` still applies (scaled by the AVERAGE of ALL row heights) to EVERY
adjacent row pair, including into/out of the spacer -- with several rows of very different height,
a moderate-looking `hspace` can dominate the visible gap far more than the spacer itself. This
round sizes `hspace` deliberately small and lets the explicit spacer rows carry the real,
controllable, intentional gap.
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
HEIGHT_MM = 188


def build():
    abs_df, traj_df, lv_df, cv_df, f1_df = pn.load_all()

    fig = plt.figure(figsize=(WIDTH_MM / MM_PER_IN, HEIGHT_MM / MM_PER_IN))
    # hspace kept small (0.14) -- the real lever is the two explicit spacer rows (index 1, 3).
    # Spacer1 (row1<->row2) widened 0.16->0.26 -- the first attempt left (a)/(b)'s captions
    # touching panel (c)'s plot area, found by opening the PNG.
    gs = fig.add_gridspec(5, 1, height_ratios=[1.0, 0.30, 0.85, 0.50, 1.28],
                            left=0.062, right=0.972, top=0.968, bottom=0.028, hspace=0.14)

    # Block I: (a) | (b)
    row1 = gs[0].subgridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.60)
    ax_a = fig.add_subplot(row1[0]); pn.panel_a(ax_a, abs_df)
    ax_b = fig.add_subplot(row1[1]); pn.panel_b(ax_b, f1_df)
    row1_caption_bottom = min(st.caption_bottom_fig_frac(ax_a, -0.16),
                               st.caption_bottom_fig_frac(ax_b, -0.16))

    # Block II: (c) main mechanism panel, 4 small multiples (gs[1] is spacer)
    row2 = gs[2].subgridspec(1, 4, wspace=0.20)
    axes_c = [fig.add_subplot(row2[i]) for i in range(4)]
    pn.panel_c(axes_c, traj_df)

    # ONE shared legend (p_E/p_M/p_L) for the whole (c) block, top-center, horizontal, longer line
    # samples -- replaces the old per-panel legend on the first sub-axes, per explicit refinement
    # request. Positioned in the row1<->row2 gap, below row1's captions and above axes_c's own top.
    hc, lc = axes_c[0].get_legend_handles_labels()
    c_x0 = min(a.get_position().x0 for a in axes_c)
    c_x1 = max(a.get_position().x1 for a in axes_c)
    c_top = max(a.get_position().y1 for a in axes_c)
    c_legend_y = min(c_top + 0.004, row1_caption_bottom - 0.010)
    fig.legend(hc, lc, loc="lower center", bbox_to_anchor=((c_x0 + c_x1) / 2, c_legend_y),
               ncol=3, fontsize=7.2, handlelength=2.6, columnspacing=1.4, handletextpad=0.5,
               frameon=False)

    # Group caption must sit BELOW the four per-config sub-captions (A1/A4/A5/A6, drawn at
    # axes-fraction y=-0.18 -- brought closer to their plots this round) -- computed from the real
    # rendered position, not a guessed flat offset (the bug class found on this panel last round).
    c_caption_top = min(st.caption_bottom_fig_frac(a, -0.13, extra=0.022) for a in axes_c)
    fig.text(0.5, c_caption_top - 0.008,
              "(c) Probability-state formation: p_E / p_M / p_L over the C6 lifecycle, representative configurations",
              ha="center", va="top", fontsize=8.2, fontweight="bold", color=st.AXIS_COLOR)

    # Block III: (d1)/(d2) + (e), tied together as one nested block (gs[3] is spacer)
    blockIII = gs[4].subgridspec(2, 1, height_ratios=[0.85, 0.55], hspace=0.62)
    row3 = blockIII[0].subgridspec(1, 2, wspace=0.42)
    axes_d = [fig.add_subplot(row3[0]), fig.add_subplot(row3[1])]
    pn.panel_d(axes_d, lv_df, cv_df)

    # ONE shared legend (A1-A6) for the whole (d) block, top-center of d1+d2 combined, replacing
    # the old in-axes legend on d1 alone -- per explicit refinement request.
    hd, ld = axes_d[0].get_legend_handles_labels()
    d_x0 = min(a.get_position().x0 for a in axes_d)
    d_x1 = max(a.get_position().x1 for a in axes_d)
    d_top = max(a.get_position().y1 for a in axes_d)
    # Anchor directly off axes_d's own top -- the previous min()-based clamp against
    # `c_caption_top` picked the WRONG branch (the c-caption's own position, not axes_d's), which
    # placed the (d) legend on top of the (c) group caption instead of above axes_d. Found by
    # opening the PNG: "...representative configurations" and "A1 A2 ... A6" were merged on one line.
    d_legend_y = d_top + 0.012
    fig.legend(hd, ld, loc="lower center", bbox_to_anchor=((d_x0 + d_x1) / 2, d_legend_y),
               ncol=6, fontsize=6.0, handlelength=2.2, columnspacing=1.0, handletextpad=0.35,
               frameon=False)

    ax_e = fig.add_subplot(blockIII[1])
    pn.panel_e(ax_e)

    # No border of any kind this round (outer or inner) -- user will add framing separately.

    return fig


def main():
    fig = build()
    paths = st.save_all(fig, OUT_DIR, "Fig4_4_ablation")
    fixed = st.save_fixed_name(fig, "fig4_4_ablation",
                                os.path.normpath(os.path.join(FIG_DIR, "..")))
    plt.close(fig)
    for k, v in paths.items():
        print(f"Wrote {k}: {v}")
    for k, v in fixed.items():
        print(f"Wrote fixed-name {k}: {v}")


if __name__ == "__main__":
    main()
