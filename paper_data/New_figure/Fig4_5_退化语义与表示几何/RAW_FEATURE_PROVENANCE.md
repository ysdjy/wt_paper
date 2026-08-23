# Raw-Feature Provenance Trace — for Fig4-5 Layer I (原 Fig.17 raw-vs-shared comparison)

Status: **RESOLVED — Option B (existing current-protocol raw-feature matrix found, re-freezing to
`derived/`)**. The audit's earlier conclusion ("current frozen `paper_data` only has the hidden
representation, so the raw-feature row is unavailable") is **corrected** by this trace: `paper_data`
itself does not carry a raw-feature CSV, but the wider project directory does, and it is verified
below to be the exact same model/checkpoint/protocol run as the currently frozen hidden
representation — not a legacy artifact.

## Source

- **Raw feature file**: `补充材料\小论文\10_第五章顶刊风格可视化\figures_representation_space\repr_raw_features.csv`
  (780 rows × 60 cols; mtime 2026-05-23 18:41).
- **Hidden representation file** (sibling, same generation run): same folder,
  `repr_hidden_hct.csv` (780 rows × 79 cols; same mtime).
- **Generating script**: same folder, `extract_hidden_representation.py` (mtime 2026-05-23
  18:40, i.e. written immediately before the two CSVs). Docstring: *"This script reuses the
  existing main experiment pipeline and checkpoint. It does not retrain the model."*
- **Upstream pipeline module**: `import main_experiment_3_fgds_psi_optimized as base` — the same
  module that exists in this project as `代码\main_experiment_3_fgds_psi_optimized.py`
  (sha256 prefix `0696085eb69de26e`, 52874 bytes). The exact copy on `sys.path` at extraction time
  was not preserved alongside the export script, but the byte-identical cross-check below removes
  any doubt about which checkpoint/pipeline actually produced the exported values.
- **Model checkpoint referenced**: `3_main_experiment_fgds_psi\2_models\fgds_psi_best_model.pth`
  (the frozen best multi-task TCN-GRU checkpoint of the main D1 experiment — the same model whose
  predictions populate `paper_data/01_PHM2010/01_main_D1/...` and `07_figure_ready/fig5/...`).
- **Corroborating note**: the sibling `README_representation_space.md` in the same folder states
  `Proxy mode used: False` — i.e. this export used real model inference, not a placeholder/proxy
  pass. It documents this file pair as the direct source of the original manuscript's
  `Fig5_repr_main_*` figures (PCA/UMAP raw-vs-hidden), i.e. the actual Fig.17 lineage.

## Feature definition

- **What "raw feature" means here**: NOT unprocessed sensor signal. It is `xb[:, -1, :]` — the
  last time-step of the model's own input window (window length `L=12`, matching Table 6's
  "Window length" parameter) — i.e. the condition-relative *online engineered feature vector* fed
  into the TCN-GRU, taken at the current cut. This matches the manuscript's own phrase "raw online
  relative features" (not "raw sensor signal"), and is the correct object to contrast against the
  shared hidden representation `h_ct` (which is what the same window becomes *after* TCN-GRU
  encoding), since the manuscript's own scientific claim is specifically about the transformation
  from window-level relative features to the shared representation, not about raw waveform vs.
  representation.
- **Columns**: 45 numeric feature columns, all condition-relative online features, suffix
  breakdown: 39 `__rel` (condition-relative normalized value), 5 `__online_rank` (online
  percentile rank within condition), 1 `__slope` (local trend). No suffix-less / absolute-value
  columns are present — confirms these are already the condition-relative feature family the
  manuscript describes ("condition-relative degradation positions and local degradation rates"),
  consistent with `04_semantics`/`07_figure_ready` conventions used elsewhere in this project.
- **Selected-feature list source**: `3_main_experiment_fgds_psi\1_results\selected_features.csv`
  — the same feature-selection artifact used by the main frozen D1 experiment, not an ad hoc list
  built just for this export.
- **Standardization**: yes. `StandardScaler().fit(feat_train[selected])` — fit on the
  `final_train` split only, then applied (`.transform`) to `final_train`/`final_internal_val`/
  `test_C6` — standard train-fit-only convention, no test-set leakage into the scaler.
- **Missing-value handling**: `fill_by_train_median()` — missing values filled with the
  **train-split** median, applied before scaling. Confirmed: 0 NaN in any of the 45 feature
  columns across all 780 exported rows.

## Sample universe

- Total 780 rows = condition C1 (238) + C4 (238) + C6 (304) = split `final_train` (416) +
  `final_internal_val` (60) + `test_C6` (304). This is exactly the D1 protocol's dual-source
  train (C1+C4) → target-test (C6) structure described in `DCPSR_Chapter4_CN_Detailed.docx` §4.1.1.
- The `test_C6` subset (304 rows, `run_id` 12–315) is the object of interest for controlled
  comparison against the current frozen test universe.

## Alignment

- `repr_raw_features.csv` and `repr_hidden_hct.csv` are built inside the **same per-batch
  inference loop**, from the same `common` metadata dict per sample (`extract_hidden_representation.py`
  lines ~155–186) — `sample_id`, `split`, `condition`, `run_id`, `true_stage`, `pred_stage`,
  `q_true`, `q_hat`, `p_E/M/L`, `uncertainty`, `entropy`, `misclassified` are byte-identical
  between the two files, row-for-row, by construction (no separate join required; they are two
  views of the same forward pass).
- **Direct cross-check against the currently frozen `paper_data/07_figure_ready/fig5/hidden_representation.csv`**
  (304 rows, current freeze commit lineage): merged on `run_id` for the `test_C6` subset of
  `repr_hidden_hct.csv` → **304/304 rows matched, 1-to-1**. For every matched row:
  - `q_true`, `uncertainty`, `entropy`: max abs diff = **0.0** (exact match).
  - `true_stage`, `pred_stage`: **100%** exact string match.
  - `h_00`, `h_01`, `h_63` (spot-checked hidden dims): max abs diff = **0.0**.

  This is definitive: `repr_hidden_hct.csv`'s `test_C6` rows and the currently frozen
  `paper_data` hidden representation are outputs of the **identical** model checkpoint, feature
  pipeline, and 304-run test universe — not merely "close" or "similar-looking" legacy data.
  Because `repr_raw_features.csv`'s rows are generated in the exact same forward pass (same
  `sample_id`, same loop iteration) as the hidden-representation rows just verified, the raw
  features for these same 304 `test_C6` runs inherit the same provenance guarantee.

## Decision

**Option B applies**: a current-protocol-compatible raw-feature matrix already exists in the
project (outside `paper_data/`, under `补充材料/`), and is legal to re-freeze into
`paper_data/New_figure/Fig4_5_退化语义与表示几何/derived/` for use in the new Fig.4-5's
Layer I (Raw vs Shared PCA panels), **restricted to verified-current rows**.

**Scope decision on which rows to freeze** (flagged for user re-confirmation, not silently
decided): the original manuscript Fig.17 plots all 780 points (C1/C4/C6, train+val+test, condition
encoded by marker shape) to show the density of the representation-space claim. Since the
byte-identical check above was only directly performed against the `test_C6` (304-run) subset —
the only subset with a currently-frozen counterpart to check against — this document recommends:
- **Freeze the full 780-row pair** (`repr_raw_features_frozen.csv`, `repr_hidden_hct_frozen.csv`)
  into `derived/`, since all 780 rows come from the identical script execution/timestamp/checkpoint
  as the 304 verified rows (there is no plausible mechanism by which the C1/C4 rows in the same
  file, same loop, same run would come from a different checkpoint).
- For the **main-text panels' raw-vs-hidden PCA** (Fig4-5 Layer I, panels a/b/(c)), use the full
  780-point set with condition-marker encoding (o=C1, ^=C4, s=C6), matching the original Fig.17's
  visual density and the manuscript's own figure — this is a geometry/structure figure, not a
  test-set performance metric, so including train/val samples in a descriptive PCA is consistent
  with what the manuscript itself did and does not conflict with the project's "never mix test
  universes for headline metrics" rule (that rule governs classification/consistency metrics, not
  a representation-geometry background plot).
- All of Fig4-5's *other* panels (lifecycle probability, q-agreement, VB semantics) remain strictly
  scoped to the 304-run `C6`/`test_C6` universe only, as before — this is unchanged and is the
  correct scope for those quantitative panels.
- If the user prefers a stricter 304-only version of the PCA panels for internal consistency with
  the rest of the chapter, that is a one-line filter (`df[df.split == "test_C6"]`) on the frozen
  derived CSV — flagged as an easy alternative, not implemented by default.

**Not legal / out of scope**: nothing found in this trace requires blocking. No legacy/incompatible
raw-feature source was used — the found file is the current-protocol source itself.
