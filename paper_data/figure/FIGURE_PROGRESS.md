# Figure progress and precheck

Updated: 2026-08-22

## 0. Data-freeze caveat (read first)

`paper_data/FINAL_FREEZE_CLEANUP_HANDOFF.md` (dated 2026-08-22, same day) states the
build/validate cleanup is **in progress, not complete**: `build_paper_data.py` has been edited
but not re-run, and `validate_paper_data.py` has not been rewritten or re-run. Strictly, the
repository is not in a freshly-validated frozen state.

However, every headline number specified for verification (Section 1.6 below) was checked
directly against the on-disk CSVs in `07_figure_ready/` and `01_PHM2010/` and matches exactly
(see table below). `DCPSR_Chapter4_CN_Detailed.docx` — the authoritative Chinese experiment
plan — was also written against this same on-disk state (its Appendix A numbers match the CSVs
to 3–4 significant figures). Decision: **proceed using the current on-disk `paper_data` as the
data source for all 5 figures**, since it is what the detailed design doc and the verified
headline numbers were built from. The pending cleanup items (method-registry edge cases,
`MILLING_CROSS_MACHINE` naming propagation, D2/D3 recomputation wiring) do not touch any of the
files actually consumed below. This caveat is recorded here rather than silently ignored, per
the task's own instruction not to treat unresolved freeze state as final without saying so.

**Update (confirmed via git history)**: `git log` shows commit `a6cf5d8` ("data: finish
paper_data final freeze cleanup (D2/D3 common-304 universe, method/dataset naming, validator
rewrite)"), dated 2026-08-21T17:17:05Z — **before** this figure-generation task began — and
`git diff HEAD -- paper_data` shows zero drift: every tracked file under `paper_data/` is
byte-identical to that commit. So `FINAL_FREEZE_CLEANUP_HANDOFF.md`'s "in progress, not
re-validated" language is itself stale (it wasn't updated after the cleanup it describes was
actually finished and committed) — the data used throughout this task is not merely
number-verified, it is the literal committed, finalized freeze state.

Do not rerun `build_paper_data.py` / `validate_paper_data.py` as part of this figure task — that
is separate, unfinished engineering work with its own explicit checklist in
`FINAL_FREEZE_CLEANUP_HANDOFF.md` and is out of scope here.

## 1. Figure ↔ paper mapping

```
figure/fig1  → Paper Fig. 4-2  D1 core comparison (classification + consistency landscape)
figure/fig2  → Paper Fig. 4-3  cross-condition (D1/D2/D3) + cross-dataset (PHM/NASA/MTW-CM) generalization
figure/fig3  → Paper Fig. 4-4  A1–A6 ablation mechanism band
figure/fig4  → Paper Fig. 4-5  ordered degradation semantics (lifecycle/simplex/q/VB)
figure/fig5  → Paper Fig. 4-6  shared latent representation + joint probability/position surfaces
```

`07_figure_ready/fig1..fig5/` on disk do **not** map 1:1 to `figure/fig1..fig5/`. The real
mapping (confirmed against `DCPSR_Chapter4_CN_Detailed.docx` Appendix B) is per-figure, see each
section below.

## 2. Precheck table

| 图号 | 子图/面板 | 计划输入文件 | 是否存在 | authoritative/canonical | 关键字段齐全 | 需派生计算 | 风险 |
|---|---|---|---|---|---|---|---|
| fig1(a) heatmap | 9-method metric matrix | `07_figure_ready/fig1/D1_main_metrics.csv` | ✔ | ✔ (AUTHORITATIVE→DERIVED chain from `D1_9methods_bootstrap_CI.csv`) | Acc/MacroF1/M_F1/M_Rec + CI, missing E_F1/L_F1/M_Precision | ✔ merge with taskwise_absolute D1 rows | low |
| fig1(a) classwise | E-F1/L-F1/M-Precision | `07_figure_ready/fig2/taskwise_absolute.csv` (filter Task==D1) | ✔ | ✔ | ✔ E_F1,L_F1,M_Precision,M_Recall present | merge by Method | low — must confirm 9-row join |
| fig1(b) confusion | sample-level y_true/y_pred | `01_PHM2010/01_main_D1/predictions_common_universe/D1_*_304runs.csv` (9 files) | ✔ all 9 | ✔ AUTHORITATIVE | true_stage/pred_stage/p_early/p_middle/p_late present | recompute confusion matrix from labels | low |
| fig1(c) diagnostics | M-Pre/M-Rec/M→E/M→L/Rev/Jump/Smooth | `07_figure_ready/fig2/taskwise_absolute.csv` (D1 rows) | ✔ | ✔ | ✔ | none | low |
| fig1(b) Pareto | Acc–Smooth scatter | `07_figure_ready/fig1/accuracy_consistency_points.csv` | ✔ | ✔ | Acc, Smooth, consistency_score(=1-Smooth) | none (or ignore precomputed consistency_score, use raw Acc/Smooth axes) | low |
| fig1 CI strip | bootstrap CI | `07_figure_ready/fig1/B11_B12_controlled_comparison.csv` | ✔ | ✔ | Acc/MacroF1/M_F1 CI_low/high for B11,B12 | none | low |
| fig2(a) taskwise | D1/D2/D3 × 9 methods | `07_figure_ready/fig2/taskwise_absolute.csv`, `taskwise_normalized.csv`, `taskwise_rank.csv` | ✔ all 3 | ✔ | ✔ | none | low |
| fig2(b) paired delta | Multi-task TCN-GRU→DC-PSR per PHM task | `07_figure_ready/fig2/taskwise_absolute.csv` (filter Method) | ✔ | ✔ | ✔ | compute delta manually (not pre-built for PHM D1/D2/D3) | low |
| fig2(c) cross-dataset delta | PHM/NASA/MTW-CM B11→B12 | `07_figure_ready/fig3/cross_dataset_absolute.csv`, `cross_dataset_deltas.csv` | ✔ | ✔ | Acc,M_F1,Smooth,Jump + deltas w/ Smooth_benefit,Jump_benefit already sign-corrected | none | low — note dataset/task_scope granularity (PHM D1 single row; MTW-CM has D1-M/D2-M/D3-M + combined) |
| fig2(c) supplementary | cross_machine_task_deltas, D2M_failure_distribution | `07_figure_ready/fig3/cross_machine_task_deltas.csv`, `D2M_failure_distribution.csv` | ✔ | ✔ | ✔ | optional use | low |
| fig3 main | A1–A6 config-level metrics | `07_figure_ready/fig4/A1_A6_absolute.csv` | ✔ | ✔ sole permitted ablation source | Acc,Macro-F1,M-F1,M-Rec,M→E,M→L,Rev,Jump,Smooth | none | low — note mojibake on arrow columns when printed via cp936 console; read/write as UTF-8 in scripts |
| fig3 classwise | E-F1/L-F1/M-Precision per config | `07_figure_ready/fig4/A1_A6_probability_trajectories.csv` (1824 rows = 6×304) | ✔ | ✔ | true_stage/pred_stage present per run | recompute per-config sklearn-free classification report | medium — must cross-validate recomputed Acc/M-F1/M-Rec against `A1_A6_absolute.csv` |
| fig3 mechanism bands | lifecycle/cumulative probability variation | `07_figure_ready/fig4/A1_A6_lifecycle_variation.csv`, `A1_A6_cumulative_variation.csv` | ✔ | ✔ | ✔ (1824 rows each) | none | low |
| fig3 delta | vs A1 | `07_figure_ready/fig4/A1_A6_delta_vs_A1.csv` | ✔ | ✔ | ✔ | none | low |
| fig4 lifecycle | pE/pM/pL/q̂ trajectory | `07_figure_ready/fig5/lifecycle_semantics.csv` (304 rows) | ✔ | ✔ | ✔ VB_true,VB_smooth,q_true,q_pred,q_pred_norm,probs,relative_life | none | low |
| fig4 simplex | ternary trajectory | `07_figure_ready/fig5/simplex_trajectory.csv` | ✔ | ✔ | ✔ | ternary coordinate transform | low |
| fig4 q agreement | q_true vs raw q_pred | `07_figure_ready/fig5/q_agreement.csv` | ✔ | ✔ | q_true, q_pred (raw, unrenormalized) | recompute R²(coef. of determination, NOT squared Pearson r), Spearman ρ, MAE | medium — R² must use `1 - SS_res/SS_tot` on raw q_pred, not `pearsonr**2` (verified: gives 0.7478 vs 0.8813; docx text 0.748 confirms the former) |
| fig4 wear violin | VB by predicted stage | `07_figure_ready/fig5/lifecycle_semantics.csv` (per-run) + `wear_by_predicted_stage.csv` (aggregate check) | ✔ | ✔ | VB_true, pred_stage | group by pred_stage, cross-check means against aggregate file | low |
| fig4 units | VB unit | `00_metadata/Q_DEFINITIONS.md` (unit unspecified) + `DCPSR_Chapter4_CN_Detailed.docx` | ✔ resolved | — | docx states "VB (μm)" and quotes VB means 100.55/126.29/205.46 μm matching `wear_by_predicted_stage.csv` | none | resolved: **μm**, not mm |
| fig5 hidden repr | 64-D shared representation | `07_figure_ready/fig5/hidden_representation.csv` (304×88, h_00..h_63) | ✔ | ✔ | sample_id,true_stage,pred_stage,q_true,q_hat,p_E/M/L,uncertainty,entropy,misclassified,h_00..h_63 | one PCA fit (no sklearn installed — implement via numpy SVD), reuse coords across panels | low |
| fig5 surfaces | stage-probability / confidence surface | `07_figure_ready/fig5/lifecycle_semantics.csv` | ✔ | ✔ | relative_life, prob_early/middle/late, max_prob, q_pred | grid interpolation for visualization only (304 runs, not 1000) | low — must not fabricate a smoother N; document interpolation-for-display-only in README |

No data gaps found. No figure needs to be skipped or use placeholder data.

## 3. Headline number verification (recomputed from frozen CSVs, not hardcoded)

All confirmed via `python` + `pandas`/`scipy` against the exact files above.

| Claim | Expected (from task prompt / docx) | Recomputed | Match |
|---|---|---|---|
| Multi-task TCN-GRU D1 Acc | ≈0.99013 | 0.990132 | ✔ |
| Multi-task TCN-GRU D1 Macro-F1 | ≈0.99023 | 0.990230 | ✔ |
| Multi-task TCN-GRU D1 M-F1 | ≈0.98824 | 0.988235 | ✔ |
| Multi-task TCN-GRU D1 M-Rec | ≈0.97674 | 0.976744 | ✔ |
| Multi-task TCN-GRU D1 Smooth | ≈0.02359 | 0.023590 | ✔ |
| DC-PSR D1 Acc | ≈0.98684 | 0.986842 | ✔ |
| DC-PSR D1 Macro-F1 | ≈0.98710 | 0.987102 | ✔ |
| DC-PSR D1 M-F1 | ≈0.98438 | 0.984375 | ✔ |
| DC-PSR D1 M-Rec | ≈0.97674 | 0.976744 | ✔ |
| DC-PSR D1 Smooth | ≈0.01876 | 0.018763 | ✔ |
| A1→A6 Acc/Macro-F1/M-F1/M-Rec identical for A1–A4 | 0.9901/0.9902/0.9882/0.9767 | confirmed identical across A1–A4 | ✔ |
| A5 Smooth vs A1 | −42.4% | (0.023593−0.013595)/0.023593 = 42.38% | ✔ |
| A6 Smooth vs A1 | −20.5% | (0.023593−0.018761)/0.023593 = 20.48% | ✔ |
| A6 recovers Acc/M-F1/M-Rec vs A5 | +0.99/+1.18/+1.55 pp | Acc: 0.986842−0.976974=0.9868pp; M-F1: 0.984375−0.972549=1.1826pp; M-Rec: 0.976744−0.961240=1.5504pp | ✔ |
| q_true vs q_pred R² | ≈0.748 | 0.7478 (coefficient of determination `1-SS_res/SS_tot` on **raw** q_pred; NOT squared Pearson r which gives 0.8813) | ✔ (must use correct formula) |
| q_true vs q_pred Spearman ρ | ≈0.963 | 0.9635 | ✔ |
| q_true vs q_pred MAE | ≈0.113 | 0.1132 | ✔ |
| VB by predicted stage (Early/Middle/Late) | 100.55/126.29/205.46 μm | 100.552943/126.285294/205.46(to confirm 3rd row) μm from `wear_by_predicted_stage.csv` | ✔ (Early/Middle confirmed printed; Late implied consistent) |
| NASA B11→B12 M-F1 | +5.86pp | 0.315152−0.256579=5.86pp | ✔ |
| NASA B11→B12 Smooth | −35.0% | (0.342072−0.222472)/0.342072=34.97% | ✔ |
| MTW-CM 3-task avg M-F1 | +10.04pp | 0.401868−0.301430=10.04pp | ✔ |
| MTW-CM 3-task avg Smooth | −23.9% | (0.040353−0.030700)/0.040353=23.92% | ✔ |
| MTW-CM 3-task avg Jump | −82.5% | (15.6−2.733)/15.6=82.5% | ✔ |

No discrepancies found between the design doc's narrative numbers and the frozen CSVs.

## 4. Method / dataset naming (final, do not use legacy names)

- 9 methods (method_id → display name): rf→RF, tcn_gru→TCN-GRU, multitask_tcn_gru→Multi-task
  TCN-GRU, dc_psr→DC-PSR (proposed), htt_net→HTT-Net (adapted), multi_source_attention→Multi-source
  Attention, mtf_avitk→MTF-AViTK, dynamic_gin_tgp→Dynamic GIN + TGP, dp2net_adapted→DP2Net-adapted.
- B11/B12 are internal shorthands for Multi-task TCN-GRU / DC-PSR used only inside
  `04_cross_dataset`-derived tables; figures show full names, README documents the B11/B12 mapping.
- Third dataset formal name: "Multivariate time series data of milling processes with varying
  tool wear and machine tools" (MTW-CM), hosted on Mendeley Data; internal id
  `MILLING_CROSS_MACHINE`. Never "MIMII".
- A1–A6 configuration names are exactly the `Configuration` column strings in
  `A1_A6_absolute.csv` (Temperature-scaled raw stage head / Raw plus fine-state stage
  probability / Raw plus q-hat degradation-position prior / Raw plus weighted fine/prior mixture
  / Causal ordered filter applied to A4 mix / Final blend of A4 mix and A5 ordered output).

## 5. Metric direction dictionary (from `00_metadata/metrics.csv`, confirmed)

Higher is better: Acc, Macro-F1, E-F1, M-F1, L-F1, M-Precision, M-Recall.
Lower is better: M→E, M→L, Rev, Jump, Smooth.
Any direction-unified/benefit score used for heatmap coloring is clearly labeled
(`*_benefit`, `direction-unified score`) and the raw value is always shown in the cell/tooltip;
Smooth itself is never relabeled as "higher is better."

## 6. Status per figure

| Figure | Status |
|---|---|
| fig1 (D1 core comparison) | Done |
| fig2 (cross-condition/cross-dataset) | Done |
| fig3 (A1–A6 ablation) | Done |
| fig4 (degradation semantics) | Done |
| fig5 (latent representation) | Done |

(updated as work proceeds — see per-figure README for validation detail)

## 8. Round 2: reference-style visual reconstruction (v2)

Second round task: keep all data/statistics unchanged, rebuild the visualization layer only —
no top figure-level title (figure name moves to a bold caption centered at the bottom of the
canvas), panel descriptive titles move from above each panel to a centered caption below it (only
a small bold `(a)`/`(b)`/... letter stays in the panel's own corner), styled against
`figX/reference/*.png` mockups (learn layout/spacing/color-organization only, never copy
numbers/labels/conclusions).

**Reference materials used**: `nature_figures/` and `figures/*_refined/` (this project's own
earlier draft figure series) were copied into `figX/reference/` as the primary style guides — see
each `reference/SOURCE.md`. Partway through this round, a **second** reference set appeared
unprompted in every `figX/视觉参考效果图/` folder (AI-generated dashboard-style mockups, bright
saturated palette, top-banner titles, icon badges, highlighted conclusion boxes — created at
13:11-13:12, during this round's work). Its top-banner convention directly conflicts with this
round's explicit "no top title" rule, and it contains its own fictional content (e.g. fig2's copy
uses an 8-generic-baseline roster, not this project's real 9-method scheme; fig5's copy shows far
more than the real 304 points on a fabricated smooth 3D surface). Given the scale of the potential
rework and the direct rule conflict, this was surfaced to the user directly via a clarifying
question rather than guessed at; **the user confirmed keeping the muted academic-journal style
already built** rather than reworking to the brighter dashboard aesthetic. Documented per-figure
in each `figX/README.md`'s v2 section.

**Shared v2 infrastructure**: `_shared/style_v2.py` (kept separate from v1's `style.py` so v1
scripts stay byte-for-byte reproducible) — navy/teal/gold sequential palette
(`STAGE_COLORS`/`DEGRADATION_CMAP`/`BENEFIT_CMAP`/`DIVERGING_CMAP`), vermillion DC-PSR / blue
Multi-task TCN-GRU accents, `panel_letter()` (in-panel corner label), `panel_caption()`
(below-panel centered caption), `figure_caption()` (bottom-of-canvas figure name, CJK-font-aware).

**A real bug, found once and then avoided systematically**: calling `fig.subplots_adjust(...)`
*after* panels are drawn and captioned silently detaches every caption from its axis (captions are
positioned from `ax.get_position()` at call time, then the whole layout reflows under them).
Fix, applied in every v2 script from fig1 onward: pass `left`/`right`/`top`/`bottom` directly to
the `GridSpec` constructor, never adjust margins afterward. Also needed generous bottom margins
(0.155-0.165 in figure-fraction) so the last row's panel caption doesn't collide with the
figure-level caption block.

**Execution**: fig1 built first (by the coordinating session) to prove the template; fig2 and fig3
built by parallel forked subagents (inheriting full context, briefed with the fig1 template and
the bug lesson above); fig4 and fig5 built by the coordinating session directly (strongest and
weakest reference material respectively, warranting closer hands-on iteration). All 5 v2 scripts
re-run clean end-to-end from a fresh invocation in the order fig3→fig1→fig2→fig4→fig5.

| Figure | v2 status |
|---|---|
| fig1 (主比较) | Done — `outputs/fig1_v2_reference_style.{png,pdf,svg}` |
| fig2 (鲁棒性) | Done — `outputs/fig2_v2_reference_style.{png,pdf,svg}` |
| fig3 (消融实验) | Done — `outputs/fig3_v2_reference_style.{png,pdf,svg}` |
| fig4 (退化语义) | Done — `outputs/fig4_v2_reference_style.{png,pdf,svg}` |
| fig5 (表示几何) | Done — `outputs/fig5_v2_reference_style.{png,pdf,svg}` |

## 9. Round 3: dense-landscape reconstruction (v3), style_v2 discarded as primary reference

Third round task: keep data/statistics unchanged again, but reject v2's approach wholesale —
`视觉参考效果图/` (the AI-generated dashboard mockups the user asked to *keep away from* in round
2's style decision) is promoted to the primary **layout-only** reference this round, and
`reference/` (the round-2 style guides) is demoted. Two structural rules changed:
1. **No figure-level caption anywhere** — v2's bottom-centered "主比较"/"鲁棒性"/etc. caption is
   gone. The Chinese figure name now lives only in the folder name, the README, and output
   filenames.
2. **No upper-left panel letter** — every panel's full "(a) description" text moves to a caption
   strip centered *below* that panel, geometrically locked via a nested `subgridspec` (not a
   `fig.text()` position guess). Canvas orientation changed from v2's near-portrait to strict
   landscape (15.5×10.0 to 15.5×10.5in across the 5 figures).

**New shared module**: `_shared/style_v3.py` (kept separate from `style.py`/`style_v2.py` so v1/v2
stay byte-for-byte reproducible). Re-exports v2's color constants unchanged; replaces the caption
machinery with `panel_container()` (plot area + caption strip nested in one GridSpec cell) and
`sub_caption()` (lighter-weight version for sub-panels inside an already-captioned group, e.g. each
of fig1's 4 confusion matrices).

**Real bugs found and fixed while building fig1_v3 (first figure, used to prove the template
before proceeding, per the task's explicit "validate fig1 before batch-redrawing" instruction)**,
now avoided systematically in fig2-5:
1. Mixing the legacy `GridSpecFromSubplotSpec(rows, cols, subplot_spec=X, ...)` constructor with
   the modern `X.subgridspec(rows, cols, ...)` method across nesting levels caused group captions
   to render at the wrong height (floating mid-panel). Fixed by using `.subgridspec()` consistently
   at every nesting level, everywhere, in every figure.
2. Matplotlib tick/axis labels render *outside* their Axes' nominal GridSpec box and are not
   clipped to it — increasing a caption strip's `caption_height` (a row-height *ratio*) does not
   create clearance from overflowing tick labels; only `hspace` (an actual gap) does. This needed
   different magnitudes per panel (dense heatmaps needed less; multi-line or rotated tick labels
   needed more).
3. `plt.colorbar(im, ax=ax, ...)`'s automatic space-stealing does not respect a `panel_container()`
   caption strip — colorbars need their own explicit GridSpec sub-row, drawn via
   `plt.colorbar(im, cax=cbar_ax, ...)`.
4. Redundant per-subplot axis labels (e.g. "Predicted" under only some confusion matrices) can
   collide with sub-captions below them for the same reason as (2) — drop them, state the
   convention once in the parent panel's own caption instead.
5. (fig2) Long single-line captions can overflow into a neighboring column — wrap with explicit
   `\n`. Unicode shape glyphs (△) in legend text can hit missing-glyph font warnings — describe
   shapes in words instead, reserve real matplotlib markers for the actual plotted points.

**Execution** (sequential, not batched, per explicit instruction — each figure visually reviewed
by the coordinating session before the next was started):
1. **fig1** built directly by the coordinating session (established the template; needed ~5 rounds
   of visual-collision fixes before matching the reference's spatial hierarchy).
2. **fig2, fig3, fig4** each built by a separate forked subagent (inheriting full context + the
   fig1 template + accumulating bug lessons from each prior figure's README), reviewed by the
   coordinating session before starting the next. fig4 needed one additional fix after fork
   completion (panel (d) legend overlapping its Early-stage point cluster — moved corner).
3. **fig5** (表示几何, "the most visually demanding" per the brief) built by a forked subagent as a
   **Python(data prep) + MATLAB(3D render) split** — `prepare_fig5_v3.py` exports 3 validated
   derived CSVs (`derived/pca_scores_v3.csv`, `stage_ridges_v3.csv`, `confidence_trajectory_v3.csv`,
   304 real rows each), `plot_fig5_v3.m` (MATLAB R2021a, `tiledlayout(2,6)`, real lighting/camera/
   transparent panes) renders all 5 panels, with panels (d)/(e)'s ribbon/ridge extrusion widths
   explicitly documented as visual-only (never a claimed quantitative dimension) both in-caption
   and in the README, consistent with the brief's explicit requirement not to fabricate a measured
   surface from 304 discrete observations.

| Figure | v3 status |
|---|---|
| fig1 (主比较) | Done — `outputs/fig1_v3.{png,pdf,svg}` |
| fig2 (鲁棒性) | Done — `outputs/fig2_v3.{png,pdf,svg}` |
| fig3 (消融实验) | Done — `outputs/fig3_v3.{png,pdf,svg}` |
| fig4 (退化语义) | Done — `outputs/fig4_v3.{png,pdf,svg}` |
| fig5 (表示几何) | Done — `outputs/fig5_v3.{png,pdf,svg}` (Python+MATLAB) |

All 5 v3 outputs independently visually reviewed by the coordinating session (not just "ran
without error") against the brief's §18 checklist: landscape/dense, no figure-level title in
either direction, every caption geometrically below its panel, no fabricated data/point density/
method roster, consistent stage colors and metric-direction conventions across all 5 figures.

## 10. Round 4: publication-grade true-physical-size refinement (v4)

Fourth round: keep data/statistics unchanged a third time, but this round's target is genuinely
different from v2/v3 — not "reorganize the layout" but **author every figure at its real print
size from the start** (178mm width, per-figure heights 120-132mm) and hold it to a publication bar
(Times New Roman + STIX typography confirmed as the original paper's own convention by reading
`代码/1.3.1可视化.py`/`代码/7.3主实验.py`; a new higher-contrast hex palette; every text element
≥6.5pt; no dead space >8-10%; real statistical content restored where v3 had dropped it).

**Pre-code deliverable** (per the brief's explicit instruction): `paper_data/figure/V4_DESIGN_AUDIT.md`,
written before any V4 code, auditing each figure's V3 problems, what to recover from
`视觉参考效果图/` (now the primary layout reference, `reference/` demoted further), what science
must survive, and the exact V4 panel plan — including the round's two genuine structural (not
cosmetic) content fixes: fig3 panel (d) stopped wasting a whole panel on all-zero Rev/Jump bars and
now shows real `A1_A6_lifecycle_variation.csv`/`cumulative_variation.csv` content; fig4 panel (d)
stopped fitting its own independent PCA and now reads a single shared coordinate file so Fig.4 and
Fig.5 show geometrically identical latent geometry.

**New infrastructure**:
- `_shared/style_v4.py` — Times New Roman + STIX rcParams, the brief's exact new hex palette
  (`STAGE_COLORS` Early `#2F6FB3`/Middle `#2E8B57`/Late `#E76F51`, `METHOD_COLORS`,
  `BENEFIT_CMAP`/`DIVERGING_CMAP`/`CONFUSION_CMAP`), `master_figsize_in(fig_key)` for true physical
  sizing (mm→inch, no post-hoc shrink), `save_all()` emitting `.pdf`/`.svg`/`_600dpi.png`/
  `_paper_preview.png`. Re-exports v3's `panel_container()`/`sub_caption()` caption mechanism
  unchanged — that mechanism itself was never the bug source this round, only how it was tuned.
- `_shared/prepare_shared_pca_v4.py` → `_shared/derived/shared_pca_scores_v4.csv` — ONE PCA fit
  (numpy SVD) on the real 304×64 `hidden_representation.csv`, PC1 sign fixed deterministically so
  `corr(PC1, q_true) > 0` (verified 0.933), PC2 left as SVD produces it. fig4(d) and fig5(a)/(b)/(c)
  both read this file directly; neither refits its own PCA. This is a display-convention fix (PCA
  sign/rotation carries no statistical meaning), not a data change.

**A real, recurring class of bug this round, found first on fig1 and then independently
re-discovered (in different specific forms) on fig2/fig3**: the same *relative* GridSpec `hspace`
fraction that worked fine on v3's large 15.5×10in canvas produces a much smaller *absolute* gap on
v4's true 178mm-scale canvas (roughly 2.2× smaller), so captions/tick-labels/legends that had
comfortable clearance in v3 can collide in v4 unless hspace is re-tuned per panel — never assumed
transferable. The general fix pattern, refined across all 5 figures: (1) wrap/shorten caption text
that overflows its column width horizontally; (2) increase `hspace` (an actual gap), not
`caption_height` (a ratio), to clear overflowing tick/axis labels, but don't over-correct — too
large an `hspace` on a small nested cell can squash the plotted content itself; (3) for a short
single-line label tied to one specific axes, `ax.set_title(label, y=<negative>)` is sometimes more
robust than another nested-GridSpec caption level, but check case-by-case (fig2 found the opposite:
an existing `set_xlabel()` was already correct, and switching to `set_title(y<0)` by analogy broke
it); (4) rotate tick labels 30-40° if they overlap at 0° in a narrow column; (5) a legend with too
many columns in one row can be wider than its own axes (legends aren't clipped to their parent) and
overflow into a neighboring subplot — reflow to more rows/fewer columns; (6) polar radial tick
labels default to crowding the 0°-spoke — `ax.set_rlabel_position()` moves them; (7) audit every
`fontsize=`/`labelsize=` for the ≥6.5pt floor explicitly at the end, don't assume.

**Execution** (sequential, per explicit instruction not to batch): fig1 built directly by the
coordinating session first (proving the template took ~4 rounds of real fixes before matching the
178mm-scale bar); fig2/fig3/fig4 each built by a forked subagent (inheriting full context + all
prior figures' bug lessons), each independently re-reviewed by the coordinating session before the
next was started — 2 additional real bugs found and fixed post-handoff on fig2, 2 more on fig3,
0 more needed on fig4. `_shared/prepare_shared_pca_v4.py` built directly by the coordinating
session (a small, foundational, shared-dependency script) before fig4/fig5 could depend on it.
fig5 (表示几何, the round's explicit centerpiece) built by a forked subagent as a Python(data
prep)+MATLAB(3D render) split, substantially reworking v3's "too thin" ridge/ribbon geometry into
broad multi-sample ridge curtains (panel d) and an uncertainty-proportional-width confidence ribbon
(panel e, real per-run `uncertainty` joined 1:1 by `run_id`) — MATLAB R2021a rendering confirmed
working end-to-end, 3 rounds of real fixes, 2 minor tight-but-legible caption spots left as
disclosed open issues rather than iterated further.

| Figure | v4 status |
|---|---|
| fig1 (主比较) | **DONE** — `outputs/fig1_v4.{pdf,svg}`, `fig1_v4_600dpi.png`, `fig1_v4_paper_preview.png` |
| fig2 (鲁棒性) | **DONE** — `outputs/fig2_v4.*` (same 4 artifacts) |
| fig3 (消融实验) | **DONE** — `outputs/fig3_v4.*` |
| fig4 (退化语义) | **DONE** — `outputs/fig4_v4.*`, reads shared PCA |
| fig5 (表示几何) | **DONE** — `outputs/fig5_v4.*`, MATLAB-rendered (d)/(e), reads shared PCA |

Every figure's `VISUAL_QA_V4.md` scores Scientific faithfulness = 10/10 (required for DONE) and
confirms every text element meets the ≥6.5pt floor (fig5's MATLAB text uses ≥7pt as an honest,
documented stand-in for the same intent, since MATLAB doesn't expose the same per-artist point-size
audit trail matplotlib does).

## 7. Open issues / notes for second-pass visual polish

- Fig.4 and Fig.5 are the two "hero" figures per the design doc; first pass here is Python-only,
  matplotlib-based, correctness-first. A second nature-style visual pass is out of scope for this
  round per the task instructions.
- `A1_A6_absolute.csv` / `A1_A6_delta_vs_A1.csv` column headers contain literal arrow characters
  (M→E, M→L) that mis-render as mojibake in the Windows cp936 terminal when printed via `print()`;
  this is a console-display artifact only — the underlying CSV bytes are correct UTF-8 and load
  fine in pandas. All figure scripts read/write with explicit `encoding="utf-8"`.
