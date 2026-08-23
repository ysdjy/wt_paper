# Figure Final QA — CIE-submission refinement pass

Checked after all four figures (Fig4-2, Fig4-3, Fig4-4, Fig4-5) were refined per
`FIGURE_REFINEMENT_AUDIT.md`. This is a **layout/visual QA only** — no data or scientific-claim
check is repeated here (that was validated per-figure in each `logs/validation.txt` during the
original build rounds and was not touched this round).

## 1. Outer border consistency

All four `assemble.py` scripts call `st.add_outer_border(fig)` as the last drawing step, using
the same shared function (`OUTER_BORDER_COLOR = "#4A4A4A"`, `lw=1.0`, rounded corners,
`rounding=0.012`). **Consistent across all four.** Verified visually in each figure's final
preview PNG — one continuous rounded rectangle, no clipping, no double lines.

## 2. Section/block border consistency

All four use `st.add_block_border()` with the same default styling
(`BLOCK_BORDER_COLOR = "#B9C2CC"`, `lw=0.8`, bold `label_color = "#3A5068"` corner labels, same
`label_fontsize=7.0`). Block counts: Fig4-2 = 2, Fig4-3 = 2, Fig4-4 = 3, Fig4-5 = 4 — count differs
by figure (as it should, driven by each figure's own scientific block structure per
`FIGURE_REBUILD_AUDIT.md`), but the visual language (thin light rounded rectangle + small bold
blue-gray corner label) is identical everywhere. **Consistent.**

## 3. Font hierarchy consistency

All four call `st.apply_style()` from the same module (Times New Roman + STIX mathtext,
`font.size=8.5`, `axes.labelsize=8.7`, `xtick/ytick.labelsize=7.6`, `legend.fontsize=7.5`).
Per-panel deviations (Fig4-5's dense 2D scatters at 6.2–6.8pt; Fig4-4's mechanism strip at
5.6–8.0pt) are density-driven exceptions already documented in each figure's own README, not
accidental drift — re-confirmed this round, no new divergence introduced by the border/spacing
changes. **Consistent**, no fixes needed.

## 4. Early/Middle/Late color consistency

`STAGE_COLORS = {early: #1B9E77, middle: #E6A01A, late: #C44E52}`, one definition in
`_shared/style.py`, imported (never redefined) by Fig4-4's panel (c) and Fig4-5's blocks A/B/e2.
**Consistent**, re-confirmed by re-reading every import statement this round — no figure carries a
local override.

## 5. Multi-task TCN-GRU / DC-PSR color consistency

`METHOD_COLORS["Multi-task TCN-GRU"] = #0072B2` (blue), `METHOD_COLORS["DC-PSR"] = #C44E52` (warm
red), one definition, used identically in Fig4-2 (panels a/b/c/e) and Fig4-3 (panel c dumbbells).
**Consistent.**

## 6. Panel captions below-center, no top titles

Re-verified across all four `panels.py`/`assemble.py` files: every `panel_caption_below()` call
places text centered (`ha="center"`) at a negative `y` (below the axes in `ax.transAxes`
coordinates); every group/block `fig.text()` caption likewise sits below its block, centered.
**No `fig.suptitle()` call exists in any of the four `assemble.py` files** — confirmed by grep, not
just visual inspection. **All captions below-center; no top titles.**

## 7. Remaining whitespace check

Canvas heights (width fixed at 178mm for all four):

| Figure | Before this round | After this round | Change |
|---|---|---|---|
| Fig4-2 | 158mm | 160mm | +2mm (traded for correct block-border clearance, not shrunk) |
| Fig4-3 | 140mm | 142mm | +2mm (same reason) |
| Fig4-4 | 232mm | 196mm | **−36mm (−15.5%)**, root-cause fix (panel (e)'s dead `ylim` zone + tied Block III together) |
| Fig4-5 | 255mm | 240mm | **−15mm (−5.9%)**, block E enlarged at the same time (not a pure shrink) |

Fig4-2/4-3 grew slightly rather than shrinking — direct measurement found their original margins
were already close to the minimum needed once a border boundary also has to fit in the row-to-row
gap (documented per-figure in each README's refinement-round section); forcing them smaller on the
first attempt caused real caption/border collisions (found and reverted, see each README). Fig4-4
and Fig4-5 — the two figures explicitly flagged as loosest in the audit — got the intended
substantial reduction. No figure has an obviously dead, unexplained blank region remaining after
this pass; any remaining whitespace (e.g. Fig4-3 panel (b)'s bar chart headroom above its tallest
bar) is inherent to the real data range, not a layout defect.

## 8. PDF readability at real submission width

All four PDFs generated at their true 178mm design width (not scaled post-hoc). Fixed-name PDFs
(`paper_data/New_figure/final_pdf/fig4_2_main_comparison.pdf`, `fig4_3_robustness.pdf`,
`fig4_4_ablation.pdf`, `fig4_5_degradation_representation.pdf`) confirmed to exist, non-zero size
(123KB–880KB, Fig4-5 largest due to its two vector 3D surfaces), generated via the same
`bbox_inches="tight", pad_inches=0.04` settings for every figure. Not independently re-opened in a
PDF viewer as part of this automated pass — recommend a final human check at actual print width
before submission, per the brief's own suggested step 4 (per-figure) which was performed via PNG
preview at each round, not the PDF file directly.

## 9. Data provenance — unchanged, re-affirmed not re-derived

This round touched **only** `assemble.py` (layout/borders/spacing) and, in Fig4-4's case, panel
(e)'s pure-decoration `ylim`/caption-offset (no data plotted in that panel). No `load_data.py`, no
`panels.py` data-plotting logic, and no `derived/*.csv` file was modified in any of the four
figures. All headline-number validations from each figure's original build round
(`logs/validation.txt`) remain valid and were not re-run this round since nothing they check was
touched.

## 10. Interpolation / envelope disclosures

Fig4-5 panels (C)/(D)'s legends still read "Interpolated surface" / "Confidence envelope" (never
"measured field"); the underlying construction (real ridges, synthetic body) is unchanged from the
first-pass build. README §6 (Fig4-5) still documents this in full. **No change needed, re-confirmed
present.**

## 11. Known residual items (disclosed, not blocking)

- Fig4-5's 3D panel caption gap is tighter than before but still slightly larger than a 2D panel's,
  an inherent `mplot3d` bbox-padding limitation (see Fig4-5 README §7a).
- Fig4-2's panel (b) "Multi-source Attention" label and Fig4-4's panel (b) A6 M-F1/L-F1 label
  proximity (both previously disclosed, unrelated to this round's border/spacing work) are
  unchanged and still minor.
- None of the four figures has had a second-reviewer pass independent of the session that built
  them, or a physical print-out check — recommended before final submission.

## 12. Summary verdict

All four figures now share one consistent, deliberate visual system (outer border, block borders,
font, stage colors, method colors, below-center captions, no top titles) implemented through one
shared `_shared/style.py` module rather than four independently-written styles. Fig4-4 and Fig4-5
— the two figures the brief flagged as needing the deepest work — received the largest whitespace
reductions (15.5% and 5.9% height respectively) via root-cause geometry fixes, not cropping. Every
collision found during this round was found by actually opening the rendered PNG (not assumed from
the code), consistent with this project's standing quality bar.
