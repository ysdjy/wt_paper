# Fig.4 V2 lifecycle-trajectory data audit

## Audit conclusion

**PASS_INFERENCE_ONLY** — the experiment protocol was not changed and no model was retrained. The work only exports missing probability trajectories from the frozen formal model and enhances visualization of already authoritative results.

Explicit statement: **未重训，仅做权威结果可视化增强。**

## Fixed protocol

- Dataset: PHM2010.
- Task: D1, train = C1+C4 and test = C6.
- Window length: L=12.
- Evaluated C6 universe: run 12–315, 304 windows.
- A1–A6 definitions and probability parameters: unchanged from the audited formal code path.
- Seed, split, stage definition, selected features, scaler and GMM: unchanged.
- New training, hyperparameter search or target-domain tuning: none.

## Existing authoritative data reused

### Summary table

- `AUTHORITATIVE_A1_A6.csv`
- Role: the only authoritative A1–A6 summary used by panels (a) and (c), and the validation target for all trajectory exports.
- Audit status inherited from the provenance audit: `PASS_WITH_CORRECTION`.

### Frozen inference inputs

- Formal checkpoint: `补充材料/小论文/4_comparison_experiment_recheck/3_models/B11_B12_multitask_tcn_gru.pth`.
- Checkpoint SHA-256: `17299bbc71baa8148a0c3916084b034ec0efe4120a36b06f2b2cb8a6919ec69b`.
- Frozen preprocessing directory: `protocol_diagnostic_fixed_preprocess/frozen_preprocess/`.
- Selected-feature list: `selected_features_seed42.json` (45 features).
- Scaled formal C6 table: `feat_test_frozen.csv`.
- Formal four-decimal probability anchor: `补充材料/小论文/4_comparison_experiment_recheck/1_results/FINAL_comparison_predictions.csv`.

The frozen preprocessing tables were loaded directly. Feature selection, scaler and GMM were **not refitted** for this figure.

## Existing trajectory candidates and decision

| Candidate | Contents | Decision |
|---|---|---|
| Formal comparison predictions | A1/B11 and A6/B12 run-wise probabilities, rounded to four decimals | Reused as formal label/probability anchor; incomplete for A2–A5 |
| Old main full internal predictions | Full A1–A6 probabilities and q_hat | Rejected: different checkpoint from formal B11/B12 |
| Independent 7.6 ablation probabilities | Full A1–A6-like probability components | Rejected: independently retrained checkpoint |
| New V2 inference-only export | Full A1–A6 probabilities and q_hat from formal checkpoint | **Selected** |

Therefore, the complete formal A1–A6 trajectory table did not previously exist and was supplemented by pure inference.

## Inference-only export

Script: `export_fig4_v2_trajectories.py`.

Execution path:

```text
frozen scaled C6 features + fixed L=12 windows
  -> formal B11/B12 checkpoint
  -> model.eval() + torch.inference_mode()
  -> raw stage / fine-state / q_hat heads
  -> audited apply_probability_inference(A1–A6)
  -> trajectory and variation CSVs
```

The exporter does not call `train_model`, create an optimizer, update weights, fit preprocessing, or search parameters.

Validation results:

- A1 labels = stored formal B11 labels: exact.
- A6 labels = stored formal B12 labels: exact.
- Maximum A1 probability difference from the stored four-decimal anchor: `4.3182×10⁻⁴`.
- Maximum A6 probability difference from the stored four-decimal anchor: `2.2920×10⁻⁴`.
- Maximum difference between recomputed A1–A6 summary metrics and `AUTHORITATIVE_A1_A6.csv`: `1.11×10⁻¹⁶`.
- All six local-variation means reproduce authoritative Smooth values.
- All six cumulative endpoints divided by 303 reproduce authoritative Smooth values.

## New trajectory data

### `A1_A6_probability_trajectories.csv`

- 1,824 rows = 6 configurations × 304 C6 windows.
- Fields include `ID`, `run_id`, `relative_tool_life`, true/predicted stage, `q_true`, `q_hat`, `p_E`, `p_M`, and `p_L`.
- Relative tool life is normalized over the evaluated L=12 universe:

```text
relative_tool_life = (run_id - 12) / (315 - 12)
```

### `A1_A6_lifecycle_variation.csv`

For configuration A and lifecycle point t:

```text
local_variation_l1(t) = |p_E(t)-p_E(t-1)|
                      + |p_M(t)-p_M(t-1)|
                      + |p_L(t)-p_L(t-1)|
```

Panel (b) shows both:

- the raw local variation as thin low-opacity lines;
- a centered 11-run rolling arithmetic mean as the darker display line.

The first point has no predecessor and is stored as missing for raw local variation. Smoothing is display-only; raw values are retained, and no smoothed value is used to recompute any official metric.

### `A1_A6_cumulative_variation.csv`

```text
cumulative_variation_l1(t) = sum(local_variation_l1(k), k=2...t)
```

Panel (d) uses the raw, unsmoothed cumulative sum. For 304 windows:

```text
cumulative endpoint / 303 = authoritative Smooth
```

## Panel-to-data mapping

| Panel | Data source | Metrics / transformation |
|---|---|---|
| (a) Overall predictive performance | `AUTHORITATIVE_A1_A6.csv` | Acc, Macro-F1, M-F1, Smooth |
| (b) Lifecycle-wise probability variation | `A1_A6_lifecycle_variation.csv` | raw adjacent L1 variation + centered 11-run display mean |
| (c) Middle-stage and transition consistency | `AUTHORITATIVE_A1_A6.csv`; audited completion of M-Precision from `ABLATION_RECOMPUTED.csv` | M-Pre, M-Rec, M→E, M→L |
| (d) Cumulative trajectory variation | `A1_A6_cumulative_variation.csv` | raw cumulative adjacent L1 variation |

## Runtime and outputs

- Inference runtime: Python 3.11.15, PyTorch 2.7.1+cu118, NVIDIA GeForce RTX 3070 Ti Laptop GPU.
- Model state: `eval`.
- Autograd state: `torch.inference_mode()`.
- Figure backend: Python / matplotlib only.
- Final outputs: `fig4_ablation_v2.pdf`, `fig4_ablation_v2.png`, `fig4_ablation_v2.svg`.
