
# Known bad, excluded, and superseded sources

- `补充材料/小论文/3_main_experiment_fgds_psi/1_results/FINAL_ablation_outputs.csv`: internally reproducible but from an independent checkpoint; **SUPERSEDED FOR MANUSCRIPT**.
- `补充材料/小论文/6_ablation_experiment/Table10_ablation_summary.csv`: independent retraining, not frozen B11/B12; **EXCLUDED FROM MANUSCRIPT**.
- Hard-coded values in `代码/7.6.1消融实验绘图.py`, `代码/8.2图15.py`, and `代码/8.2图16.py`: not experimental data sources.
- Old `nature_figures/plot_data/fig4_D1_ablation_A1_A6.csv`: derived from the superseded Fig.4 source; not canonical.
- Paths containing reconstructed, superseded, old, backup, before_smooth_fix, debug, or diagnostic are excluded by default.
- `legacy_repro_audit/`, `protocol_diagnostic_fixed_preprocess/`, and `final_five_seed_sweep/` remain AUDIT_SUPPORTING and do not replace frozen manuscript evidence.
- `outputs/mtf_avitk/unified_protocol/` has ambiguous old D1 seed identity; D1 uses final statistical evidence only.
