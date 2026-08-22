# Fig.3 v4 — Visual QA

Reviewed against `outputs/fig3_v4_paper_preview.png` (rendered at the true 178×130mm master
size, 200 DPI) — not just the 600dpi PNG at screen zoom.

## Scores (0–10)

| Criterion | Score | Notes |
|---|---|---|
| Reference layout similarity | 8 | Dual-axis bar+line density in (a)/(c) and the 6-node mechanism flow-chain both directly recover the reference's visual devices; layout ratio changed per the brief (top 2×2 ≈78%, mechanism band ≈22%, vs v3's roughly 50/50). |
| Information density | 9 | 4 quantitative panels (predictive/state-wise/middle-stage/lifecycle-dynamics) + a fully-annotated 6-node mechanism band, all real, nothing dropped; panel (d) now carries genuine content (real lifecycle variation curves) instead of v3's near-all-zero Rev/Jump panel. |
| Whitespace efficiency | 8 | No dead zone exceeds ~5-6% of canvas; mechanism band's generous node spacing is deliberate (readability), not waste. |
| Typography consistency | 10 | Times New Roman + STIX math throughout; every `fontsize=` call audited and raised to ≥6.5pt (the two 6.0pt instances found on review — panel (d)'s config legend, mechanism-band delta text — were bumped to 6.5pt and re-verified not to cause any new collision). |
| Color consistency | 10 | `ABLATION_COLORS` (grey→teal, A5=gold, A6=teal) and `STAGE_COLORS` used identically to fig1/fig2's palette; A5's very light warm vertical shading (not a heavy warning box) consistent across panels a/b/c. |
| Scientific faithfulness | **10** | A1-A4 confirmed byte-identical and rendered visually flat (no y-axis truncation to exaggerate); A5 dip and A6 recovery are the real magnitudes; Smooth always shown as an explicitly-labeled "improvement (%)" derived value, with the raw Smooth value annotated at each point for traceability; Rev=Jump=0 stated as real, not hidden; mechanism band uses the real `Configuration` strings and real per-node Δ vs A1 from `A1_A6_delta_vs_A1.csv`. All `np.isclose` checks pass (`logs/validation_v4.txt`). |
| A4/178mm-width readability | 8 | Confirmed legible at true preview scale after 3 rounds of real fixes (below). |

## Answers to the brief's 8 required questions

1. **Reference elements adopted**: dual-axis bar+line combo density in panels (a)/(c); light warm
   A5 shading; 6-node mechanism flow-chain with arrows between nodes.
2. **Reference elements NOT adopted, and why**: the reference's specific numeric annotations
   (e.g. its "0.0236"/"0.0136" Smooth values) — this project's real values are close in shape but
   different in the exact digits, recomputed independently and asserted to match the design doc,
   never read off the mockup.
3. **Any visual interpolation?** None in the quantitative panels. Panel (d)'s curves are the real
   per-run `local_variation_l1_smoothed` (a pre-existing centered rolling-mean smoothing already
   applied upstream in the frozen data, not something this script adds) and real cumulative sums.
4. **Any change to a real data point?** No. `validate()`'s assertions (A1-A4 identical, Smooth
   benefit ≈42.4%/≈20.5%, A6 recovery ≈0.99/1.18/1.55pp) all pass unchanged from v1/v2/v3.
5. **Smallest text at final size**: 6.5pt, uniformly, across every element in the figure.
6. **Dead space >8–10% of canvas?** No.
7. **Legend covering data?** No — panel (a)'s legend was originally `loc="lower left"` inside the
   axes, overlapping the bars (bars fill nearly the full y-range since the axis is not zero-based).
   Moved above the axes via `bbox_to_anchor=(0.5, 1.01)`; no legend now overlaps any plotted data.
8. **Caption/panel visual conflicts?** None remaining. Found and fixed 3 real ones this round (see
   README's v4 section): panel (a)'s twin-axis label was clipped/bled into panel (b) at default
   `wspace`; panels (b)/(c)'s in-plot annotations initially overlapped plotted data/lines; panel
   (d)'s two x-axis labels initially collided severely with its own caption despite a first-round
   `hspace` increase, requiring a much larger correction (0.42→1.35) than any other panel in this
   figure set needed.

## Status: **DONE**

Scientific faithfulness = 10 and every text element in the figure is ≥6.5pt, with no legend
overlapping any plotted data.

## Open issues

None outstanding.

## Post-handoff fixes (independent review, same session)

Two real true-physical-size bugs found on independent review of the fork's initial handoff, both
fixed directly:
1. Panel (b)'s "A5" x-tick label collided with its own caption below (`hspace=0.42` insufficient
   given the panel's tight y-limits push tick labels close to the axis bottom) — fixed by raising
   to `hspace=1.10`, the same magnitude panel (d) already needed for the same reason.
2. Panel (d)'s local-variation legend at `ncol=6` (one row) was wider than `ax_local`'s own box;
   since matplotlib legends aren't clipped to their parent axes, it visually overflowed into
   `ax_cum`'s area, reading as a split/broken legend ("A1 -- A2" stranded left, "A3 A4 A5 A6"
   floating over the neighboring subplot). Fixed by reflowing to `ncol=3` (2 rows), which fits
   within `ax_local`'s actual width.
