"""
Fig4-2 (主比较) final composite assembly -- refinement round 4 (borders removed entirely).

User will add any framing themselves later in PPT/layout. This round draws NO outer border and NO
inner block borders of any kind -- only the axes/heatmap/colorbar outlines each panel needs on its
own. Structure/grouping is conveyed purely by whitespace, alignment, and proportion. Compared to
round 3: no border means no reserved border-clearance margin is needed, which is used here to
tighten top/bottom margins and the two inter-row spacers further (carefully -- round 3 already hit
a real collision from over-tightening `hspace` together with a spacer; this round only tightens
spacer heights, `hspace` stays at its proven-safe value).
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
HEIGHT_MM = 150  # reduced from 160mm -- no border to clear means top/bottom margins shrink, and
# the two inter-row spacers are trimmed a bit further (matplotlib's bbox_inches="tight" still
# captures every caption regardless of the nominal (0,1) figure extent, so there is no longer any
# need to reserve extra bottom margin "to stay inside a border" -- that border is gone).

# SPACER1_H (a/b/c <-> d) and SPACER2_H (d <-> e1/e2/e3) both trimmed further vs round 3;
# hspace is LEFT UNCHANGED at its round-2/3 proven-safe value -- round 3's one real regression
# came from cutting hspace and a spacer at the same time, so this round only touches spacer height.
ROW1_H, SPACER1_H, ROW2_H, SPACER2_H, ROW3_H = 1.30, 0.085, 0.85, 0.050, 1.05


def build():
    main_df, ac_df, ci_df, rep_df, paired_df = pn.load_all()

    fig = plt.figure(figsize=(WIDTH_MM / MM_PER_IN, HEIGHT_MM / MM_PER_IN))
    gs = fig.add_gridspec(5, 1, height_ratios=[ROW1_H, SPACER1_H, ROW2_H, SPACER2_H, ROW3_H],
                            left=0.058, right=0.978, top=0.975, bottom=0.045, hspace=0.55)

    # Row 1: (a) | gap | (b) | wider gap | (c) -- explicit spacer COLUMNS (same technique as the
    # spacer ROWS used for vertical gaps) so (a)-(b) and (b)-(c) can have DIFFERENT gap widths,
    # which a single `wspace` cannot do. Per explicit request: (b) shifts left (closer to (a), but
    # never touching it), (c) shifts right (using its own previously-empty right margin) so its
    # y-axis method-name labels stop crowding into (b)'s territory.
    # (a)-(b) gap widened again (was 0.20) to shift the (b)+(c) pair further right as a group,
    # per explicit request -- (b)-(c) gap itself is unchanged (their relative spacing was already
    # correct, only the whole pair needed to move right).
    row1 = gs[0].subgridspec(1, 5, width_ratios=[1.25, 0.32, 0.85, 0.42, 1.05], wspace=0.0)
    ax_a = fig.add_subplot(row1[0]); pn.panel_a(ax_a, main_df)
    ax_b = fig.add_subplot(row1[2]); pn.panel_b(ax_b, ac_df)
    # (c) is now a two-part panel (paired-effect forest on top, Smooth-reduction strip below),
    # sharing row1's height but split internally -- its own subgridspec, not a single Axes.
    col_c = row1[4].subgridspec(2, 1, height_ratios=[0.56, 0.44], hspace=0.70)
    ax_c_top = fig.add_subplot(col_c[0])
    ax_c_bot = fig.add_subplot(col_c[1])
    pn.panel_c(ax_c_top, ax_c_bot, main_df, paired_df)
    # (c)'s caption and two short annotation lines are placed here (not inside panels.py) using
    # REAL rendered positions of ax_c_top/ax_c_bot -- panel (c) is internally two differently-sized
    # sub-axes, so a flat axes-fraction guess (the bug class hit repeatedly on (d) and Fig4-5 A/B)
    # would not reliably land at the same figure-height as (a)/(b)'s captions or clear ax_c_bot's
    # own x-axis label. The caption's y is pinned to (a)'s actual caption baseline (same row,
    # same ROW1_CAPTION_Y offset) so all three of (a)/(b)/(c) align; the two annotation lines are
    # anchored to ax_c_bot's real bottom edge via caption_bottom_fig_frac.
    pos_a = ax_a.get_position()
    row1_caption_fig_y = pos_a.y0 + pn.ROW1_CAPTION_Y * pos_a.height
    pos_c_bot = ax_c_bot.get_position()
    x_c_center = (pos_c_bot.x0 + pos_c_bot.x1) / 2
    ann1_y = st.caption_bottom_fig_frac(ax_c_bot, -0.58, extra=0.010)
    ann2_y = ann1_y - 0.022
    fig.text(x_c_center, ann1_y, "point estimate only, no CI (order-dependent metric)",
              ha="center", va="top", fontsize=5.4, color="#7A7A7A", style="italic")
    fig.text(x_c_center, ann2_y,
              "Rev = 0 → 0;  Jump = 0 → 0  (both methods, identical on the 304-run sequence)",
              ha="center", va="top", fontsize=5.6, color="#555555")
    fig.text(x_c_center, min(row1_caption_fig_y, ann2_y - 0.028),
              "(c) Paired effect of DC-PSR\nrelative to its backbone",
              ha="center", va="top", fontsize=9.0, fontweight="bold", color=st.AXIS_COLOR)

    # Row 2: (d) 4 confusion matrices + thin shared colorbar (gs[1] is spacer)
    row2 = gs[2].subgridspec(1, 5, width_ratios=[1, 1, 1, 1, 0.055], wspace=0.28)
    axes_d = [fig.add_subplot(row2[i]) for i in range(4)]
    im = pn.panel_d_row(axes_d, st.REPRESENTATIVE_METHODS)
    cax = fig.add_subplot(row2[4])
    cb = fig.colorbar(im, cax=cax)
    cb.ax.tick_params(labelsize=6.0)
    cb.set_label("Row-normalized\nproportion", fontsize=6.2, labelpad=3)
    # Group caption must sit BELOW the per-matrix method-name captions (RF/MTF-AViTK/...), which
    # are drawn at axes-fraction y=-0.30 under each matrix -- placing it at a small fixed offset
    # from the matrices' own bottom (row2_bottom - 0.030) ignored those method-name captions
    # entirely and the two ended up on top of each other (found by opening the PNG: "MTF-AViTK"
    # and "Multi-task TCN-GRU" were overlapped/obscured by the group-caption line). Fixed by
    # computing the real bottom of the deepest method-name caption first.
    method_caption_bottom = min(st.caption_bottom_fig_frac(a, -0.30) for a in axes_d)
    fig.text(0.5, method_caption_bottom - 0.010, "(d) Representative confusion matrices (row-normalized; count)",
              ha="center", va="top", fontsize=8.4, fontweight="bold", color=st.AXIS_COLOR)

    # Row 3: (e1)/(e2)/(e3) triptych (gs[3] is spacer)
    row3 = gs[4].subgridspec(1, 3, wspace=0.50)
    ax_e1 = fig.add_subplot(row3[0]); pn.panel_e_recognition(ax_e1, rep_df)
    ax_e2 = fig.add_subplot(row3[1]); pn.panel_e_misclass(ax_e2, rep_df)
    ax_e3 = fig.add_subplot(row3[2]); pn.panel_e_consistency(ax_e3, main_df)

    # No border of any kind this round (outer or inner) -- user will add framing separately.
    # Grouping is conveyed by whitespace/proportion only.

    return fig


def main():
    fig = build()
    paths = st.save_all(fig, OUT_DIR, "Fig4_2_main_comparison")
    fixed = st.save_fixed_name(fig, "fig4_2_main_comparison",
                                os.path.normpath(os.path.join(FIG_DIR, "..")))
    plt.close(fig)
    for k, v in paths.items():
        print(f"Wrote {k}: {v}")
    for k, v in fixed.items():
        print(f"Wrote fixed-name {k}: {v}")


if __name__ == "__main__":
    main()
