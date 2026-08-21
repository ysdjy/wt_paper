# Legacy Table 9 (B12) Reproduction Audit — seed=42, literal old code

Ran the **unmodified** `代码/7.4对比实验.py::main()` exactly as written — one
`base.set_seed(42)` call at the top, original B1→B2→...→B12 execution order,
no per-model RNG isolation, no diagnostic-runner changes. Only patch applied:
`base.FEATURE_FILE` pointed at `baselines/htt_net/data/run_level_features_all.csv`
(same patch pattern already used for the other 4 seeds in
`final_five_seed_sweep/`, since the script's hardcoded default path
`C:\Users\wangting\...` does not exist on this machine). `RANDOM_SEED` was
left at its script default of 42 — never overridden.

Ground truth = the archived original run at
`补充材料/小论文/4_comparison_experiment_recheck/` (files dated 2026-05-17,
predating this repo's git history — this is the actual run Table 9 was
built from). New run output: `legacy_repro_audit/output/seed42_literal_main/`.

## A. Did it exactly reproduce old B12?

**Essentially yes — 10/12 metrics bit-identical after rounding, 2 off by 0.0001.**

| metric | Table 9 target | this literal rerun | diff |
|---|---|---|---|
| Acc | 0.9868 | 0.9868 | 0 |
| Macro-F1 | 0.9871 | 0.9871 | 0 |
| E-F1 | 0.9825 | 0.9825 | 0 |
| M-F1 | 0.9844 | 0.9843 | 0.0001 |
| L-F1 | 0.9945 | 0.9945 | 0 |
| M-Pre | 0.9921 | 0.9921 | 0 |
| M-Rec | 0.9767 | 0.9767 | 0 |
| M→E | 0.0233 | 0.0233 | 0 |
| M→L | 0.0000 | 0.0000 | 0 |
| Rev | 0 | 0 | 0 |
| Jump | 0 | 0 | 0 |
| Smooth | 0.0188 | 0.0189 | 0.0001 |

## B. First actual difference point

**Not in B12 itself — in the upstream B10/B11 neural training**, which did
NOT reproduce exactly this run:

| | Table 9 / archived | this literal rerun | diff |
|---|---|---|---|
| B10 Acc | 0.8684 | 0.7599 | 10.85pp |
| B11 Acc | 0.9901 | 0.9868 | 0.33pp |
| B12 Acc | 0.9868 | 0.9868 | 0.00pp |

Preprocessing is confirmed byte-identical to the archived run (selected
45 features, MI/redundancy scores, order, and per-condition stage
thresholds all match exactly — checked against
`补充材料/.../_base_cache/1_results/selected_features.csv` and
`condition_relative_stage_thresholds.csv`). So the divergence is not a
preprocessing/data difference. It first appears inside the neural
training itself: `base.set_seed(42)` fixes `numpy`/`random`/`torch.manual_seed`,
but the old script never sets `torch.backends.cudnn.deterministic` or
`use_deterministic_algorithms` — so on GPU, cuDNN's convolution/GRU kernel
selection is not bit-reproducible even for an identical seed, identical
code, identical data, run twice (or on a different machine than the
original archived run, which predates this repo and may have run on
different hardware/driver/cuDNN version). B8→B9→B10 additionally share one
un-reset RNG stream, so B10 accumulates the most drift; B11 resets its own
seed inside `base.train_model()`, so it drifts less; B12 is pure
deterministic post-processing on top of B11's output and drifts least of
all.

## C. What Table 9's B12 actually depends on

- **Code** (both untouched since git's initial commit, verified via
  `git log`/`git diff`): `代码/7.4对比实验.py` (`main()`, B1–B12 logic,
  `B12_PARAMS`) + `代码/main_experiment_3_fgds_psi_optimized.py` (`base`:
  `load_feature_table`, `define_condition_relative_stages`,
  `split_grouped_lifecycle`, `build_online_features_by_split`,
  `select_features_train_only`, `fit_train_gmm`, `assign_fine_states`,
  `make_pack`, `train_model`, `predict_model`, `apply_probability_inference`).
- **Data**: `baselines/htt_net/data/run_level_features_all.csv` (945 rows ×
  345 cols, C1/C4/C6 315 each) — confirmed to reproduce the archived run's
  selected-feature list/scores/order and per-condition stage thresholds
  exactly.
- **RNG call order**: `main()` calls `base.set_seed(42)` **once** at the top
  (`numpy.random.seed`, `random.seed`, `torch.manual_seed`,
  `torch.cuda.manual_seed_all` — no cuDNN determinism flags). Feature
  selection (`mutual_info_classif`/`mutual_info_regression`,
  `random_state=42`) and GMM fitting (`GaussianMixture(random_state=42,
  n_init=10)`) use their own explicit `random_state`, independent of the
  global seed reset. Models train in original order B1→B2(RF regressor)→
  B3(RF)→B4(SVM)→B5(RF)→B6(XGBoost)→B7(MLP)→B8(TCN)→B9(GRU)→B10(TCN-GRU) —
  B8/B9/B10 share one un-reset RNG stream — →B11 (`base.train_model()`
  internally re-calls `base.set_seed(42)` before building the model, so
  it is the one deep model that IS seed-isolated) →B12 (pure deterministic
  inference on B11's raw output, no RNG at all).
- **Parameters**: `B12_PARAMS = {eta:0.75, fine_weight:0.30, temperature:1.20,
  mid_floor:0.12, late_tau:0.66, early_tau:0.38, order_blend:0.25}`;
  `BEST_ARCH = {L:12, dropout:0.20, lr:5e-4, channels:(32,64,64),
  gru_hidden:64}`; `EPOCHS=120, PATIENCE=18, WEIGHT_DECAY=1e-5,
  GRAD_CLIP=1.0`; multitask loss weights `LAMBDA_STAGE=1.00,
  LAMBDA_FINE=0.25, LAMBDA_Q=0.30, LAMBDA_MONO=0.03` (all read live from
  code, not retyped from memory).

**Why B12 has historically looked "stable at ~98.68%" despite B10/B11
training drift:** this run shows B12's deterministic post-processing layer
(`apply_probability_inference` — the q-based Gaussian priors, monotonic/
order-consistency filtering, mid-floor and early/late suppression) absorbed
a 10.85pp swing in B10 and a 0.33pp swing in B11 and still landed within
0.0001 of the original Table 9 B12 numbers on every metric. That is
evidence, from a single repeated-run comparison (n=2, not a systematic
claim), that B12's calibration step is what makes the reported B12 number
robust — not that B11's own training is reproducible run-to-run.
