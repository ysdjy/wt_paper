# Figure Data Audit

## Source-priority policy

The audit followed this order: FINAL/authoritative/common-universe outputs; values cited by final reports; latest formal results; historical or superseded results only when they contain the authoritative panel-specific variables and are protocol-compatible. No values were transcribed from screenshots, no seed was selected for favorable performance, and no synthetic observations were created.

## Panel-level provenance

| Figure/panel | Source file | Source columns | Filter | Transformation | n used | Normalization |
|---|---|---|---|---|---:|---|
| Fig. 1a | `final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv` | `Method`, `Acc`, `Acc_CI_low`, `Acc_CI_high` | all 9 methods; D1 common universe | none; methods ordered by point estimate | 9 method estimates, each from 304 common test runs | none |
| Fig. 1b | same as Fig. 1a | `Acc`, `Smooth` | all 9 methods | non-dominated frontier for Acc↑/Smooth↓ | 9 method estimates | none |
| Fig. 1c | same as Fig. 1a | `Acc`, `MacroF1`, `M_F1`, `Smooth`, `Rev` | Multi-task TCN-GRU and DC-PSR | paired display; each metric retains its own truthful axis | 2 methods × 5 metrics | none |
| Fig. 2a–c | `final_statistical_evidence/results/TRANSFER_TASKS_D1_D2_D3.csv` | `Method`, `Task`, `Acc`, `M_F1`, `Smooth` | all 9 methods; D1/D2/D3 | task-wise ranks and min–max scores | 27 method-task estimates per metric | Acc/M-F1: `(x-min_task)/(max_task-min_task)`; Smooth: `(max_task-x)/(max_task-min_task)` |
| Fig. 3a | `final_statistical_evidence/PROTOCOL.md`; NASA original N1–N4 split table; `experiments_mendeley/02_protocols/task_definitions.json` | dataset/task definitions | PHM2010, NASA, cross-machine milling | concise validation ladder | 3 validation levels | none |
| Fig. 3b | D1 common-universe table; `补充材料/小论文/nasa_dcpsr_results_stageaware_opt/Table_NASA_original_split_mean_std.csv`; cross-machine five-seed task summary | Acc, M-F1, Smooth, Jump for B11/backbone and B12/DC-PSR | PHM D1; NASA original N1–N4; D1-M/D2-M/D3-M | high-is-good: DC−B11; low-is-good: B11−DC; cross-machine row is the task mean | 3 dataset levels; NASA n=4 tasks; cross-machine n=3 tasks × 5 seeds | each metric column divided by its maximum absolute dataset-level effect |
| Fig. 3c | `experiments_mendeley/04_overall_comparison/summary/overall_comparison_mean_std_by_task.csv` | `Acc_mean`, `M_F1_mean`, `Smooth_mean`, `Jump_mean` | B11/B12; D1-M/D2-M/D3-M | directional deltas versus B11 | 3 tasks × 2 methods × 5 seeds | each metric column divided by its maximum absolute task-level effect; raw deltas printed in cells |
| Fig. 3d | `experiments_mendeley/07_semantic_consistency/probability_evolution/D2-M_seed42_predictions_test_B11B12.csv` | `stage_true`, `stage_pred_final_name` | D2-M, seed 42, test split | class fractions | 2,751 runs | fractions sum to 1 within true and predicted distributions |
| Fig. 4a–c | `补充材料/小论文/3_main_experiment_fgds_psi/1_results/FINAL_ablation_outputs.csv` | A1–A6; Acc, Macro-F1, M-F1, M-Rec, Smooth | `Split=test_C6` | high-is-good: Ai−A1; Smooth benefit: Smooth_A1−Smooth_Ai | 6 configurations evaluated on 304 C6 runs | heatmap colors are column-normalized by maximum absolute delta; raw deltas printed in cells |
| Fig. 5a,b,c,e | `补充材料/小论文/9_probability_wear_consistency_analysis/Data_5_4_A6_probability_wear_trajectory.csv` | run id, VB, q_true, q_pred, three probabilities, true/predicted stage | full C6 lifecycle | relative life from min–max run index; ternary barycentric transform; q statistics computed directly; wear grouped by predicted stage | 304 runs | relative-life only; probabilities and wear remain on original scales |
| Fig. 5d | `补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/repr_hidden_hct.csv` | `h_00`–`h_63`, `q_true`, `true_stage`, split, condition | `split=test_C6`, `condition=C6` | feature standardization followed by deterministic two-component SVD PCA | 304 real hidden representations | PCA only; no retraining, label fitting, UMAP, or simulated points |

## Test-universe note

D1 uses the fixed 304-run common universe for all methods. In D2/D3, the source table preserves the formal outputs: internal methods use 304 run-level predictions, while adapted external baselines use 315 native run-level predictions. The figure therefore reports within-task competitive position and does not claim a pooled absolute cross-task average.

## Excluded historical material

Superseded files, backups marked `before_smooth_fix`, screenshot-derived values, best-seed selection, and cross-task headline averages were not used. The prohibited 88.2 ± 9.7% simple average does not appear in any figure or caption.
