# Fig4-5 退化语义与表示几何 (Degradation Semantics & Representation Geometry) — first-pass draft

Status: **first full assembly, visually reviewed once** — per explicit instruction, this is a
first pass; panel-by-panel refinement (including a possible MATLAB pass on panels C/D) is deferred
to a later round, not done here.

## 1. Scientific question
How does DC-PSR organize degradation information geometrically and semantically? Specifically: does
the shared representation become more ordered than the raw feature space; does the probability-state
evolution follow a structured lifecycle progression; does confidence align with degradation position
`q`; do the learned stages correspond to real physical wear (VB)?

**Honest headline (recomputed from frozen data, not asserted)**: the shared representation is
*more* ordered than the raw space, not perfectly ordered. PCA explained variance in the top 2
components: raw = 49.3%+10.2% = **59.4%**, shared = 54.8%+37.3% = **92.0%** — the shared space
compresses far more of its structure into a 2D-visualizable form. `corr(PC1, q_true)`: raw = 0.775,
shared = 0.835 — both already fairly ordered along PC1, shared modestly more so. The raw-feature
scatter (panel A) shows visible overlap between Middle and Late and a small disconnected outlier
cluster; the shared scatter (panel B) shows one continuous curved manifold with Early/Middle/Late
occupying distinct arms and uncertainty concentrated near the Early–Middle transition vertex — a
real, visible difference, not a dramatic "perfect ordering" claim.

## 2. Final panel list
- **(A) a/b/c** — Raw-feature PCA (780 samples, C1+C4+C6), colored by true stage / q_true /
  uncertainty, condition-encoded markers (o=C1, ^=C4, s=C6), misclassified samples ring-marked.
- **(B) d/e/f** — Shared hidden-representation PCA, same 780 samples, same encoding, plus a binned
  q_true lifecycle-centroid path (arrow) not present in the raw row.
- **(C)** 3D stage-probability surface (p_E/p_M/p_L) over the C6 lifecycle (304 real runs).
- **(D)** 3D confidence surface (max probability) over `q̂` (display-normalized), with the real
  max-probability ridge and `q̂` projection overlaid.
- **(e1)** q_true vs. raw q_pred agreement (scatter, y=x reference, R²/Spearman/MAE stat box).
- **(e2)** VB_true by predicted stage (violin + box + jittered points + mean marker).

## 3. Frozen data source per panel
See `inputs_manifest.csv` for the full per-panel breakdown. Core sources:
- `New_figure/Fig4_5.../derived/repr_raw_features_frozen_780.csv` / `repr_hidden_hct_frozen_780.csv`
  — the provenance-verified raw/hidden representation pair (see `RAW_FEATURE_PROVENANCE.md`), now
  PCA-projected by this figure's own `scripts/load_data.py`.
- `paper_data/07_figure_ready/fig5/lifecycle_semantics.csv`, `q_agreement.csv`,
  `wear_by_predicted_stage.csv` — unchanged from the already-validated D1/C6 304-run test universe.

## 4. Original Fig.17/Fig.18 code framework reused
- **Panels A/B**: `代码/8.2图18.py` (`Fig5_repr_main_misclassified_v2`) is the primary template —
  `pca_2d()` (mean-center + std-normalize + SVD, ported as `data_utils.pca_2d_standardized`),
  `scatter_by_condition()`, `overlay_misclassified()`, `add_lifecycle_path()`, `Q_CMAP`/`U_CMAP`
  color scales, and the 2-row/3-column layout convention are all reused directly (function logic
  ported, not the file's own stale data). `代码/8.1.2共享表征图.py`'s `add_lifecycle_path()` binning
  logic is the direct source for panel B's centroid-path arrow.
- **Panel C**: `代码/8.2图17.py::plot_stage_probability_surface` — turbo colormap, 3-ridge overlay,
  camera angle (`elev=26–28, azim≈-58`), pane/grid polish, all ported near-verbatim.
- **Panel D**: `代码/8.2图17.py::plot_confidence_surface` — the Gaussian-attenuation confidence
  envelope construction, black max-probability ridge, gray `q̂` projection, all ported near-verbatim.
- **e1/e2**: no direct `代码/8.2图*.py` ancestor scatter/violin script was used verbatim; built fresh
  in this round's own style (`_shared/style.py`), consistent with Fig4-2/4-3/4-4's shared visual
  language (stage colors, Times New Roman, arrow axes for e1/e2's 2D axes).

## 5. Python vs. MATLAB
**All panels this round are Python/matplotlib**, including C and D. The two 3D surfaces were
built by porting `代码/8.2图17.py`'s exact construction (same colormap, same ridge/envelope logic,
same camera-angle family) and judged, on visual review, to already be clean and non-jagged — not
"crude default matplotlib appearance." Per the explicit instruction ("if Python already gives a
publication-quality surface, use Python"), this round stays in Python. **A MATLAB pass on C/D
remains an open option for the panel-by-panel refinement stage** if closer review finds the Python
version insufficient — flagged here, not decided as final.

## 6. Display-only interpolation/smoothing (disclosed, per explicit requirement)
- **Panel C**: the three ridges (p_E, p_M, p_L vs. run index) are **real**, one value per real run.
  The colored surface **body** between them is a visual interpolation along the stage axis
  (E=0→M=1→L=2 via `np.interp`) — there is no fourth/fifth real stage-probability observation
  between Early/Middle/Late. This is stated in the panel's own legend ("Interpolated surface") and
  here.
- **Panel D**: the black max-probability ridge and the gray `q̂` projection are **real** per-run
  values. The colored **envelope** around them is a synthetic Gaussian-attenuation band (width
  ±0.075 in `q̂`-space) added purely for visual body, ported unchanged from `代码/8.2图17.py`'s own
  construction — it is not a second measured dimension, and the legend labels it "Confidence
  envelope" (not "measured field").
- **Panel D's y-axis** (`q̂`) uses `q_pred_norm` — `Q_DEFINITIONS.md`'s display-only min-max
  normalization of `q_pred` — for the 3D axis **position only**. Agreement statistics (panel e1)
  always use raw `q_pred`, never this normalized field, per the frozen protocol.
- **Panel B's lifecycle path** is a 12-bin centroid line through `q_true`-binned PCA coordinates,
  a display aid (matches `代码/8.2图18.py`'s own `add_lifecycle_path`), not a new data point.

## 7. Validation notes
`logs/validation.txt`:
- q-agreement R²=0.7478 (expected 0.748), Spearman ρ=0.9635 (expected 0.963), MAE=0.1132 (expected
  0.113) — all PASS, using the coefficient-of-determination formula (not squared Pearson r).
- VB_mean by predicted stage: Early=100.55, Middle=126.29, Late=205.46 μm — all PASS against the
  docx's stated values.
- Raw/hidden PCA: PC1 sign convention (`corr(PC1, q_true) > 0`) enforced and logged for both.
- `raw["sample_id"] == hidden["sample_id"]` row-alignment asserted before PCA (both provenance-
  verified files are outputs of the same forward pass, so this must hold exactly).

## 7a. Refinement round (CIE-submission pass, highest priority per the brief)
Formalized the previously-implicit A/B/C/D structure into 4 actual bordered blocks (Raw-feature
geometry; Shared latent geometry; Probability-state geometry [C+D together]; Semantic anchors) +
one outer canvas border, via `_shared/style.py`'s new border helpers — matching the "接近实验设置图
模块清晰" target. Canvas height **255mm→240mm**. Concrete changes: the semantic block (e1/e2) was
enlarged (its own row height_ratio increased relative to the other three blocks, addressing the
prior round's own open item that it was "the smallest block despite being the figure's semantic-
closure role"); the 3D panels' (C)/(D) caption gap — flagged as an open item in the first-pass
README — is now visibly tighter, computed from the same real-axes-position pattern used elsewhere,
though 3D axes' inherent bbox padding (mplot3d reserves internal space for perspective/labels that
2D axes don't) means it can never be as tight as a 2D panel's caption; documented, not fully
eliminated. One collision found and fixed by opening the PNG: blocks 1/2's corner labels initially
touched the top y-axis tick numbers ("10", "7.5") of their first panel — fixed with more headroom
above the axes top. Added fixed-name export (`fig4_5_degradation_representation.pdf`/`_600dpi.png`,
note the different basename vs. the working `Fig4_5_semantics_geometry` files — required by the
submission naming convention) to `New_figure/final_pdf/`.

## 8. Output paths
`outputs/Fig4_5_semantics_geometry.{pdf,svg}`, `_600dpi.png`, `_preview.png`. Individual panel
previews: `outputs/panel_a_preview.png` (block A, 3 sub-panels), `panel_b_preview.png` (block B),
`panel_c_preview.png`, `panel_d_preview.png` (3D, Python), `panel_e1_preview.png`,
`panel_e2_preview.png`.

## 9. Unresolved / open items for the next refinement round (not fixed in this first pass)
- Panels C/D have a visibly large blank gap between the plotted 3D content and their captions —
  3D axes' `get_position()` bounding box includes generous internal padding for perspective/labels
  that 2D axes don't have, so the same "caption below the axes" convention leaves more visual
  whitespace here than in the 2D panels. Not a collision, just not perfectly tight; a candidate fix
  next round (e.g. a manually-tuned fixed offset instead of `get_position()`-derived one for 3D
  panels specifically).
- Panel D's view angle/label placement is not perfectly symmetric with panel C's (different azimuth
  needed for readability given the different y-axis meaning) — acceptable for a first pass, could
  be tuned further.
- MATLAB re-render of C/D not attempted this round (see §5) — open for next round if requested.
- No second-reviewer pass or ≥6.5pt-at-print-size micro-audit yet (first-pass status only).

## 10. What was explicitly NOT done this round (per instruction)
- Fig4-2/4-3/4-4 were not touched.
- The chapter plan was not redesigned.
- No search for alternate/unfrozen data sources — the already-resolved raw-feature provenance
  (`RAW_FEATURE_PROVENANCE.md`) was reused as-is, per instruction not to re-search unless a field is
  genuinely missing (none was).
