# Fig.4 — Ordered degradation semantics (paper Fig. 4-5)

## Figure purpose

One of the two "hero" figures (per the design doc). Answers: does DC-PSR's output probability
evolve in an ordered way over the tool's lifecycle; does the continuous degradation position `q`
track real wear progression; and does the predicted stage correspond to real physical wear? The
four panels are designed as **one C6 lifecycle projected into four spaces** (time, probability
simplex, q-agreement, physical wear), not four independent plots, per
`DCPSR_Chapter4_CN_Detailed.docx` §4.5.

## Input files

- `paper_data/07_figure_ready/fig5/lifecycle_semantics.csv` (304 rows) — per-run `VB_true`,
  `q_true`, `q_pred`, `prob_early/middle/late`, `relative_life`, `pred_stage`. Drives panels (a)
  and (d).
- `paper_data/07_figure_ready/fig5/simplex_trajectory.csv` (304 rows) — per-run
  `prob_early/middle/late` + `relative_life`, drives panel (b)'s ternary-coordinate trajectory.
- `paper_data/07_figure_ready/fig5/q_agreement.csv` (304 rows) — `q_true` vs **raw** `q_pred`,
  explicitly tagged `q_comparison_definition == "q_true_vs_raw_q_pred_no_renormalization"`
  (asserted in the script). Drives panel (c).
- `paper_data/07_figure_ready/fig5/wear_by_predicted_stage.csv` (3 rows) — aggregate VB mean/median
  by predicted stage, read only to cross-check the per-run recomputation in panel (d), never
  plotted directly.

`q_pred_normalized_display.csv` was inspected but **not used** — `Q_DEFINITIONS.md` explicitly
marks it `display_only_not_q_agreement_metrics`, so using it for panel (c)'s R²/ρ/MAE would
misrepresent the model's actual agreement statistic.

See `inputs_manifest.csv` for row/column counts and SHA-256 of each file as read.

### VB unit: micrometers (μm)

`00_metadata/Q_DEFINITIONS.md` itself does not state a unit ("observed flank-wear value ... in the
source wear unit"). Resolved from `DCPSR_Chapter4_CN_Detailed.docx`, which states VB in "μm" and
quotes group means of 100.55/126.29/205.46 μm — these match this project's
`wear_by_predicted_stage.csv` exactly, confirming μm (not mm, which the original placeholder
figures incorrectly used).

## Plot script

`plot_fig4.py` — run with:

```
python paper_data/figure/fig4/plot_fig4.py
```

Panels:
- (a) Full C6 lifecycle: stacked probability area (p(Early)/p(Middle)/p(Late)) over relative life,
  with a shared-x sub-panel below showing `q_true` (black) vs raw `q_pred` (red).
- (b) Probability-simplex trajectory: (p_E, p_M, p_L) mapped to 2D ternary coordinates, colored
  continuously by relative life — shows the geometric Early→Middle→Late path directly.
- (c) `q_true` vs raw `q_pred` hexbin density with y=x reference and a stat box.
- (d) Violin + box + jittered points of `VB_true` grouped by **predicted** stage — the physical
  anchor. Group means annotated and cross-validated against `wear_by_predicted_stage.csv`.

### q-agreement formula (important, and easy to get wrong)

`R²` is the standard coefficient of determination `1 − SS_res/SS_tot` computed on **raw** `q_pred`
as-is (no refit regression line, no renormalization) — this is what `Q_DEFINITIONS.md` mandates
and it is **not the same number** as squared Pearson correlation: on this data, coefficient of
determination = 0.7478 but squared Pearson r = 0.8813. The higher number would be wrong to report.
See `_shared/data_utils.py::r2_coefficient_of_determination` and
`paper_data/figure/FIGURE_PROGRESS.md` §3 for the verification that caught this.

## Outputs

- `outputs/fig4_main.png` / `.pdf` / `.svg`

## Validation (see `logs/validation.txt`)

- All 3 core input files have exactly 304 rows.
- q agreement: R²=0.7478 (≈0.748), Spearman ρ=0.9635 (≈0.963), MAE=0.1132 (≈0.113) — all match the
  design doc's stated values.
- Panel (d): recomputed per-predicted-stage `VB_true` mean/median from `lifecycle_semantics.csv`
  exactly match `wear_by_predicted_stage.csv`'s aggregate for all 3 stages; means match the design
  doc's 100.55/126.29/205.46 μm; Late/Early ratio = 2.043 (≈2.04, "physical monotonicity").

## v2: reference-style visual reconstruction

`plot_fig4_v2.py` produces `outputs/fig4_v2_reference_style.{png,pdf,svg}`. **Statistics are
unchanged from v1** — v2 reuses v1's `load()` function and re-runs the exact same R²/Spearman/MAE
formula and VB-mean/median cross-check (copied, not altered) so the numbers are guaranteed
identical; only the visualization layer changed. Style reference:
`reference/reference_mockup.png` (`figures/fig5_semantics_refined/fig5_semantics_refined.png`,
panels a/b/c/e only — see `reference/SOURCE.md`).

**Layout changes vs. v1:**
- No top figure-level title; figure-level caption "退化语义" + English subtitle centered at the
  bottom (`figure_caption`).
- Panel captions moved below each panel; small bold `(a)`–`(d)` letters kept in-panel.
- Panel (a): added shaded Early/Middle/Late background zones with dashed boundary lines and
  in-panel zone labels (learned from the reference's zone-shading style — computed from the real
  `true_stage` transitions in `lifecycle_semantics.csv`, not hand-placed).
- Panel (b): added open-circle "start" / filled-square "end" endpoint markers and a horizontal
  colorbar for relative life, matching the reference's simplex styling.
- Panel (c): switched to a `bone_r` hexbin on a log color scale plus an added **binned-median
  trend line** (20 bins along q_true, median of q_pred per bin, only for bins with ≥2 samples) —
  this line is purely a visual aid computed from the real per-run pairs, it does not change the
  reported R²/ρ/MAE which are still computed on all 304 raw pairs.
- Panel (d): added a dashed connector line between the three stages' VB medians, matching the
  reference's "physical monotonicity" visual thread.
- Colors switched to the navy/teal/gold `STAGE_COLORS` / `DEGRADATION_CMAP` from `style_v2.py`.

**Deliberately not copied from the reference mockup:** its panel (d) (shared latent PCA) — that
belongs to fig5's subject matter, not fig4's, and is deliberately excluded here to avoid
duplicating fig5's content (see `reference/SOURCE.md`); any of its R²/ρ/MAE/VB numbers (recomputed
independently in v2 exactly as in v1, and they are asserted to match, but never read off the
image).

**Bugs found and fixed while building this** (same two failure modes as fig1_v2, now systematic
across all v2 scripts): (1) `left`/`right`/`top`/`bottom` must be set on the `GridSpec`
constructor, never via a later `subplots_adjust()` call, or captions detach from their axes; (2)
the last GridSpec row's panel caption needs enough bottom margin to clear the figure-level caption
block below it — this figure's 2-line figure caption (bold CJK title + English subtitle) needed
`bottom=0.165`, larger than fig1's `0.155`. Also fixed a same-corner collision between panel (c)'s
`(c)` letter and its R²/ρ/MAE stat box by moving the stat box down from y=0.97 to y=0.88 in axes
fraction.

**Note on a second, later-arriving reference set**: after this v2 build was finished, a folder
`视觉参考效果图/` appeared in every `figX/` directory (AI-generated dashboard-style mockups, bright
saturated palette, top banner title, icon badges, highlighted conclusion boxes; its fig4 copy also
uses full 3D `plot_surface`s and shows visibly more than 304 points despite its own caption stating
n=304 — another sign it is illustrative, not literal). Asked the user directly whether to rework
all 5 figures to match its brighter dashboard aesthetic; they confirmed keeping the current
academic-journal style. No changes made as a result.

## Open issues

- Panel (c)'s scatter shows visible compression of `q_pred` at high `q_true` (plateauing around
  0.7 rather than reaching 1.0) — this is the real, expected pattern described in the design doc
  ("适合表述为强排序一致性 + 后期压缩, 不应写成精确VB回归"), not a plotting artifact; caption
  language should say "relative degradation ordering" rather than "precise wear regression."
- No latent-manifold panel included here (an earlier draft of the task considered adding one) —
  the design doc's actual Fig. 4-5 panel plan has exactly 4 panels (a–d) and explicitly reserves
  latent-representation analysis for Fig.5/Fig. 4-6, to avoid duplicating content across the two
  hero figures.
