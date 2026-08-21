
# PHM2010 D1 training-seed sensitivity — audit supporting only

The manuscript main comparison remains the fixed official model evaluated on the 304-run common universe, with moving-block bootstrap 95% confidence intervals. Nothing in this directory may be merged into, averaged with, or substituted for `01_main_D1/D1_9methods_bootstrap_CI.csv`.

- `original_5seed_*` preserves the original five-seed sweep, including its documented preprocessing/training-seed coupling.
- `fixed_preprocessing_*` varies only `TRAIN_SEED` while holding preprocessing at seed 42.
- `old_vs_fixed_preprocessing.csv` is a protocol diagnostic, not a main-table estimate.

All files in this directory have catalog status `AUDIT_SUPPORTING`.
