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

## v3: dense landscape reconstruction (视觉参考效果图/ promoted to primary style reference)

`plot_fig4_v3.py` produces `outputs/fig4_v3.{png,pdf,svg}` using the new `_shared/style_v3.py`
module (same one fig1/fig2/fig3's v3 builds use). **Statistics unchanged again** — v3 imports
v1's `load()` verbatim and reuses the same R²/Spearman/MAE formula (coefficient of determination
on raw `q_pred`, never squared Pearson r or `q_pred_norm`).

**Layout, ground-up rebuilt:**
- Canvas: landscape 15.5×10.0in, top row ≈52% / bottom row ≈48% (was v2's near-square 14.2×12.8).
- 5-panel arrangement: top row = (a) lifecycle probability + q strip, (b) probability simplex,
  (c) q agreement; bottom row = (d) latent manifold, (e) physical wear — matching
  `视觉参考效果图/`'s spatial proportions (layout only, see below for what was and wasn't taken
  from it).
- No figure-level title anywhere — not even v2's bottom-centered "退化语义" caption. Every panel
  caption "(a)-(e) description" sits below its panel via `style_v3.panel_container()`'s nested
  `subgridspec` (geometrically locked, no `fig.text()` position guessing). No upper-left panel
  letters.
- Panel (a): switched from v1/v2's semi-opaque stacked area to three real line curves with a
  light semi-transparent fill under each — the actual (slightly noisy) trajectory is visible, not
  smoothed into an idealized shape.
- Panel (b): thicker trajectory line, larger points, explicit start (open circle)/end (filled
  square) markers, one arrow marking the time direction, horizontal colorbar — same real 304
  `(p_E,p_M,p_L)` triples as v1/v2, not reshaped.
- Panel (c): added a real binned-median trend line (20 bins along `q_true`, median `q_pred` per
  bin with ≥2 samples) alongside the hexbin — the visible saturation of `q_pred` at high
  `q_true` (plateauing ~0.7 instead of reaching 1.0) is preserved exactly, not smoothed away.
- **Panel (d) is new**: v1/v2 fig4 had no "latent manifold" panel (fig4's own input files carry no
  hidden-representation data). v1's own README anticipated exactly this situation
  ("Fig.4 若放 latent manifold, only保留一个简洁二维overview; 更系统的分析留给Fig.5"). v3 acts on
  that: it loads the real 304×64 `hidden_representation.csv` (the same file fig5 uses) and fits a
  **fresh, independent** PCA here via `data_utils.pca_2d` (numpy SVD, no sklearn) — not copied
  from fig5's own PCA run. Deliberately kept to a single simple view (stage-marker-shaped,
  q-colored points, a thin q-sorted dashed trajectory, one "increasing degradation →" arrow) so it
  doesn't duplicate fig5's fuller stage/q/uncertainty treatment.
- Panel (e): **VB axis is linear, ~70–240 μm** (real data range) — the reference mockup's own
  panel (e) uses a log axis (10¹–10⁴), which does not match this project's real, modest-range wear
  values and was not reproduced.

**Deliberately not copied from `视觉参考效果图/`**: its own R²/MAE/Spearman numbers (recomputed
live here and asserted to match, never read off the image); its lifecycle curve's exact shape;
its panel (d)'s multi-hundred/thousand-point dense cloud with 4 fictional "domain" marker shapes
(○/□/△/× for "域A/域B/域C/域D/未分类") — this project's real C6 test set is a single condition
with exactly 304 runs, so panel (d) here uses exactly 304 points, no jitter-inflated density, no
fabricated domain groups; its log-scale VB axis.

**Bugs found and fixed**: layout/caption geometry ran clean and collision-free on the first
attempt, having inherited every layout lesson from fig1_v3/fig2_v3/fig3_v3's READMEs (GridSpec
margins at construction time, `hspace` vs `caption_height` for tick-label clearance, colorbars in
their own explicit sub-row, `\n`-wrapped long captions). One content-placement issue was caught on
independent review afterward: panel (d)'s `loc="upper right"` stage legend sat directly on top of
the Early-stage point cluster in that corner. Fixed by moving it to `loc="lower right"` (with a
translucent white background for safety), which is genuinely empty in this manifold's shape.

## v4: publication-grade true-physical-size refinement

`plot_fig4_v4.py` produces `outputs/fig4_v4.{pdf,svg}`, `fig4_v4_600dpi.png`, and
`fig4_v4_paper_preview.png`, using `_shared/style_v4.py`. **Statistics unchanged a third time**
for panels (a)/(b)/(c)/(e) — v4 imports v1's `load()` and R²/Spearman/MAE formula verbatim. Full
rationale: `paper_data/figure/V4_DESIGN_AUDIT.md`. Detailed scoring: `VISUAL_QA_V4.md` (status:
**DONE**, scientific faithfulness 10/10, every text element ≥6.5pt).

**Two real content changes this round** (not just restyling — see `VISUAL_QA_V4.md`'s "Content
changes" section for full detail):
1. **Panel (d) now reads `_shared/derived/shared_pca_scores_v4.csv`** instead of fitting its own
   independent PCA. This closes a real cross-figure consistency gap: PCA sign/orientation is
   mathematically arbitrary, so Fig.4(d) and Fig.5(a)-(c) fitting PCA independently could
   legitimately come out mirrored relative to each other even though both are correct — which
   would make the same shared representation look inconsistent to a reader across the two hero
   figures. The shared file is built once by `_shared/prepare_shared_pca_v4.py`, with a
   deterministic, documented sign convention (`corr(PC1, q_true) > 0`), and is now the single
   source both figures read.
2. **Panel (b)'s simplex vertex convention changed** to Early=bottom-left/Middle=bottom-right/
   Late=top, matching `代码/7.3主实验.py::plot_probability_simplex`'s own established convention
   (confirmed by reading that file this session, per the round-4 brief's explicit instruction to
   consult the original pre-refactor plotting code before touching Fig.5-adjacent panels). v1-v3
   used a different (Early=left/Late=right/Middle=top) convention; v4 aligns with the paper's own
   prior visual language instead. Same real trajectory, only the corner labels changed.

**True-physical-size bugs found and fixed** (2, both on independent review after the initial
build — see `VISUAL_QA_V4.md`): panel (b)'s caption named its convention source directly in-figure
including a Chinese filename, which both overflowed into panel (c)'s caption at 178mm width and
triggered Times-New-Roman missing-glyph warnings (Times has no CJK coverage) — fixed by shortening
the on-canvas caption and moving the citation to this README; panel (d)'s "increasing degradation
→" annotation was visually swallowed by a dense point cluster at the manifold's vertex — fixed by
repositioning to emptier space with a white backing box.

**No significance annotation in panel (e)**: the brief requires any shown p-value to come from a
real test run this session, never a placeholder. The real gap between Early/Middle/Late VB means
(100.6/126.3/205.5 μm, non-overlapping IQRs) is visually self-evident without one, so none was
added, per the brief's own explicit "better to omit than force it" guidance for this exact case.

**Deliberately not copied from `视觉参考效果图/fig4`**: its idealized near-y=x q-agreement point
cloud; its log-scale VB axis; any of its numbers.

## Open issues

- Panel (c)'s scatter shows visible compression of `q_pred` at high `q_true` (plateauing around
  0.7 rather than reaching 1.0) — this is the real, expected pattern described in the design doc
  ("适合表述为强排序一致性 + 后期压缩, 不应写成精确VB回归"), not a plotting artifact; caption
  language should say "relative degradation ordering" rather than "precise wear regression."
- No latent-manifold panel included here (an earlier draft of the task considered adding one) —
  the design doc's actual Fig. 4-5 panel plan has exactly 4 panels (a–d) and explicitly reserves
  latent-representation analysis for Fig.5/Fig. 4-6, to avoid duplicating content across the two
  hero figures.
