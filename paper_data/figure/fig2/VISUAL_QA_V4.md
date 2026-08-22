# Fig.2 v4 — Visual QA

Reviewed against `outputs/fig2_v4_paper_preview.png` (rendered at the true 178×125mm master
size, 200 DPI) — not just the 600dpi PNG at screen zoom.

## Scores (0–10)

| Criterion | Score | Notes |
|---|---|---|
| Reference layout similarity | 8 | Strict 2×2 dashboard, (a)/(b) visually larger than (c)/(d) per the brief; panel (a) now shares one y-axis (method labels on D1 only) and one colorbar across all 3 mini-heatmaps, closing the visible gaps v3 had; panel (d) carries 4 pale quadrant background tints as requested. |
| Information density | 9 | 3×9-method heatmap + 8-row×4-metric lollipop + 3 radar cards + 6-point balance map, all real, nothing dropped. |
| Whitespace efficiency | 8 | No dead zone exceeds ~5–6% of canvas; panel (d)'s legend sits in a deliberately reserved right margin (`right=0.86` figure bound), not a code accident. |
| Typography consistency | 10 | Times New Roman + STIX math throughout; every text element, including the smallest (panel (d)'s legend), verified ≥6.5pt at final print size (see script grep audit in the build log). |
| Color consistency | 9 | `BENEFIT_CMAP` for panel (a)'s heatmaps; `STAGE`/`METHOD_COLORS`-derived blue (Multi-task TCN-GRU) / red (DC-PSR) accents consistent across panels (b)/(c)/(d); panel (d)'s quadrant tints use the same terracotta/teal/gold family as `DIVERGING_CMAP`. |
| Scientific faithfulness | **10** | All values recomputed from frozen `paper_data` via v1's unchanged `load()`; `np.isclose` checks on PHM D1 ΔAcc/ΔM-F1, NASA and MTW-CM-avg ΔM-F1 all pass (`logs/validation_v4.txt`). Panel (c) never claims a 9-method NASA/MTW-CM comparison; panel (d) plots exactly 6 real points (asserted). No fabricated data. |
| A4/178mm-width readability | 8 | Confirmed legible at true preview scale after two post-handoff fixes (below): panel (a)'s 3-metric x-tick labels actually DID overlap horizontally within each mini-heatmap column at 0° rotation (found on independent review of the paper-preview PNG, not caught by the original build) — fixed with a 32° rotation, which resolved it without shrinking below the 6.5pt floor. Panel (c)'s radar cards are legible but tight: "Acc"/"Cons." labels from adjacent cards sit close together (not merged/overlapping characters) since 3 polar mini-axes in ~55mm total width leaves limited lateral clearance — flagged as a minor open item below rather than iterated further. |

## Answers to the brief's 8 required questions

1. **Reference elements adopted**: 2×2 dashboard with (a)/(b) larger than (c)/(d); shared y-axis
   and shared colorbar for panel (a)'s 3 task heatmaps (closing v3's visible inter-panel gaps);
   4-quadrant pale background tinting idea in panel (d).
2. **Reference elements NOT adopted, and why**: reference's fictional 9-method comparison on
   NASA/MTW-CM in what would be panel (c) — never reproduced, since those datasets were never
   evaluated with all 9 methods; reference's in-plot quadrant text labels — tried once, caused real
   collisions with data-point labels and the panel's own axis label at this figure's true physical
   size, replaced with a caption sentence instead (same fix pattern as panel (c)'s legend, below).
3. **Any visual interpolation?** None. Every lollipop/radar/scatter value is a real point estimate
   from `taskwise_absolute.csv` / `cross_dataset_absolute.csv`.
4. **Any change to a real data point?** No. `np.isclose` checks against the same headline numbers
   used in v1/v2/v3 all pass; panel (d)'s `n_points == 6` assertion passes.
5. **Smallest text at final size**: 6.5pt (panel (d)'s legend, panel (a)'s colorbar ticks) — meets
   the brief's ≥6.5pt floor; verified via a direct grep of every `fontsize=` literal in the script.
6. **Dead space >8–10% of canvas?** No.
7. **Legend covering data?** No — panel (d)'s legend was deliberately placed in a reserved right
   margin outside the plotted quadrant (figure `right=0.86` leaves that room on purpose).
8. **Caption/panel visual conflicts?** None remaining. Several real ones were found and fixed
   during this build (see README's v4 section) — most instructively, an early attempt to reuse
   fig1_v4's `ax.set_title(y<0)` trick for panel (a)'s D1/D2/D3 task tags was the *wrong* fix for
   *this* panel's geometry and caused new collisions; reverting to v3's original `ax.set_xlabel()`
   approach (which was already correct) resolved it — a reminder that a lesson from one panel
   doesn't automatically transfer to a differently-shaped one.

## Status: **DONE**

All required conditions met, including the mandatory Scientific faithfulness = 10 and the ≥6.5pt
minimum text size across every element in the figure.

## Open issues

- Panel (c)'s radar cards: "Acc"/"Cons." axis labels from horizontally-adjacent cards sit close
  together (legible, not merged) given 3 polar mini-axes packed into ~55mm total width. Not
  addressed further this round since it doesn't rise to a real collision (no overlapping
  characters).

## Post-handoff fixes (independent review, same session)

Two real true-physical-size bugs found on independent review of the fork's initial handoff, both
fixed directly:
1. Panel (a)'s 3-metric x-tick labels ("Acc↑"/"M-F1↑"/"Smooth↓") genuinely overlapped each other
   within the narrower D2/D3 mini-heatmap columns at 0° rotation. Fixed with `rotation=32,
   ha="right", rotation_mode="anchor"` — same "shorten/reflow, don't just add space" family of fix
   as fig1_v4's caption wrapping, applied to tick labels instead of caption text.
2. Panel (c)'s polar radial tick labels ("0.5"/"1.0") default to rendering along the same spoke as
   the "Acc" axis label (matplotlib's default `rlabel_position`), crowding that one corner. Fixed
   with `ax.set_rlabel_position(45)` to move them into empty space between the Acc and M-F1 spokes,
   plus increased inter-card `wspace` (0.65→1.05) for extra lateral clearance.
