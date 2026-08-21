# Final pre-figure data freeze cleanup — progress and handoff

Updated: 2026-08-22 (Asia/Shanghai)

## Current state: work in progress, not frozen

The cleanup has **not** reached the build/validation stage. The existing generated files under `paper_data/` still represent the previous freeze (`PASS_WITH_WARNINGS` at that time). Only `paper_data/99_scripts/build_paper_data.py` has been edited so far for this cleanup. Do not interpret the current generated CSV/JSON/MD files as the new final state until both commands below have completed successfully:

```powershell
python paper_data/99_scripts/build_paper_data.py
python paper_data/99_scripts/validate_paper_data.py
```

No model has been trained or retrained during this cleanup.

## Completed in the build script

The following changes are present in `paper_data/99_scripts/build_paper_data.py` and the file passes Python AST syntax parsing:

1. **Unique method registry drafted**
   - Added one canonical row per method in `METHOD_METADATA`.
   - Added `dp2net_adapted` explicitly.
   - Canonical names and aliases are separated, so `HTT-Net`/`HTT-Net (adapted)` and the two multi-source labels will no longer create duplicate `method_id` rows in `methods.csv`.

2. **Third-dataset naming constants drafted**
   - Internal ID: `MILLING_CROSS_MACHINE`.
   - Formal name: `Multivariate time series data of milling processes with varying tool wear and machine tools`.
   - Short name: `MTW-CM`.
   - Hosting platform: `Mendeley Data`.
   - The existing folder `03_MENDELEY_CROSS_MACHINE/` is intentionally retained for path stability; it must not be treated as the formal dataset name.

3. **D2/D3 common-universe recomputation implemented in principle**
   - Added a deterministic metric recomputation function using existing `true_stage`, `pred_stage`, and probability columns.
   - `copy_phm()` now filters every D2/D3 prediction file to `run_id=12..315` and requires exactly 304 unique ordered runs.
   - The four raw-signal methods (`multi_source_attention`, `mtf_avitk`, `dynamic_gin_tgp`, `dp2net_adapted`) are reduced from 315 to the shared 304-run universe.
   - The other five methods are rechecked through the same filter and should remain at 304 rows.
   - D2/D3 metrics JSON, the 27-row D1/D2/D3 table, and the across-task mean/std table are intended to be regenerated from those frozen predictions only.
   - D1 remains sourced from the fixed official D1 bootstrap table; no training-seed result is substituted into the main comparison.

4. **Training-seed sensitivity archive function added**
   - Added `copy_phm_training_seed_sensitivity()` to copy the original five-seed sweep and the fixed-preprocessing diagnostic into `01_PHM2010/05_training_seed_sensitivity/`.
   - All of these files are designed to be cataloged as `AUDIT_SUPPORTING` and explicitly barred from replacing the fixed official D1 main table.
   - Important: this function is defined but is **not yet called from `main()`**.

5. **Figure-ready metadata helper added and partially applied**
   - Required fields are: `dataset_id`, `task_id`, `protocol_id`, `aggregation_level`, `uncertainty_type`, `n_test`, `test_universe`, `source_path`, and `status`.
   - The helper has been wired into the current Fig.1, Fig.2, Fig.3, Fig.4, and Fig.5 generation sections.
   - This has not yet been exercised by a build, so schemas and downstream compatibility still require testing.

6. **Fig.4 run-level data integration drafted**
   - The builder is prepared to ingest the audited files currently located at:
     - `figures/fig4_ablation/A1_A6_probability_trajectories.csv`
     - `figures/fig4_ablation/A1_A6_lifecycle_variation.csv`
     - `figures/fig4_ablation/A1_A6_cumulative_variation.csv`
   - Intended destination: `paper_data/07_figure_ready/fig4/`, with 6 configurations × 304 runs = 1,824 rows per file.

7. **Frozen q-definition document drafted in the builder**
   - Intended output: `paper_data/00_metadata/Q_DEFINITIONS.md`.
   - It distinguishes `VB_true`, centered 7-run `VB_smooth`, condition-relative `q_true`, raw model-head `q_pred`, display-only `q_pred_norm`, and `(run_id-12)/303` relative life.
   - Fig.5 agreement data are intended to use `q_true` versus raw `q_pred`; normalized prediction is separated into a display-only audit file.

8. **Controlled canonical-source update support added**
   - `safe_copy(..., allow_source_update=True)` was added for an explicitly audited source change.
   - It is currently used only for the Fig.4 `data_manifest.json`; strict hash protection remains the default elsewhere.

## Work still required before running the build

1. **Finish and review `build_paper_data.py`**
   - Call `copy_phm_training_seed_sensitivity()` from `main()`.
   - Finish replacing internal `MENDELEY_CROSS_MACHINE` dataset values with `MILLING_CROSS_MACHINE` while retaining legacy folder paths.
   - Update generated README/source-priority/transformation/manuscript-map text to use the formal dataset name and identify Mendeley Data only as the host.
   - Replace the old D2/D3 “method-native universe” README text with the common 304-run protocol.
   - Move manuscript-only stale items into a separate `MANUSCRIPT_SYNC_STATUS=PENDING` artifact instead of reporting them as unresolved data-integrity failures.
   - Remove `FIG4-001` only after every formal script has actually been switched.
   - Review source inventory exclusions now that both seed-sensitivity suites are being copied as `AUDIT_SUPPORTING`.
   - Make `VALIDATION_REPORT.md` a post-validation runtime artifact (or otherwise exclude it from self-invalidating checksum comparisons), so repeated validation is stable.

2. **Update all formal Fig.4 scripts**
   - `nature_figures/scripts/fig4_ablation.py` still reads the retired `FINAL_ablation_outputs.csv`.
   - `nature_figures/scripts/generate_docs.py` still documents that retired source and still says D2/D3 use different native universes.
   - The new/refined scripts under `figures/fig4_ablation/` currently read files beside the script; formal plotting paths should be changed to `paper_data/01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv` and the run-level files under `paper_data/07_figure_ready/fig4/`.
   - Do not overwrite their layout/rendering changes; only change data-path/provenance logic.

3. **Rewrite and strengthen `validate_paper_data.py`**
   - Check exactly 9 unique method IDs and explicit presence of `dp2net_adapted`.
   - Check third-dataset ID/formal name/short name/hosting platform separation.
   - Check D1 remains fixed official + moving-block bootstrap 95% CI.
   - Check every D2/D3 method has exactly `run_id=12..315`, 304 rows, and recomputed metrics equal the frozen tables.
   - Check Fig.2 is rebuilt from the common-304 table.
   - Check every summary-like `07_figure_ready` CSV has the required metadata fields and non-empty values.
   - Check Fig.4 has 1,824 audited rows in each run-level file and no formal script contains `FINAL_ablation_outputs.csv`.
   - Check the q-definition document exists and `q_agreement.csv` excludes `q_pred_norm` from reported agreement statistics.
   - Check both seed-sensitivity suites are `AUDIT_SUPPORTING` and are absent from main comparison/figure tables.
   - Report manuscript synchronization separately as pending rather than changing numerical integrity status.

4. **Run compact pre-build tests**
   - Recompute D2/D3 metrics once in a non-writing check and compare unchanged 304-run methods against their old metrics.
   - Record old-versus-new values for the four filtered raw-signal methods; these are the key changes required in the final report.
   - Confirm all source prediction files have one row per `run_id` and identical true labels on the shared universe.

5. **Run build, then validation**
   - Use the bundled Python runtime if dependency consistency is needed.
   - A build failure must be fixed at its source; do not edit generated status fields merely to obtain PASS.
   - Run validation at least twice if checksum/report-cycle logic was changed, confirming the second run is stable.

6. **Final audit and report**
   - Inspect `git diff` only for files in scope.
   - Summarize modified files, D2/D3 metric deltas after filtering, remaining genuine unresolved items, manuscript sync status, and final validation status.

## Known risks in the current intermediate script

- Only AST syntax has been checked; the builder has not executed, so missing field names or downstream schema assumptions may still fail at runtime.
- The new dataset-table row has extra columns compared with the first two rows; normalize the row schema before writing CSV, otherwise `extrasaction="ignore"` may silently omit those fields.
- Existing `paper_data/90_provenance/COPY_MANIFEST.csv` protects prior canonical hashes. Any additional deliberately updated copied source needs a narrowly scoped `allow_source_update=True`; do not disable protection globally.
- `VALIDATION_REPORT.md` currently participates in generated integrity metadata and may create a build/validate checksum cycle after validator changes.
- Figure-ready metadata were added broadly. Formal plotting scripts should tolerate extra columns, but this must be tested.

## Worktree boundary: preserve unrelated changes

The repository already contained substantial modified/deleted/untracked figure work before this cleanup. In particular, Fig.4/5 render files, refined plotting scripts, MATLAB exports, and a DOCX are dirty. They are not all owned by this cleanup. Do not reset, delete, or bulk-stage the worktree.

For this cleanup, the only file modified so far is:

- `paper_data/99_scripts/build_paper_data.py`

The new handoff document is:

- `paper_data/FINAL_FREEZE_CLEANUP_HANDOFF.md`

## Recommended continuation order

1. Read this file and inspect the diff of `paper_data/99_scripts/build_paper_data.py`.
2. Finish builder text/status/main-call work.
3. Patch formal Fig.4 paths with minimal diffs.
4. Rewrite validator checks.
5. Run non-writing metric comparison.
6. Run build.
7. Run validation twice and inspect the report.
8. Only then declare the data frozen.
