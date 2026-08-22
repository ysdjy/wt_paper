# Fig.1 v4 — Visual QA

Reviewed against `outputs/fig1_v4_paper_preview.png` (rendered at the true 178×120mm master
size, 200 DPI) — not just the 600dpi PNG at screen zoom.

## Scores (0–10)

| Criterion | Score | Notes |
|---|---|---|
| Reference layout similarity | 8 | Heatmap-left/confusion-right-2×2/diagnostics-bottom matches `视觉参考效果图/` structure; slim under-heatmap colorbar, shared confusion-matrix colorbar, and CI inset all directly recover reference devices. Docked one point: reference's 3-block diagnostic rhythm is now one connected panel (a deliberate, documented deviation, not a miss). |
| Information density | 9 | 9×12 heatmap + 4 confusion matrices + 5-method diagnostic landscape + CI inset, all at true print scale, nothing dropped. |
| Whitespace efficiency | 8 | No dead zone exceeds ~5% of canvas area; the only "spare" space is the CI inset's own reclaimed corner, used deliberately. |
| Typography consistency | 10 | Times New Roman + STIX math throughout, matching the original paper's own `plt.rcParams` convention (confirmed by reading `代码/1.3.1可视化.py` etc., not assumed). Sizes: captions 8.4pt bold, axis labels ~8.7pt, ticks 6.5–7.6pt, heatmap/confusion cells 6.3–6.5pt, smallest annotations (colorbar/CI-inset labels) raised to 6.5pt — every text element now clears the brief's 6.5pt floor. |
| Color consistency | 9 | `BENEFIT_CMAP` (terracotta→cream→cyan→blue) used only for the landscape heatmap; sequential `Blues` used only for confusion matrices — visually distinct roles, as required. DC-PSR/Multi-task TCN-GRU marked by thin colored row outlines, not colored tick text. |
| Scientific faithfulness | **10** | All values recomputed from frozen `paper_data`, `np.isclose`-validated against the same headline numbers as v1/v2/v3 (see `logs/validation_v4.txt`). No fabricated data, no fictional method roster, no distorted axis. Required for DONE — met. |
| A4/178mm-width readability | 8 | Confirmed legible at the true preview scale; smallest text (colorbar/inset tick labels) is small but readable, not garbled or overlapping. |

## Answers to the brief's 8 required questions

1. **Reference elements adopted**: heatmap+2×2-confusion top row / full-width diagnostics bottom
   row proportions; slim colorbar under the heatmap; one shared colorbar for all 4 confusion
   matrices instead of 4 separate ones; sequential Blues distinct from the landscape heatmap's
   benefit palette; thin method-accent row outlines instead of colored text.
2. **Reference elements NOT adopted, and why**: the reference's exact 3-way split of the bottom
   diagnostics area — kept as one connected panel instead, per the brief's own instruction that it
   should read as "one complete diagnosis landscape, not 3 unrelated plots"; the reference's own
   numbers/method roster (fictional, e.g. its 8-generic-baseline scheme) — never used.
3. **Any visual interpolation?** None. Every value plotted is a real point estimate or a real
   bootstrap CI bound; no smoothing, no synthetic samples.
4. **Any change to a real data point?** No. Confirmed via `logs/validation_v4.txt`'s 10
   `np.isclose` headline checks (unchanged from v1/v2/v3) plus a fresh row-count assertion.
5. **Smallest text at final size**: 6.5pt (colorbar tick labels, confusion-matrix cell text,
   CI-inset labels) — meets the brief's stated ≥6.5pt floor for all body text.
6. **Dead space >8–10% of canvas?** No single contiguous region exceeds that; the largest
   "empty-looking" area is the white space around the CI inset, which is deliberate framing, not
   waste.
7. **Legend covering data?** No — checked specifically: panel (c)'s legend sits above the axes
   (`bbox_to_anchor=(0.0, 1.14)`), the CI inset has an opaque white background (`facecolor="white"`,
   `zorder=10`) so it never blends into the bars behind it.
8. **Caption/panel visual conflicts?** None remaining. Two real ones were found and fixed during
   this build (see README's v4 section): panel (a)/(b)'s single-line captions overflowed
   horizontally into each other at 178mm width (fixed by wrapping to 2 lines + shortening); the
   confusion-matrix sub-captions, when built via nested `sub_caption()` with a large `hspace`
   correction, squashed each matrix's own content instead of just adding a gap (fixed by switching
   to `ax.set_title(method, y=-0.34)`, which is robust because it's positioned relative to the
   axes' own transform, not a separately-computed GridSpec cell).

## Status: **DONE**

All required conditions met, including the mandatory Scientific faithfulness = 10 and the ≥6.5pt
minimum text size across every element in the figure.

## Open issues

None outstanding.
