from __future__ import annotations

from pathlib import Path

from common import OUT


def write_docs() -> None:
    audit = r"""# Figure Data Audit

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
| Fig. 4a–c | `paper_data/01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv`; run-level detail in `paper_data/07_figure_ready/fig4/` | A1–A6; Acc, Macro-F1, M-F1, M-Rec, Smooth | `Split=test_C6` | high-is-good: Ai−A1; Smooth benefit: Smooth_A1−Smooth_Ai | 6 configurations evaluated on 304 C6 runs | heatmap colors are column-normalized by maximum absolute delta; raw deltas printed in cells |
| Fig. 5a,b,c,e | `补充材料/小论文/9_probability_wear_consistency_analysis/Data_5_4_A6_probability_wear_trajectory.csv` | run id, VB, q_true, q_pred, three probabilities, true/predicted stage | full C6 lifecycle | relative life from min–max run index; ternary barycentric transform; q statistics computed directly; wear grouped by predicted stage | 304 runs | relative-life only; probabilities and wear remain on original scales |
| Fig. 5d | `补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/repr_hidden_hct.csv` | `h_00`–`h_63`, `q_true`, `true_stage`, split, condition | `split=test_C6`, `condition=C6` | feature standardization followed by deterministic two-component SVD PCA | 304 real hidden representations | PCA only; no retraining, label fitting, UMAP, or simulated points |

## Test-universe note

D1, D2, and D3 all use the same fixed common universe (run_id 12..315; 304 runs) for all nine methods. D1 values are the fixed official model's point estimates from the moving-block bootstrap table; D2/D3 values are recomputed by deterministically filtering each method's existing frozen predictions to run_id 12..315, with no retraining. The earlier method-native/window-based-vs-raw-signal universe distinction has been retired. The figure therefore reports within-task competitive position and does not claim a pooled absolute cross-task average.

## Excluded historical material

Superseded files, backups marked `before_smooth_fix`, screenshot-derived values, best-seed selection, and cross-task headline averages were not used. The prohibited 88.2 ± 9.7% simple average does not appear in any figure or caption.
"""

    report = r"""# Figure Report

## Workflow and export contract

- Nature Figure skill used: `nature-figure`
- Backend: Python only (`matplotlib`, `pandas`, `numpy`, `scipy`)
- Archetypes: quantitative grid (Figs. 1, 2, 4); schematic-led mixed composite (Fig. 3); asymmetric mixed-modality figure with a ternary hero panel (Fig. 5)
- Final width: approximately 183 mm (7.2 in) for a full-width two-column layout
- Export: editable SVG, Type-42-font PDF, and 600-dpi PNG
- Typography: Arial/Helvetica/DejaVu Sans fallback, 7–9 pt effective journal sizing
- Image integrity: no photographic panels, crops, local contrast changes, or synthetic observations

## Core conclusions and evidence hierarchy

### Figure 1

Core conclusion: on the D1 common universe, DC-PSR maintains near-backbone discrimination while reducing probability-sequence roughness. The forest plot is the primary statistical evidence; the Pareto map and controlled paired comparison provide trade-off and mechanism context. Comparable parameter counts were incomplete, so marker area is deliberately not used.

### Figure 2

Core conclusion: competitive position changes across unseen target conditions and must be read task by task rather than through a pooled mean. Colors encode within-task relative scores, never absolute Accuracy. All D1/D2/D3 results and unfavorable cells are retained.

### Figure 3

Core conclusion: degradation-consistent inference preserves some middle-state and smoothness benefits as domain shift increases, but absolute discrimination gains are not universal. NASA Accuracy is slightly negative relative to the backbone; D2-M and D3-M negative Accuracy deltas remain visible. Cross-dataset uncertainty structures differ (NASA original N1–N4 versus cross-machine five-seed means), so the heatmap is descriptive and controlled, not a pooled significance analysis.

### Figure 4

Core conclusion: ordered inference gives the strongest smoothing but sacrifices discrimination, whereas final fusion partially restores discrimination for a balanced configuration. A2 (Raw+Fine) and A3 (Raw+Prior) are parallel variants rather than nested sequential additions; therefore path-node effects are shown against A1, not interpreted as isolated adjacent causal increments.

### Figure 5

Core conclusion: the real C6 lifecycle outputs form an ordered trajectory in probability space and retain continuous wear semantics. The PCA panel uses existing real 64-dimensional hidden representations and deterministic SVD only; it does not retrain the network or fit a label-driven embedding.

## Unified visual system

The fixed method palette and markers requested in the task are defined once in `scripts/common.py`. DC-PSR is always vermillion (`#D55E00`) with a circle; the shared Multi-task TCN-GRU backbone is deep blue (`#0072B2`) with a diamond. Signed effects use a zero-centered muted-blue/near-white/vermillion map. Relative high-is-good scores use deep navy/teal/pale gold.

## Reproducibility

All figure-level derived tables are saved in `plot_data/`. Each figure has its own script, and the complete package is rebuilt from the project root with:

```bash
python nature_figures/scripts/make_all_figures.py
```
"""

    captions = r"""# Caption Drafts

**Figure 1 | Primary-benchmark performance and the discrimination–consistency trade-off.** a, Accuracy point estimates and 95% moving-block bootstrap confidence intervals for nine methods evaluated on the fixed 304-run D1 common test universe (C1+C4 → C6). Sequence-dependent Rev, Jump and Smooth measures are point estimates because block resampling would introduce artificial sequence boundaries. b, Accuracy–Smooth Pareto map; lower Smooth indicates a more stable probability sequence, and the dashed line connects non-dominated methods. c, Controlled comparison between DC-PSR and its shared Multi-task TCN-GRU backbone. Each small axis retains the original metric scale; arrows in labels indicate the favorable direction.

**Figure 2 | Task-wise robustness under changing unseen operating conditions.** a–c, Relative Accuracy, middle-stage F1 and probability-sequence consistency for D1 (C1+C4 → C6), D2 (C1+C6 → C4) and D3 (C4+C6 → C1). Colors represent within-task normalized relative scores rather than absolute accuracy. For high-is-better metrics, the score is `(x−min_task)/(max_task−min_task)`; for Smooth, the direction is reversed as `(max_task−x)/(max_task−min_task)`, so 1 denotes the smoothest method within that task. Cell labels give within-task ranks, and the thin vermillion outline identifies DC-PSR. Raw values are supplied in the associated plot-data table.

**Figure 3 | Progressive domain-shift evaluation and the boundary of degradation-consistent inference.** a, Validation ladder from PHM2010 cross-condition evaluation through heterogeneous NASA cross-case evaluation to cross-machine milling with machine and sensing shift. b, Dataset-level directional effects of DC-PSR relative to the shared Multi-task TCN-GRU backbone. For Accuracy and M-F1, delta values are DC-PSR minus backbone; for Smooth and Jump, positive benefit is backbone minus DC-PSR. Each metric column is divided by its maximum absolute effect for color encoding, while cell text reports the raw delta. c, The same controlled effect definitions at the D1-M, D2-M and D3-M task level; negative Accuracy effects, including D2-M, are retained. d, True and predicted stage fractions for the representative D2-M seed-42 test run, showing collapse toward the middle state under the M1+M3 → M2 machine-domain shift.

**Figure 4 | Component contributions and the discrimination–consistency balance.** a, D1 ablation effects for A1–A6 relative to the raw-stage reference A1. High-is-better metrics are expressed as `Ai−A1`, whereas Smooth benefit is `Smooth_A1−Smooth_Ai`; colors are column-normalized around zero and raw deltas are printed. b, Mechanism evidence path from raw prediction through fine-state evidence, degradation-position prior, mixture, ordered inference and final fusion. Effects are reported against A1 because the fine and prior variants are parallel ablations. c, Accuracy–Smooth trajectory showing that ordered inference provides the strongest smoothing at a discrimination cost, while final fusion yields the selected balance.

**Figure 5 | Degradation semantics of the probabilistic state representation.** a, Full 304-run C6 lifecycle trajectory of early, middle and late state probabilities, with the inferred continuous degradation position shown in the aligned lower strip. b, The same probability sequence in the Early–Middle–Late simplex; color encodes relative life, and marked endpoints denote the beginning and end of the observed sequence. c, Hexagonal density map of true and inferred degradation position with identity line and directly computed R², Spearman correlation and mean absolute error. d, PCA of the existing real 64-dimensional shared hidden representation for C6 test runs; color encodes continuous degradation position and marker shape encodes the true stage. e, Distribution of measured flank wear across predicted Early, Middle and Late states, shown as violin, box and lightly jittered run-level observations.
"""

    (OUT / "FIGURE_DATA_AUDIT.md").write_text(audit, encoding="utf-8")
    (OUT / "FIGURE_REPORT.md").write_text(report, encoding="utf-8")
    (OUT / "CAPTIONS.md").write_text(captions, encoding="utf-8")


if __name__ == "__main__":
    write_docs()
