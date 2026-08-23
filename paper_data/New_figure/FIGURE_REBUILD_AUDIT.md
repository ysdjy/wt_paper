# Figure Rebuild Audit — `paper_data/New_figure/`

Status: **pre-rendering audit**. No plotting has started. This document must be reviewed/approved
before any script writes a pixel.

## 0. Why this document exists, and what supersedes what

Three prior artifacts already describe this chapter's figures, and they now disagree with each
other in one specific way:

1. **`paper_data/DCPSR_Chapter4_CN_Detailed.docx`** ("方案A") — the most detailed prior plan.
   Specifies **1 design figure + 5 result figures**: 图4-1 (design, already done, out of scope
   here), 图4-2 (主比较), 图4-3 (稳健性/泛化), 图4-4 (消融机制), 图4-5 (退化语义, 4 panels: lifecycle
   probability, simplex, q-agreement, VB), 图4-6 (表示几何, 5 panels: PCA×3 colorings, 2×3D surfaces)
   — 图4-5 and 图4-6 are **separate** figures in this plan.
2. **`paper_data/figure/fig1..fig5/`** (v1→v4/v5 rounds) — the actual prior implementation of
   方案A's 图4-2 through 图4-6, already built, QA'd (10/10 scientific faithfulness each), using
   real frozen data. `fig4`=退化语义(图4-5), `fig5`=表示几何(图4-6), kept separate, matching the docx.
3. **This session's explicit user instruction** (current task) — asks for **4 result figures**,
   not 5: Fig4_2_主比较, Fig4_3_鲁棒性, Fig4_4_消融实验, and **Fig4_5_退化语义与表示几何**, the last of
   which *merges* what the docx and the old `fig4`/`fig5` treat as two separate hero figures into
   one. The user was explicit that this merge is deliberate ("NOT a simple merge of the old
   layouts... rebuilt according to the new plan") and supersedes both the docx's 方案A figure count
   and the old fig4/fig5 visual layouts.

**Resolution applied throughout this document**: (3) governs the final figure count, naming, and
composition target. (1) and (2) are used as the *panel-content and data-source reference* — every
panel the docx specified for 图4-2/图4-3/图4-4/图4-5/图4-6 is accounted for somewhere in the four new
figures below (nothing scientifically silently dropped), except where explicitly flagged in each
figure's §7 as newly out of scope for this round.

## 1. Reuse policy (applies to all four figures)

**Reuse verbatim (scientific computation only, never hardcoded legacy data):**
- `paper_data/figure/_shared/data_utils.py` — `confusion_counts`, `precision_recall_f1_per_class`,
  `accuracy`, `macro_f1`, `r2_coefficient_of_determination` (verified: coefficient of
  determination `1-SS_res/SS_tot` on **raw** `q_pred`, NOT squared Pearson r — the docx's
  R²≈0.748 is this formula; squared Pearson r gives 0.881, wrong), `pca_2d` (numpy SVD, no
  sklearn), `ternary_coords`.
- `paper_data/figure/_shared/prepare_shared_pca_v4.py` → `derived/shared_pca_scores_v4.csv` — the
  ONE deterministic-sign-convention PCA fit on the 304×64 hidden representation (`corr(PC1,
  q_true) > 0`). Must be read directly, never refit, so Fig4_5's PCA panels stay internally
  consistent.
- Frozen bootstrap CIs already computed and stored in `07_figure_ready/fig1/D1_main_metrics.csv`
  / `B11_B12_controlled_comparison.csv` — no bootstrap is recomputed live in any plot script, old
  or new.
- Sample-level prediction parsing pattern from `paper_data/figure/fig1/plot_fig1.py::load_predictions()`
  (reads `01_PHM2010/.../predictions_common_universe/D1_<method>_304runs.csv`, asserts 304 rows).
- Metric-direction dictionary `METRIC_DIRECTION` (`style_v2.py`, re-exported by `style_v3`/`style_v4`).

**Reuse as visual/layout framework (from `代码/` — the original manuscript's own plotting code),
never its hardcoded old-B1–B12/old-A1–A6 data:**
- Signature convention found consistently across `8.2图8/9/10/11/12/13/14/15/16/17/18.py`: open
  "arrow-tipped" axes replacing spines (`add_axis_arrows`/`style_axis`), dashed y-gridlines only,
  Times New Roman + STIX mathtext, white-fill/colored-hatch bars instead of solid fills,
  `emphasize_b12`-style bolding of the proposed method. This is the strongest, most consistent
  "this is the manuscript's own house style" signal found in the whole `代码/` audit — recommended
  as the shared visual language for all 4 new figures, replacing the previous rounds'
  independently-invented "dense-landscape v3/v4" AI-driven style.
- Per-figure specific devices are listed in each figure's §4 below.

**Do not reuse:** any hardcoded data table inside a `代码/*.py` script (old 12-baseline B1–B12
scheme, stale A1–A6 numbers, stale q-agreement statistics) — all superseded by the 9-method frozen
scheme. Do not reuse `paper_data/figure/fig1..fig5`'s v2/v3/v4 *layout/composition* decisions
wholesale — those are explicitly demoted to "data-pipeline reference only" per the user's
instruction this round.

## 2. Global scientific/naming conventions (carried over from prior audits, still binding)

- 9 methods: RF, TCN-GRU, Multi-task TCN-GRU, DC-PSR (proposed), HTT-Net (adapted), Multi-source
  Attention, MTF-AViTK, Dynamic GIN + TGP, DP2Net-adapted. B11/B12 = internal shorthand for
  Multi-task TCN-GRU/DC-PSR only inside cross-dataset-derived tables.
- Stage colors: Early `#2F6FB3`, Middle `#2E8B57`, Late `#E76F51` (keep — already validated
  across 5 prior figures, and the docx independently converges on "Early蓝/Middle青金/Late橙红").
- VB unit: **μm** (confirmed, `Q_DEFINITIONS.md` + docx cross-check, means 100.55/126.29/205.46).
- `q_pred` (raw) is the only field paired with `q_true` for agreement stats; `q_pred_norm` is
  display-only, never used for R²/ρ/MAE.
- Higher-better: Acc, Macro-F1, E/M/L-F1, M-Pre, M-Rec. Lower-better: M→E, M→L, Rev, Jump, Smooth.
  Any "benefit"/direction-unified score used for color must show the raw value alongside it.
- Third-dataset name: MTW-CM ("Multivariate time series data of milling processes with varying
  tool wear and machine tools", Mendeley). Never "MIMII".

---

## Fig4_2_主比较

### 1. Required scientific question
On PHM2010 core task D1 (C1+C4→C6, n=304): how do all 9 methods compare jointly on classification
and consistency; where does DC-PSR sit relative to its backbone (Multi-task TCN-GRU) on the
accuracy–consistency trade-off; what do representative confusion patterns and middle-stage/
transition diagnostics look like. Headline (already verified against frozen CSVs): DC-PSR is not
the top classifier (Multi-task TCN-GRU leads by 0.3–0.4pp on Acc/Macro-F1/M-F1), but has the
lowest Smooth (0.01876, −20.5% vs backbone) with Rev=Jump=M→L=0.

### 2. Final panel list (5 panels, superseding docx's a/b/c-only sketch by folding in the
manuscript's own Fig.9/Fig.10 content that the docx's later "附录B" data index also references)
- (a) 9-method × 12-metric normalized performance landscape (direction-corrected color, raw value
  always shown).
- (b) Accuracy vs Smooth Pareto/scatter, DC-PSR & Multi-task TCN-GRU emphasized.
- (c) Bootstrap 95% CI strips, Acc/Macro-F1/M-F1, representative methods only.
- (d) Confusion matrices, representative methods (RF, MTF-AViTK, Multi-task TCN-GRU, DC-PSR),
  row-normalized + count.
- (e) Middle-stage & consistency triptych: M-Pre/M-Rec, M→E/M→L, Rev/Jump+Smooth — this is a
  direct rebuild of manuscript Fig.10, restricted to the 9-method roster.

### 3. Current frozen data source per panel
- (a): `07_figure_ready/fig1/D1_main_metrics.csv` (9-method point estimates) merged with D1 rows
  of `07_figure_ready/fig2/taskwise_absolute.csv` (adds E_F1/L_F1/M_Precision; cross-checked
  byte-identical M_F1/M_Rec between the two files).
- (b): `07_figure_ready/fig1/accuracy_consistency_points.csv` + `D1_main_metrics.csv`.
- (c): `07_figure_ready/fig1/D1_main_metrics.csv` CI columns, `B11_B12_controlled_comparison.csv`
  for the paired Multi-task-TCN-GRU/DC-PSR CI preferentially.
- (d)/(e): `01_PHM2010/01_main_D1/predictions_common_universe/D1_{rf,mtf_avitk,multitask_tcn_gru,
  dc_psr}_304runs.csv` — sample-level `true_stage`/`pred_stage`, confusion matrices and M-Pre/
  M-Rec/M→E/M→L/Rev/Jump/Smooth all recomputed from these labels, never hand-entered.

### 4. Original manuscript figure/code reusable
- `代码/8.2图10.py` — **is** manuscript Fig.10: hatched-white-bar + arrow-axis triptych
  (M-Pre/M-Rec/M-F1 | M→E/M→L | Rev/Jump-bars+Smooth-line with proposed-method highlight band).
  Direct template for panel (e).
- `代码/8.2图9.py` — **is** manuscript Fig.9: small-multiple confusion matrices, custom
  white→cyan→blue→purple→red diverging colormap (`CMAP_ORIGINAL_LIKE`), dual count+row-norm cell
  annotation, shared external colorbar. Direct template for panel (d); `draw_confusion_matrix()`
  is portable as-is (swap in real 9-method matrices).
- `代码/8.2图8.py` — manuscript Fig.8's multi-line "profile" chart with arrow-axis + per-method
  fixed color/marker/linestyle and B11/B12 emphasis (`add_axis_arrows`, `style_axis`). Style
  reference for panel (a)'s axis treatment and for consistent method-color/marker legend reused
  across (a)/(b)/(c).
- `代码/7.4对比实验.py` — `emphasize_b12()` (bold/red proposed-method tick label), axvspan
  true-stage background device — reusable highlight conventions, not its B1–B12 data.

### 5. Previous `paper_data/figure` code reusable for data calculation only
- `fig1/plot_fig1.py`: `load()`, `build_heatmap_table()`, `validate_headline()`,
  `load_predictions()` — the merge/validation logic for panel (a)/(d)/(e), byte-verified against
  10 headline numbers via `np.isclose`. Port these functions; discard `plot_fig1_v2/v3/v4.py`'s
  layout code.
- `_shared/data_utils.py::confusion_counts` for panel (d)/(e).

### 6. Parts that must be newly designed
- Whole-figure composition and axis styling: replace the v4 "dense-landscape, true-physical-size"
  AI-driven layout with the arrow-axis/hatched-bar manuscript-native style from 8.2图8/9/10,
  applied consistently across all 5 panels (panels a/b/c did not have this style in any prior
  round — new work).
- Panel (a)'s heatmap and panel (b)'s Pareto scatter have no direct 代码/ ancestor at the 9-method
  scale (原 Fig.8 was a profile-line chart, not a heatmap) — must be newly composed, but staying
  within the arrow-axis/muted-hatch visual language rather than re-inventing a new aesthetic.
- Merging (a)/(b)/(c) [regular, "reviewer-friendly" per docx] with (d)/(e) [Fig.9/10-style] into
  one coherently-styled composite is new integration work — no prior figure (old or docx) combined
  all five into one canvas.

### 7. Panels that cannot be supported by current data
- None identified. All five panels have complete, verified frozen-data backing.

---

## Fig4_3_鲁棒性

### 1. Required scientific question
Does DC-PSR's advantage generalize across target-condition difficulty (D1/D2/D3 on PHM2010) and
across datasets (NASA Milling, MTW-CM)? Headline: no single method wins every target condition
(target-condition dependence is real); B11→B12 trades a small classification delta for
consistently improved M-F1/Smooth/Jump direction on NASA and MTW-CM, though absolute Acc is
dataset-dependent and is deliberately not used as a cross-dataset headline (per docx §4.3 policy).

### 2. Final panel list (3 core + 1 optional inset, per docx's own explicit "reviewer-friendly,
matrix/heatmap language, do not overcomplicate" instruction for this figure)
- (a) D1/D2/D3 × 9-method within-task-normalized heatmap / rank matrix.
- (b) Multi-task TCN-GRU → DC-PSR paired-delta (dumbbell/slope) for Acc, M-F1, M-Rec, Smooth
  across D1/D2/D3.
- (c) Cross-dataset delta matrix: PHM2010/NASA/MTW-CM, ΔAcc/ΔM-F1/Smooth-benefit/Jump-benefit only
  (never a mixed absolute-Acc headline).
- (d) *Optional, space-permitting*: one compact confusion-matrix row (D1/D2/D3, DC-PSR only) using
  8.2图11's diverging-colormap style, to give the "stable stage boundaries under cross-condition"
  visual claim (manuscript Fig.11) a literal presence, not just table-derived heatmap cells.

### 3. Current frozen data source per panel
- (a): `07_figure_ready/fig2/taskwise_normalized.csv`, `taskwise_rank.csv`.
- (b): `07_figure_ready/fig2/taskwise_absolute.csv` (Multi-task TCN-GRU and DC-PSR rows only,
  D1/D2/D3).
- (c): `07_figure_ready/fig3/cross_dataset_deltas.csv` (primary), `cross_dataset_absolute.csv`,
  `cross_machine_task_deltas.csv`, `D2M_failure_distribution.csv` (supplementary/footnote use).
- (d), if included: `01_PHM2010/02_cross_condition_D1_D2_D3/predictions/D2/`,
  `/D3/` sample-level files for DC-PSR (need to confirm exact filenames at build time — flagged
  below).

### 4. Original manuscript figure/code reusable
- `代码/8.2图11.py` — **is** manuscript Fig.11: 1×4 confusion-matrix row (D1/D2/S1/S2 in the old
  scheme), shared diverging colormap, dual count/row-norm annotation, single shared colorbar.
  `draw_confusion_matrix()` directly portable for optional panel (d), restricted to D1/D2/D3 (this
  project's frozen tasks; S1/S2 are not part of current frozen scope — see §7).
- `代码/8.2图13.py` — mean±std dot/errorbar plot with arrow-axis + dual-source/single-source color
  coding — style reference for panel (b)'s dumbbell/slope treatment (axis convention, not literal
  chart type, since paired-delta reads better as a slope chart than mean±std dots here).
- `代码/8.2图12.py` — life-cycle stage-background-shading device (`stage_segments`/
  `add_stage_background`) — available if a probability-evolution inset is later wanted, not
  required for the core 3-panel composite (docx explicitly assigns lifecycle-probability-evolution
  content to Fig4_5, not Fig4_3 — kept out here to avoid duplicating that story).
- `代码/8.2图14.py` / `代码/8.2图11补充.py` — clipped-radius radar comparing tasks/datasets —
  considered and **not** selected as a core panel (docx explicitly restricts this figure to
  "matrix/heatmap language"); noted as a fallback if panel (c)'s delta matrix reads as too sparse
  once real numbers are plotted.

### 5. Previous `paper_data/figure` code reusable for data calculation only
- `fig2/plot_fig2_v4.py`'s taskwise merge/load logic (panel a/b data assembly).
- `fig3/plot_fig3_v4.py`'s cross-dataset delta load/validation logic (panel c), including the
  existing sign-correction for `Smooth_benefit`/`Jump_benefit` already baked into
  `cross_dataset_deltas.csv` — do not re-derive signs, just load.

### 6. Parts that must be newly designed
- Panel (b)'s specific dumbbell/slope visual — no direct 代码/ ancestor at this exact
  paired-delta framing; must be newly composed using the arrow-axis style.
- Whole-composite layout (a top matrix + b/c bottom pair, per docx sketch) restyled in the
  manuscript-native arrow-axis/muted palette instead of old fig2/fig3 v4's dense-landscape design.
- Decision on whether panel (d) (confusion-matrix inset) is included — recommend confirming with
  user before implementation given docx's explicit "keep this figure regular" instruction; noted
  as an open design choice, not decided unilaterally here.

### 7. Panels that cannot be supported by current data
- **S1/S2 PHM sub-tasks**: manuscript Table 9 mentions S1/S2 single-source transfer tasks
  alongside D1/D2, but the docx's own data description (§4.1.1, 附录B) and the frozen
  `07_figure_ready/fig2/*.csv` files only cover D1/D2/D3. Confirmed: **S1/S2 are out of the
  current frozen scope** — do not attempt to plot them; this matches the docx's own scope, not a
  new gap introduced here.
- **Panel (d) confusion-matrix inset (if pursued)**: exact per-task DC-PSR sample-level prediction
  file paths for D2/D3 were located as directories
  (`01_PHM2010/02_cross_condition_D1_D2_D3/predictions/{D2,D3}/`) but individual filenames were
  not yet enumerated in this audit pass — must be verified at build time before panel (d) is
  committed to the final panel list.

---

## Fig4_4_消融实验

### 1. Required scientific question
What does each module (fine-state assistance A2, degradation-position prior A3, weighted mix A4,
ordered filtering A5, final fusion A6) actually change, relative to the raw stage head A1 —
particularly on *probability-state formation*, not just final hard-classification numbers.
Headline: A1–A4 have byte-identical hard classification (Acc/Macro-F1/M-F1/M-Rec) — the gains from
A2–A4 are entirely in probability-distribution shape (Smooth improves 11–16%), invisible to argmax
metrics. A5 pushes Smooth to the best value (−42.4% vs A1) at a real Acc/M-F1/M-Rec cost. A6
recovers most of that classification loss while keeping Smooth −20.5% vs A1.

### 2. Final panel list (one shared A1→A6 x-axis, 3 bands, per docx's explicit instruction not to
rebuild this as "4 independent panels stitched together")
- Band 1 (top): Acc/Macro-F1/M-F1 across A1–A6, thin-bar/point-line mix, annotated where values
  are identical across configs (A1–A4).
- Band 2 (middle): M-Rec/M→E/M→L/Smooth across A1–A6, small heatmap-strip or twin-axis
  bar+line — direction-unified visual language, consistent with Fig4_2's panel (e) idiom.
- Band 3 (bottom, the "probability-state formation" emphasis the user asked for): per-lifecycle
  local probability variation + cumulative variation curves for A1–A6 (color ramp light-gray→theme
  color), **plus** a small side-by-side stage-background-shaded E/M/L probability-trajectory
  comparison for 2–4 representative configs (at minimum A1-raw vs A6-final; A4/A5 optional if
  space allows) — this is the literal "probability-state formation" visual, built from the
  original code's per-config trajectory idiom, not present in any prior round's ablation figure.
- Small inset: accuracy–smoothness trade-off scatter with contour background and A1→A6 dashed
  path (manuscript Fig.16) — placed as a compact corner inset rather than a full separate panel,
  to keep the single-shared-x-axis narrative dominant per docx's instruction.

### 3. Current frozen data source per panel
- Band 1/2: `07_figure_ready/fig4/A1_A6_absolute.csv` (authoritative), `A1_A6_delta_vs_A1.csv`
  (for annotated deltas, e.g. "A5 Smooth −42.4%", "A6 Acc +0.99pp vs A5").
- Band 3: `07_figure_ready/fig4/A1_A6_lifecycle_variation.csv`, `A1_A6_cumulative_variation.csv`
  (1824 rows = 6 configs × 304 runs each), `A1_A6_probability_trajectories.csv` (per-run p_E/p_M/
  p_L per config, for the representative-config trajectory comparison).
- Trade-off inset: `A1_A6_absolute.csv` (Acc or Macro-F1 vs Smooth, 6 points A1–A6).

### 4. Original manuscript figure/code reusable
- `代码/8.2图15.py` — **is** manuscript Fig.15: grouped bars (Acc/Macro-F1/E-F1/M-F1/L-F1) + twin-
  axis Smooth line + true-stage-probability boxplot overlay per A-column, reading real per-run
  probabilities. Direct backbone for Band 1 (richer than the summary-only bar approach used in
  prior AI-driven rounds).
- `代码/8.2图16.py` — **is** manuscript Fig.16: accuracy-smoothness trade-off scatter with soft
  contourf background scored by trade-off, dashed A1→A6 path, per-point annotations ("highest
  Macro-F1"/"lowest Smooth"/"balanced trade-off"). Direct template for the trade-off inset.
- `代码/7.6消融实验.py::plot_fig13_probability_evolution` — 2×2 grid of per-run E/M/L probability
  curves with true-stage background shading (`add_stage_background`) for representative configs
  (A1/A4/A5/A6 in the legacy version). **This is exactly the "probability-state formation" panel**
  requested — reuse its structure, restyle axis subset to whichever 2–4 configs are chosen, feed
  current frozen `A1_A6_probability_trajectories.csv`.
- `代码/7.6消融实验.py::add_a6_band` — highlight-final-config device, reusable for Band 1/2.
- `代码/8.2图12.py` / `7.6消融实验.py`'s `stage_segments`/`add_stage_background` — shared
  life-cycle shading helper, should be centralized once and reused by Fig4_3(d-optional), Fig4_4
  (Band 3), and Fig4_5 (lifecycle panel) for visual consistency across the whole New_figure set.

### 5. Previous `paper_data/figure` code reusable for data calculation only
- `fig3/plot_fig3_v4.py`'s A1–A6 load/merge/validation logic (the v4 round's real structural fix —
  panel (d) stopped wasting space on all-zero Rev/Jump bars and switched to
  `lifecycle_variation`/`cumulative_variation` content — that data-selection decision is scientific,
  not stylistic, and should carry forward unchanged into Band 3).
- `_shared/data_utils.py` metric functions if any per-run classwise recomputation is needed to
  cross-validate `A1_A6_absolute.csv` against `A1_A6_probability_trajectories.csv` (medium-risk
  item flagged in the original fig3 precheck — worth re-running that cross-check here too).

### 6. Parts that must be newly designed
- The single-shared-x-axis 3-band composite structure itself — no prior round (old fig3, or any
  代码/ script) laid out A1–A6 as one continuous horizontal narrative with 3 stacked bands; this is
  new integration work combining Fig.15+Fig.16+the trajectory-evolution idiom into one figure.
- The representative-config subset choice for the Band-3 trajectory comparison (which of
  A1/A2/A3/A4/A5/A6 to show side-by-side, given 6 would be visually dense) — recommend A1
  (raw baseline) vs A5 (max-smoothing extreme) vs A6 (final) as the minimum informative set,
  matching the docx's own narrative ("A5 over-smooths, A6 balances") — open to user confirmation.

### 7. Panels that cannot be supported by current data
- None identified. All required CSVs exist and were precheck-verified in the prior round
  (`FIGURE_PROGRESS.md` §2 table, fig3/fig4 rows).

---

## Fig4_5_退化语义与表示几何 (merged — the figure requiring the most new design work)

### 1. Required scientific question
Two questions folded into one coherent lifecycle story, per the user's explicit merge instruction:
(i) does DC-PSR's output evolve in an ordered, physically-meaningful way (probability trajectory,
continuous position `q`, real wear VB)? (ii) does the shared 64-D internal representation actually
encode continuous degradation structure, consistent with (i), rather than three disconnected
clusters? Headline: probability trajectory is ordered (Rev=Jump=0 on D1/C6); q_true vs raw q_pred
R²≈0.748 (coefficient of determination, not squared Pearson r — see §1 formula note), Spearman
ρ≈0.963, MAE≈0.113; VB means increase monotonically Early→Middle→Late (100.55/126.29/205.46 μm,
Late≈2.04× Early); the shared representation forms one continuous curved manifold (not 3 clusters),
with q-color varying continuously along it and uncertainty concentrated near stage boundaries.

### 2. Final panel list (6 core panels + 1 conditional; deliberately narrower than the docx's
combined 9-panel 图4-5+图4-6 sketch — see rationale below)
- (a) Shared hidden-representation PCA, colored by true stage, with a binned lifecycle-path arrow
  overlay (Early→Middle→Late centroid path) — **the Fig.17 ingredient**, single-condition (C6)
  version of `8.2图18.py`'s hidden-row.
- (b) Same PCA coordinates, colored continuously by `q_true` — same layout, only color changes
  (must reuse the exact same `(PC1,PC2)` as (a), never refit).
- (c) Same PCA coordinates, colored by `uncertainty`, misclassified samples ring-marked.
- (d) Full C6 lifecycle: stacked/line probability trajectory (p_Early/p_Middle/p_Late) over
  relative life, stage-shaded background, with `q_true`/raw-`q_pred` dual-line sub-band —
  **the "lifecycle probability / q evidence" ingredient**.
- (e) `q_true` vs raw `q_pred` scatter/hexbin with y=x reference and stat box (R²/ρ/MAE) —
  **the "q agreement" ingredient**.
- (f) VB-by-predicted-stage physical anchor: violin/box + dual-axis bar(q_pred)+line(VB mean) —
  **the "physical wear semantics" ingredient**.
- (g) *Conditional, corner inset only*: one 3D stage-probability surface (from `代码/8.2图17.py`'s
  refined version) — **the "Fig.18 probability-surface" ingredient the user explicitly asked to
  integrate**. Must carry an explicit caption disclosure that it is a visual/illustrative
  interpolation across only 304 discrete real observations, not a new quantitative claim or a
  fitted/measured density — matching the honesty standard already set in old `fig5`'s v3/v4 README
  ("ridge-lines/trajectories, not an interpolated surface... a literal continuous surface would
  require inventing values... not scientifically justified"). Include only if panel (g) can be
  sized as a true corner supplement without crowding (a)–(f); if it cannot, drop it and rely on
  panel (d)'s 2D trajectory to carry the "joint evolution" claim, which the manuscript text itself
  says is sufficient ("该三维视图不作为新的定量指标").

**Deliberately dropped vs. the docx's fuller 9-panel sketch**: the probability-simplex ternary
trajectory (old 图4-5(b) / old `fig4` panel b) and the 3D confidence-over-q surface (old 图4-6(e)).
Rationale: panels (a)–(c) already give a geometric reading of stage separation via PCA (the
simplex would be a second, largely redundant geometric view of the same ordering claim), and a
second 3D surface would push this already-dense merged figure past a coherent single-canvas budget.
This is a scope decision, not a data gap — **flagged here explicitly for user confirmation before
build**, since the user's brief listed simplex/second-surface as part of "old fig4+fig5" content
without saying whether both must survive the merge.

### 3. Current frozen data source per panel
- (a)/(b)/(c): `paper_data/figure/_shared/derived/shared_pca_scores_v4.csv` (PC1/PC2 + true_stage/
  pred_stage/q_true/q_hat/uncertainty/entropy/misclassified — already deterministic-sign-fixed,
  reuse directly, do not refit) **or**, if that derived file is judged stale/not to be carried
  forward under the "old figure code = data-pipeline reference only" policy, regenerate identically
  from `07_figure_ready/fig5/hidden_representation.csv` via `data_utils.pca_2d` — same numbers
  either way since it's a pure function of the same frozen 304×64 matrix; recommend reusing the
  existing derived CSV rather than paying for a redundant refit.
- (d): `07_figure_ready/fig5/lifecycle_semantics.csv` (304 rows: VB_true, q_true, q_pred, prob_
  early/middle/late, relative_life, pred_stage).
- (e): `07_figure_ready/fig5/q_agreement.csv` (304 rows, raw q_pred vs q_true, tagged
  `q_comparison_definition == "q_true_vs_raw_q_pred_no_renormalization"`).
- (f): `07_figure_ready/fig5/wear_by_predicted_stage.csv` (3-row aggregate, cross-check only) +
  per-run `VB_true`/`pred_stage` from `lifecycle_semantics.csv` for the actual violin/points.
- (g), if included: `07_figure_ready/fig5/lifecycle_semantics.csv` (same source as (d), re-shaped
  into an E/M/L × relative-life grid for the 3D surface — no new data file needed).

### 4. Original manuscript figure/code reusable
- `代码/8.2图18.py` (misnamed in the repo — actually the final, most-refined PCA figure,
  `Fig5_repr_main_misclassified_v2`) — 2×3 grid, custom vivid-but-muted `Q_CMAP`/`U_CMAP`,
  misclassified open-ring overlay, per-row shared axis limits, external colorbars, lifecycle-path
  arrow on the hidden-representation row only. **Primary template for panels (a)/(b)/(c)** — almost
  certainly closest to the actual submitted manuscript Fig.17.
- `代码/8.1.2共享表征图.py::add_lifecycle_path()` — bins q, connects centroid path with arrow;
  directly portable for (a).
- `代码/7.9磨损估计.py` — `q_metrics()` (MAE/RMSE/R²/Spearman/Pearson), its fig17 (2-panel prob-
  lines + q dual-line, stage-shaded — template for (d)), its fig19 (q_true-vs-q_pred scatter +
  stats textbox + diagonal, stage-colored points — template for (e)), its fig23 (dual-axis
  bar(q_pred)+line(VB mean) by stage — template for (f)), `add_stage_background()`.
- `代码/7.9.1磨损估计可视化.py`'s Fig24 (2-panel lifecycle with `fill_between` gap) — alternate/
  supplementary template for (d) if fig17's version reads too sparse.
- `代码/8.2图17.py` — polished final 3D stage-probability-surface + confidence-surface 2-panel,
  shared colorbar — template for optional panel (g), **only the stage-probability half**, not the
  confidence-over-q half (dropped per §2 scope decision above).

### 5. Previous `paper_data/figure` code reusable for data calculation only
- `_shared/prepare_shared_pca_v4.py` — the deterministic PCA fit + sign convention (see §3).
- `_shared/data_utils.py::r2_coefficient_of_determination` — critical, easy to get wrong (verified
  0.7478 vs the incorrect squared-Pearson 0.8813 on this exact file).
- Old `fig4/plot_fig4.py`'s q-agreement stat-box computation and VB-violin per-run grouping logic
  (panel (e)/(f) numeric assembly), old `fig5/plot_fig5_v4.py`'s (or v5, if superior — check both
  before build) PCA-coordinate loading pattern for (a)/(b)/(c).

### 6. Parts that must be newly designed
- The entire 6(+1)-panel single-canvas composition — no prior artifact (old fig4, old fig5, or any
  代码/ script) combines representation-geometry panels with lifecycle/q/VB panels in one figure;
  this is the genuinely new integration work the user asked for.
- Visual style: switch from old fig5 v3/v4/v5's MATLAB-rendered ridge/ribbon-curtain 3D aesthetic
  to the `8.2图18.py`/`8.2图17.py` Python arrow-axis + `Q_CMAP`/`U_CMAP` aesthetic, for consistency
  with the other 3 new figures' shared visual language (§1).
- Shared color/marker/lifecycle-path conventions must be identical across panels (a)–(c) and
  visually continuous into (d)/(e)/(f) (e.g., the same stage colors, the same handful of
  "interesting" sample IDs cross-referenced) — per the user's and docx's explicit "same batch of
  samples projected into different spaces, not four independent papers' figures" requirement.

### 7. Panels that cannot be supported by current data
- **Manuscript Fig.17's "raw feature space" comparison row is not supportable as specified.**
  Fig.17 in the manuscript is a 2-row PCA (raw online-relative features vs. shared hidden
  representation `h`), explicitly making the point that raw features overlap while `h` separates
  cleanly. **Confirmed by direct check this round**: `07_figure_ready/fig5/hidden_representation.csv`
  contains only the 64-D `h_00..h_63` shared representation plus stage/q/uncertainty metadata —
  no raw feature columns. `01_PHM2010/04_semantics/` (the other semantics data location) contains
  only `C6_hidden_representation.csv`, `C6_lifecycle_probability_wear.csv`, `q_statistics.csv` —
  same gap. **Decision needed from user**: (i) drop the raw-vs-hidden comparison entirely and show
  only the hidden-representation PCA (panels a/b/c as scoped above already do this — the current
  panel list assumes this resolution), or (ii) locate/derive the raw online-relative feature matrix
  for the same 304 C6 runs from elsewhere in the repo (not found in this audit pass — would need a
  separate targeted search, e.g. in `01_PHM2010/01_main_D1/` feature files or the original training
  pipeline's intermediate outputs) before committing to reproducing Fig.17's exact 2-row structure.
  This document proceeds under resolution (i) unless told otherwise.
- Optional panel (g)'s 3D surface, if included, is **not a new quantitative panel** — it re-displays
  (d)'s same probabilities via interpolation across only 304 real points; flagged so it is never
  captioned or discussed as adding new evidence beyond panel (d).

---

## 3. Open decisions — RESOLVED (user directive, this round)

1. **Fig4_3 confusion-matrix inset**: **RESOLVED = NO.** Fig4_2 already carries the representative
   confusion-matrix panel; Fig4_3 stays focused on domain-shift/generalization only. Final panel
   list for Fig4_3 (superseding §"Fig4_3_鲁棒性 / 2. Final panel list" above): (a) PHM D1/D2/D3
   task-landscape mini-panels (9 methods, Acc/M-F1/Smooth only — not the full metric roster), (b)
   Multi-task-TCN-GRU→DC-PSR paired change across PHM D1/D2/D3 + NASA + MTW-CM (ΔAcc, ΔM-F1,
   Smooth-benefit, Jump-benefit, sign convention: positive = improvement, computed as
   `(Smooth_backbone − Smooth_DCPSR)/Smooth_backbone` etc. — never silently flip a value and still
   call it "Smooth"), (c) external task-level paired profiles (NASA N1–N4, MTW-CM D1-M/D2-M/D3-M,
   Multi-task-TCN-GRU vs DC-PSR only, individual task points kept, not collapsed to one averaged
   bar), (d) optional cross-domain M-F1-vs-Smooth balance summary with backbone→DC-PSR arrows per
   dataset, raw axes only (no arbitrary composite score) — include only if it earns its space
   during panel-first review.
2. **Fig4_4 representative-config subset**: **RESOLVED = A1, A4, A5, A6** (not all 6) for the
   Band-3 / panel-(c) probability-state-formation small multiples — A1 (raw instantaneous output),
   A4 (fusion formed, pre-ordering), A5 (strongest ordered filtering, over-smoothed), A6 (final
   balanced blend). This traces the actual mechanism chain the manuscript narrates, not a device to
   show every ablation row.
3. **Fig4_5 scope**: **RESOLVED = Fig.17 (raw+shared PCA×3, first-pass all 6 sub-views) + Fig.18
   (both 3D surfaces, Python/matplotlib, not MATLAB) + q-agreement + VB physical semantics.** The
   simplex panel and any independent Fig4-4-style probability-trajectory duplication stay dropped
   (superseded by this round's explicit Layer I/II/III structure, §"Fig4_5" section 2 below,
   supersedes the previous 6(+1)-panel sketch). First pass restores the full original Fig.17 2×3
   grid; if final paper-size composition is too dense, the deletion order is fixed by user
   directive: Raw/uncertainty and Shared/uncertainty drop to supplementary **first** (moved out,
   not shrunk below the 7pt floor); Raw-vs-Shared/true-stage and Raw-vs-Shared/q are never dropped.
   Fig.18's two 3D surfaces are both kept (not reduced to one) — see the new "Fig4_5_退化语义与表示几何"
   section below for full detail.
4. **Fig4_5 raw-feature gap**: **RESOLVED.** The prior conclusion ("current frozen data only has
   hidden representation, raw-feature row unavailable") was **wrong** and is corrected by a full
   provenance trace — see `Fig4_5_退化语义与表示几何/RAW_FEATURE_PROVENANCE.md`. Summary: a
   current-protocol raw-feature matrix (`repr_raw_features.csv`, paired 1:1 with
   `repr_hidden_hct.csv`) exists under `补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/`,
   generated by `extract_hidden_representation.py` from the same frozen checkpoint as the rest of
   this project's Fig.5-lineage data. Verified byte-identical (q_true/uncertainty/entropy/
   true_stage/pred_stage/h_00/h_01/h_63, 304/304 matched rows, max abs diff = 0.0) against the
   currently frozen `paper_data/07_figure_ready/fig5/hidden_representation.csv`. Now re-frozen into
   `Fig4_5_退化语义与表示几何/derived/` (`repr_raw_features_frozen_{780,C6_304}.csv`,
   `repr_hidden_hct_frozen_{780,C6_304}.csv` + `RAW_FEATURE_FREEZE_MANIFEST.json` with row/col
   counts and SHA-256). **Fig.17's raw-vs-shared comparison is UNBLOCKED.**

## 4. Updated §7 for Fig4_5 (supersedes the old "cannot be supported" entry)

The old audit's §7 entry "Manuscript Fig.17's raw feature space comparison row is not supportable"
is **retracted**. Corrected statement: it is supportable, using the freshly-frozen
`derived/repr_raw_features_frozen_*.csv` documented in `RAW_FEATURE_PROVENANCE.md`. The only
still-open sub-decision (flagged in that document, not decided unilaterally) is whether the raw-
vs-shared PCA panels use the full 780-point set (C1+C4+C6, matching the original Fig.17's visual
density — recommended) or a 304-only `test_C6` subset (stricter scope-match with the rest of the
chapter) — default assumption going into rendering is the 780-point version, condition-encoded by
marker shape, per the recommendation in `RAW_FEATURE_PROVENANCE.md`.

## 5. Build order (starting now)

Panel-first, one figure at a time, with visual review of each panel PNG (not just "script ran")
between steps: **Fig4_2 → Fig4_3 → Fig4_4 → Fig4_5**, each figure's individual panels rendered and
inspected before assembly into the final composite, per the user's explicit process directive.
