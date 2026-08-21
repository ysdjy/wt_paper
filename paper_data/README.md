
# Paper data — Single Source of Truth

This directory is the only permitted data entrypoint for manuscript numbers, tables, and figures. It was built by copying audited sources and regenerating every derived table without training, seed selection, or manual transcription from images.

## Absolute canonical data

- PHM2010 D1 9-method table: `01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv`
- PHM2010 D1/D2/D3: `01_PHM2010/02_cross_condition_D1_D2_D3/transfer_tasks_long.csv`
- PHM2010 A1-A6: `01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv` (the only permitted ablation source)
- PHM2010 Fig.5 semantics: `01_PHM2010/04_semantics/C6_lifecycle_probability_wear.csv` and `C6_hidden_representation.csv`
- NASA original N1-N4: `02_NASA/original_split_mean_std.csv` plus task/prediction evidence
- MTW-CM (Multivariate time series data of milling processes with varying tool wear and machine tools; hosted on Mendeley Data): `03_MENDELEY_CROSS_MACHINE/overall_by_task_mean_std.csv` plus seed/prediction/semantic evidence. The folder name `03_MENDELEY_CROSS_MACHINE` is a retained path only, not the formal dataset name.

## Derived data

`04_cross_dataset`, `07_figure_ready`, and `08_table_ready` are derived. Delta, rank, min-max, normalized, and relative scores never replace absolute values. Formulas are in `90_provenance/TRANSFORMATIONS.md`.

## Never use as manuscript canonical data

The old `FINAL_ablation_outputs.csv`, `Table10_ablation_summary.csv`, hard-coded plotting values, reconstructed/superseded features, diagnostics, and ambiguous old MTF-AViTK D1 runs are excluded. See `90_provenance/KNOWN_BAD_AND_SUPERSEDED.md`.

## Rebuild and validate

```powershell
python paper_data/99_scripts/build_paper_data.py
python paper_data/99_scripts/validate_paper_data.py
```

Repository anchor: branch `diagnostic/fixed-preprocess-5seed`, commit `7b9fa2b`. The task-start state is frozen in `90_provenance/REPOSITORY_STATE.md`.
